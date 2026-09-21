"""The note-size gate: one cap table, applied to staged notes by a pre-commit hook.

The hook is a ratchet: it refuses a commit only where a note is over its
cap *and* grew relative to HEAD (or is new) — a guard bites growth, not existence, so the
legacy backlog of already-over-cap notes stays editable. `tracked_breaches` feeds the
hygiene note-caps row instead, which reports that backlog without blocking anything.

A note's size is its BODY only: front matter (every property, including a tool-written
`status:`) is derived metadata, not authored content, and is excluded from the cap in both
places above, so the enforced and reported sizes always agree.
"""

from __future__ import annotations

import re
import shlex
import sys
from collections.abc import Iterable, Mapping
from pathlib import Path

from .board import Config, Repo, VaultError

# Deliberately not `board.FRONTMATTER_RE`: that regex's capture group is load-bearing for
# `sync.with_status`, which reconstructs a note from `match.start(1)`/`match.end(1)` and gains a
# spurious blank line (and a fence jammed against the last value with no newline) if the capture
# boundary moves. Its `(.*?)\r?\n---\r?\n` shape is also wrong for two boundary cases this gate
# must get right: an EMPTY front-matter block (adjacent `---`/`---` lines have no `\n---\n` for a
# zero-length capture to land on, so it backtracks past the whole block to the next `---` anywhere
# in the file -- a cap bypass) and a closing `---` at end-of-file with no trailing newline (the
# trailing `\r?\n` it requires never matches, so the block goes undetected). Detection here instead
# finds the closing fence directly: the first line that is exactly `---` after the opening line.
_FRONT_MATTER_OPEN = re.compile(r"\A---\r?\n")
_FRONT_MATTER_CLOSE = re.compile(r"^---\r?$", re.MULTILINE)


def _body_size(text: str) -> int:
    """Character count of `text` after its leading front-matter block, if any.

    A note with no front-matter block, or an unterminated one (no closing `---` line found), is
    measured whole.
    """
    open_match = _FRONT_MATTER_OPEN.match(text)
    if open_match is None:
        return len(text)
    close_match = _FRONT_MATTER_CLOSE.search(text, open_match.end())
    if close_match is None:
        return len(text)
    end = close_match.end()
    if end < len(text) and text[end] == "\n":
        end += 1
    return len(text) - end


HOOK_BODY = """#!/bin/sh
# vaulttools note-size gate -- `vault hook check`
exec env PYTHONPATH={package} {python} -m vaulttools.cli hook check
"""


def cap_for(relative: str, caps: Mapping[str, int]) -> int | None:
    """The character cap for a vault-relative Markdown path; `None` where the folder is uncapped."""
    if not relative.lower().endswith(".md"):
        return None
    if "/" not in relative:
        return caps.get("root")
    prefixes = [prefix for prefix in caps if prefix.endswith("/") and relative.startswith(prefix)]
    return caps[max(prefixes, key=len)] if prefixes else None


def _breach(relative: str, size: int, cap: int, old: int | None = None) -> str:
    detail = f" (grew from {old})" if old is not None else ""
    return f"{relative}: {size} chars over the {cap} cap{detail}"


def _head_size(repo: Repo, relative: str) -> int:
    """Body size of `relative` at HEAD; 0 when the path is new (absent from HEAD)."""
    result = repo.git("show", f"HEAD:{relative}", check=False)
    return _body_size(result.stdout) if result.returncode == 0 else 0


def staged_breaches(repo: Repo, config: Config) -> tuple[str, ...]:
    """Staged notes over their cap that also grew relative to HEAD — the ratchet.

    An over-cap note that is equal to or smaller than its HEAD size is allowed through: the
    cap only bites the growth of an over-cap note, never its mere pre-existing size. A note
    absent from HEAD (new) counts as size 0, so any new over-cap note refuses. Deletions
    never reach here — `--diff-filter=ACM` excludes them, so removing an over-cap note
    always commits.
    """
    names = repo.git("diff", "--cached", "--name-only", "-z", "--diff-filter=ACM").stdout.split("\0")
    breaches: list[str] = []
    for name in filter(None, names):
        cap = cap_for(name, config.caps)
        if cap is None:
            continue
        size = _body_size(repo.git("show", f":{name}").stdout)
        if size <= cap:
            continue
        old = _head_size(repo, name)
        if size <= old:
            continue
        breaches.append(_breach(name, size, cap, old))
    return tuple(breaches)


def tracked_breaches(vault: Path, config: Config, notes: Iterable[Path]) -> tuple[str, ...]:
    """Notes on disk whose BODY is larger than the cap of the folder holding them."""
    breaches: list[str] = []
    for note in notes:
        relative = note.relative_to(vault).as_posix()
        cap = cap_for(relative, config.caps)
        if cap is None or not note.is_file():
            continue
        size = _body_size(note.read_text(encoding="utf-8"))
        if size > cap:
            breaches.append(_breach(relative, size, cap))
    return tuple(breaches)


def hook_body(package: Path, python: str) -> str:
    """The pre-commit script, with both paths shell-quoted so a spaced path stays one word."""
    return HOOK_BODY.format(package=shlex.quote(str(package)), python=shlex.quote(python))


def _hooks_dir(vault: Path) -> Path:
    """The hooks directory git itself would run, shared by a linked worktree with its clone."""
    relative = Repo(vault).git("rev-parse", "--git-path", "hooks").stdout.strip()
    if not relative:
        raise VaultError(f"{vault} has no git directory to install a hook into")
    return (vault / relative).resolve()


def install(vault: Path, force: bool = False) -> Path:
    """Write the `pre-commit` hook so every commit runs `vault hook check`."""
    hooks = _hooks_dir(vault)
    hooks.mkdir(parents=True, exist_ok=True)
    hook = hooks / "pre-commit"
    if hook.exists() and not force:
        raise VaultError(f"{hook} already exists — pass --force to replace it")
    hook.write_text(hook_body(Path(__file__).resolve().parent.parent, sys.executable), encoding="utf-8")
    hook.chmod(0o755)
    return hook
