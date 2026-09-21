"""Vault root, configuration, note front matter, Kanban parsing, and the git transaction.

Every other module reads and writes the vault through this one: the card mover, the
stream sweep and the hygiene check share this board parser and this transaction.
"""

from __future__ import annotations

import os
import re
import signal
import subprocess
import tomllib
from collections.abc import Callable, Mapping, Sequence
from contextlib import suppress
from dataclasses import dataclass, field
from pathlib import Path

CONFIG_NAME = "vault.toml"
CARD_RE = re.compile(r"^- \[[ xX]\] \[\[([^\]|]+?)(?:\|[^\]]*)?\]\]")
HEADING_RE = re.compile(r"^##\s+(.+?)\s*$")
FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)
FIELD_RE = re.compile(r"([A-Za-z_][\w-]*):\s*(.*)$")
ITEM_RE = re.compile(r"\s*-\s+(.*)$")
DEFAULT_CAPS = {"root": 15000, "tasks/": 10000, "08 Tasks/": 10000, "doctrine/": 15000}
PIN_RE = re.compile(r"[0-9a-fA-F]{40}\Z")


class VaultError(RuntimeError):
    """An operation cannot proceed without losing or corrupting vault state."""


@dataclass(frozen=True)
class Scope:
    """One configured Git checkout and the branch or immutable commit it follows."""

    name: str
    path: str
    branch: str | None = None
    pin: str | None = None


@dataclass(frozen=True)
class Config:
    """Vault layout and bounds. `vault.toml` at the vault root overrides any field."""

    board: str = "kanban.md"
    tasks: tuple[str, ...] = ("tasks", "08 Tasks")
    temp: str = "temp"
    repos: str = "repos"
    columns: tuple[str, ...] = ("backlog", "open", "in progress", "promotion")
    promotion_bound: int = 5
    promotion_days: int = 7
    backlog_days: int = 90
    # A landing merges a stream and deletes its branch in one step; the worktree it merges
    # from carries this prefix and legitimately outlives the stream card it is retiring.
    merge_branch_prefix: str = "merge-"
    caps: dict[str, int] = field(default_factory=lambda: dict(DEFAULT_CAPS))
    scopes: tuple[Scope, ...] = ()


@dataclass(frozen=True)
class Card:
    """One board card: the note it links and the column holding it."""

    title: str
    column: str


def find_vault(start: Path | None = None) -> Path:
    """Nearest directory at or above `start` holding `vault.toml`, else holding a `.git`."""
    here = (start or Path.cwd()).resolve()
    for marker in (CONFIG_NAME, ".git"):
        for directory in (here, *here.parents):
            if (directory / marker).exists():
                return directory
    raise VaultError(f"no vault root ({CONFIG_NAME} or .git) at or above {here}")


def find_root(vault: Path, config: Config) -> Path:
    """The workspace holding `<config.repos>/`: the nearest ancestor of `vault` with that
    subdirectory, else `vault`'s parent — the layout where the vault sits at the workspace root.
    """
    for directory in vault.parents:
        if (directory / config.repos).is_dir():
            return directory
    return vault.parent


def load_config(vault: Path) -> Config:
    """The vault's configuration; `vault.toml` overrides any default and `false` removes a cap."""
    path = vault / CONFIG_NAME
    raw = tomllib.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
    caps = dict(DEFAULT_CAPS)
    for key, value in raw.get("caps", {}).items():
        if value is False:
            caps.pop(str(key), None)
        else:
            caps[str(key)] = int(value)
    for key in caps:
        if key != "root" and not key.endswith("/"):
            raise VaultError(f"cap key {key!r} names no folder: use 'root' or a prefix ending in '/'")
    raw_scopes = raw.get("scopes", {})
    if not isinstance(raw_scopes, dict):
        raise VaultError("[scopes] must be a TOML table")
    scopes: list[Scope] = []
    for name, value in raw_scopes.items():
        if isinstance(value, str):
            escaped = value.replace("\\", "\\\\").replace('"', '\\"')
            raise VaultError(
                f"scope {name!r} uses the old string form; migrate to "
                f'{name} = {{ path = "{escaped}", branch = "main" }}'
            )
        if not isinstance(value, dict):
            raise VaultError(f"scope {name!r} must be an inline table")
        unknown = set(value) - {"path", "branch", "pin"}
        if unknown:
            raise VaultError(f"scope {name!r} has unknown keys: {', '.join(sorted(unknown))}")
        path_value = value.get("path")
        branch = value.get("branch")
        pin = value.get("pin")
        if not isinstance(path_value, str) or not path_value:
            raise VaultError(f"scope {name!r} needs a non-empty string path")
        if (branch is None) == (pin is None):
            raise VaultError(f"scope {name!r} needs exactly one of branch or pin")
        if branch is not None and (not isinstance(branch, str) or not _valid_branch(branch)):
            raise VaultError(f"scope {name!r} has invalid branch {branch!r}")
        if pin is not None and (not isinstance(pin, str) or not PIN_RE.fullmatch(pin)):
            raise VaultError(f"scope {name!r} pin must be a full 40-character commit ID")
        scopes.append(Scope(str(name), path_value, branch, pin.lower() if isinstance(pin, str) else None))
    return Config(
        board=str(raw.get("board", Config.board)),
        tasks=tuple(str(name) for name in raw.get("tasks", Config.tasks)),
        temp=str(raw.get("temp", Config.temp)),
        repos=str(raw.get("repos", Config.repos)),
        columns=tuple(str(name) for name in raw.get("columns", Config.columns)),
        promotion_bound=int(raw.get("promotion_bound", Config.promotion_bound)),
        promotion_days=int(raw.get("promotion_days", Config.promotion_days)),
        backlog_days=int(raw.get("backlog_days", Config.backlog_days)),
        merge_branch_prefix=str(raw.get("merge_branch_prefix", Config.merge_branch_prefix)),
        caps=caps,
        scopes=tuple(scopes),
    )


def _valid_branch(value: str) -> bool:
    """The branch-name constraints enforced by `git check-ref-format --branch`."""
    if not value or value.startswith("-") or value == "@" or value.endswith(("/", ".")):
        return False
    if ".." in value or "@{" in value or "//" in value:
        return False
    if any(ord(char) < 32 or ord(char) == 127 or char in " ~^:?*[\\" for char in value):
        return False
    return all(
        part and not part.startswith(".") and not part.endswith(".lock") for part in value.split("/")
    )


def _scalar(raw: str) -> str:
    return raw.strip().strip('"').strip("'")


def read_frontmatter(path: Path) -> dict[str, str | list[str]]:
    """Front-matter fields of a Markdown note; list values in flow or block form."""
    match = FRONTMATTER_RE.match(path.read_text(encoding="utf-8"))
    if not match:
        return {}
    data: dict[str, str | list[str]] = {}
    key = ""
    for line in match.group(1).splitlines():
        item = ITEM_RE.match(line)
        if item and key:
            current = data.get(key)
            data[key] = [*current, _scalar(item.group(1))] if isinstance(current, list) else [
                _scalar(item.group(1))
            ]
            continue
        found = FIELD_RE.match(line)
        if not found:
            continue
        key, raw = found.group(1), found.group(2).strip()
        if raw.startswith("[") and raw.endswith("]"):
            data[key] = [_scalar(part) for part in raw[1:-1].split(",") if part.strip()]
        else:
            data[key] = _scalar(raw)
    return data


def frontmatter_list(front: dict[str, str | list[str]], key: str) -> tuple[str, ...]:
    """A front-matter field as a tuple, whether it was written scalar, flow or block."""
    value = front.get(key)
    if isinstance(value, list):
        return tuple(item for item in value if item)
    return (value,) if value else ()


def read_cards(board: str) -> tuple[Card, ...]:
    """Every card on the board, in file order, tagged with the column heading above it."""
    cards: list[Card] = []
    column = ""
    for line in board.splitlines():
        heading = HEADING_RE.match(line)
        if heading:
            column = heading.group(1).strip().lower()
            continue
        card = CARD_RE.match(line)
        if card:
            cards.append(Card(card.group(1).strip(), column))
    return tuple(cards)


def _locate(board: str, title: str, exact_only: bool) -> tuple[list[str], int, str]:
    lines = board.splitlines()
    column = ""
    hits: list[tuple[int, str, str]] = []
    for index, line in enumerate(lines):
        heading = HEADING_RE.match(line)
        if heading:
            column = heading.group(1).strip().lower()
            continue
        card = CARD_RE.match(line)
        if not card:
            continue
        found = card.group(1).strip()
        if found == title or (not exact_only and title.lower() in found.lower()):
            hits.append((index, column, found))
    exact = [hit for hit in hits if hit[2] == title]
    if not hits:
        raise VaultError(f"card not found: {title!r}")
    if len(hits) > 1 and len(exact) != 1:
        raise VaultError("ambiguous card title; matches: " + ", ".join(hit[2] for hit in hits))
    index, column, _ = (exact or hits)[0]
    return lines, index, column


def move_card(board: str, title: str, target: str, drops: Sequence[str] = ()) -> tuple[str, str]:
    """Return the board with the card at the top of `target`, plus the column it came from."""
    lines, index, column = _locate(board, title, exact_only=False)
    line = lines[index]
    for tag in drops:
        line = re.sub(r"\s*#" + re.escape(tag) + r"(?=\s|$)", "", line)
    del lines[index]
    for position, existing in enumerate(lines):
        heading = HEADING_RE.match(existing)
        if heading and heading.group(1).strip().lower() == target:
            after = position + 1
            while after < len(lines) and not lines[after].strip():
                after += 1
            lines.insert(after, line.rstrip())
            return "\n".join(lines) + ("\n" if board.endswith("\n") else ""), column
    raise VaultError(f"target column not found: {target!r}")


def remove_card(board: str, title: str, column: str) -> str:
    """Return the board without the exact card, which must sit in `column`."""
    lines, index, found = _locate(board, title, exact_only=True)
    if found != column:
        raise VaultError(f"{title!r} is in {found!r}, not {column!r}")
    del lines[index]
    return "\n".join(lines) + ("\n" if board.endswith("\n") else "")


class Repo:
    """Git commands for one clone, plus the race-safe commit-and-push transaction."""

    def __init__(self, root: Path) -> None:
        self.root = root

    def git(
        self,
        *args: str,
        check: bool = True,
        timeout: float | Callable[[], float] | None = None,
        env: Mapping[str, str] | None = None,
        input_text: str | None = None,
    ) -> subprocess.CompletedProcess[str]:
        argv = ("git", "-C", str(self.root), *args)
        resolved_timeout = timeout() if callable(timeout) else timeout
        if resolved_timeout is None:
            result = subprocess.run(
                argv,
                capture_output=True,
                text=True,
                encoding="utf-8",
                env={**os.environ, **env} if env else None,
                input=input_text,
            )
        else:
            grouped = os.name == "posix"
            process = subprocess.Popen(
                argv,
                stdin=subprocess.PIPE if input_text is not None else None,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                env={**os.environ, **env} if env else None,
                start_new_session=grouped,
            )
            try:
                stdout, stderr = process.communicate(input_text, timeout=resolved_timeout)
            except subprocess.TimeoutExpired as error:
                stop_grace = min(0.2, max(0.05, resolved_timeout))
                if grouped:
                    with suppress(ProcessLookupError):
                        os.killpg(process.pid, signal.SIGTERM)
                else:
                    process.terminate()
                try:
                    process.wait(timeout=stop_grace)
                except subprocess.TimeoutExpired:
                    if grouped:
                        with suppress(ProcessLookupError):
                            os.killpg(process.pid, signal.SIGKILL)
                    else:
                        process.kill()
                    try:
                        process.wait(timeout=stop_grace)
                    except subprocess.TimeoutExpired as kill_error:
                        raise VaultError(f"git {' '.join(args)} did not stop after SIGKILL") from kill_error
                raise VaultError(f"git {' '.join(args)} timed out after {resolved_timeout:g}s") from error
            result = subprocess.CompletedProcess(argv, process.returncode, stdout, stderr)
        if check and result.returncode:
            raise VaultError(f"git {' '.join(args)} failed: {(result.stderr or result.stdout).strip()}")
        return result

    def ok(self, *args: str) -> bool:
        """Whether the command succeeded; used where failure is a checked fact, not an error."""
        return self.git(*args, check=False).returncode == 0

    def require_clean(self, paths: Sequence[str]) -> None:
        """Refuse while a path this action rewrites is dirty; a vault is routinely dirty elsewhere."""
        dirty = self.git("status", "--porcelain", "--", *paths).stdout.strip()
        if dirty:
            raise VaultError("uncommitted changes in the paths this action rewrites:\n" + dirty)

    def sync(self) -> None:
        """Rebase onto the remote before touching tracked state; a conflict fails loud."""
        if not self.ok("pull", "--rebase", "-q"):
            self.git("rebase", "--abort", check=False)
            raise VaultError(f"{self.root} could not rebase onto origin — reconcile manually")

    def commit(self, paths: Sequence[str], message: str) -> None:
        self.git("add", "-A", "--", *paths)
        self.git("commit", "-q", "-m", message)

    def push(self, owned: Sequence[str], reapply: Callable[[], None]) -> None:
        """Push HEAD to origin/main, re-applying `reapply` onto upstream when another writer races."""
        for _ in range(6):
            if self.ok("push", "-q", "origin", "HEAD:main"):
                return
            if not self.ok("pull", "--rebase", "-q"):
                unmerged = [
                    name
                    for name in self.git("diff", "--name-only", "--diff-filter=U", check=False)
                    .stdout.split("\n")
                    if name.strip()
                ]
                if [name for name in unmerged if name not in owned]:
                    self.git("rebase", "--abort", check=False)
                    raise VaultError("conflict outside the swept files:\n" + "\n".join(unmerged))
                try:
                    reapply()
                except VaultError:
                    self.git("rebase", "--abort", check=False)
                    raise
                self.git("add", "-A", "--", *owned)
                self.git("-c", "core.editor=true", "rebase", "--continue", check=False)
        raise VaultError("could not push after retries — reconcile without force-pushing")

    def last_commit_time(self, relative: str) -> int:
        """Unix time of the last commit touching `relative`; 0 when the path has no history."""
        stamp = self.git("log", "-1", "--format=%ct", "--", relative, check=False).stdout.strip()
        return int(stamp) if stamp.isdigit() else 0


def prepare(vault: Path, paths: Sequence[str]) -> Repo:
    """The vault repo, refused while a target path is dirty, then rebased onto its remote."""
    repo = Repo(vault)
    repo.require_clean(paths)
    repo.sync()
    return repo


def move_and_push(repo: Repo, config: Config, title: str, target: str, drops: Sequence[str] = ()) -> str:
    """Move one card into `target`, dropping `drops` tags from it, and push past a racing writer."""
    board = repo.root / config.board
    text, previous = move_card(board.read_text(encoding="utf-8"), title, target, drops)
    if previous == target:
        return f"{title!r} is already in {target}"

    def reapply() -> None:
        upstream = repo.git("show", f"origin/main:{config.board}").stdout
        board.write_text(move_card(upstream, title, target, drops)[0], encoding="utf-8")

    board.write_text(text, encoding="utf-8")
    repo.commit([config.board], f"kanban: {title} {previous} -> {target}")
    repo.push([config.board], reapply)
    return f"moved {title!r}: {previous} -> {target}"


def note_paths(vault: Path) -> tuple[Path, ...]:
    """Every tracked Markdown note in the vault."""
    listed = Repo(vault).git("ls-files", "-z", "--", "*.md").stdout.split("\0")
    return tuple(vault / name for name in listed if name)
