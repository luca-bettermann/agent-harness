"""The two-phase stream sweep: promotion on verified merge, deletion on a ticked Execute."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .board import (
    Config,
    Repo,
    VaultError,
    frontmatter_list,
    move_and_push,
    note_paths,
    prepare,
    read_frontmatter,
    remove_card,
)
from .links import link_targets, links_into, referrers, render_referrers, resolve

SECTION_LABELS = (
    "Owner",
    "Stream description",
    "Rulings in force",
    "Tasks",
    "MR link",
    "Merge evidence",
    "Promotion",
)
LABEL_RE = re.compile(rf"^(?:##\s+)?({'|'.join(SECTION_LABELS)})\s*:?\s*$", re.IGNORECASE)
EVIDENCE_RE = re.compile(
    r"^\s*-\s+(?P<repo>[^:]+):\s*(?P<tip>[0-9a-fA-F]{7,40})\s*(?:->\s*(?P<target>\S+))?\s*$"
)
EXECUTE_RE = re.compile(r"^\s*-\s+\[(?P<box>[ xX])\]\s+Execute\s*$", re.MULTILINE)
DEFAULT_TARGET = "origin/main"
PROMOTION = "promotion"


@dataclass(frozen=True)
class Stream:
    """One stream: its note, participating repositories, merge evidence and member task notes."""

    name: str
    note: Path
    repos: tuple[str, ...]
    evidence: dict[str, tuple[str, str]]
    execute: bool
    members: tuple[Path, ...]

    @property
    def doomed(self) -> tuple[Path, ...]:
        """The whole deletion set: the stream note and every front-matter member."""
        return (self.note, *self.members)


def section(text: str, label: str) -> str:
    """The block under a `Label:` or `## Label` line, ending only at another known label.

    Prose never ends a section: a label is one of `SECTION_LABELS` and nothing else.
    """
    collected: list[str] = []
    inside = False
    for line in text.splitlines():
        found = LABEL_RE.match(line)
        if found:
            inside = found.group(1).strip().lower() == label.lower()
            continue
        if inside:
            collected.append(line)
    return "\n".join(collected)


def _evidence(text: str) -> dict[str, tuple[str, str]]:
    """Recorded merge evidence — `- <repo>: <tip sha> -> <target ref>` under `Merge evidence:`."""
    found: dict[str, tuple[str, str]] = {}
    for line in section(text, "Merge evidence").splitlines():
        match = EVIDENCE_RE.match(line)
        if match:
            target = match.group("target") or DEFAULT_TARGET
            found[match.group("repo").strip()] = (match.group("tip"), target)
    return found


def task_notes(vault: Path, config: Config) -> tuple[Path, ...]:
    """Every note at any depth under a configured tasks folder."""
    return tuple(path for folder in config.tasks for path in sorted((vault / folder).rglob("*.md")))


def _membership_faults(vault: Path, note: Path, text: str, members: tuple[Path, ...]) -> tuple[str, ...]:
    """Disagreements between the note's `Tasks:` list and the front matter that authorises it."""
    listed = {target: resolve(target, note, vault) for target in link_targets(section(text, "Tasks"))}
    known = {path.resolve() for path in members}
    resolved = {path for path in listed.values() if path is not None}
    faults = [
        f"{target}: listed under Tasks but no front-matter member of the stream"
        for target, path in sorted(listed.items())
        if path is None or path not in known
    ]
    faults.extend(
        f"{path.stem}: a front-matter member of the stream but not listed under Tasks"
        for path in sorted(members)
        if path.resolve() not in resolved
    )
    return tuple(faults)


def load_stream(vault: Path, config: Config, name: str) -> Stream:
    """The stream note for `name` and the task notes whose front matter claims membership."""
    fronts = {path: read_frontmatter(path) for path in task_notes(vault, config)}
    notes = [
        path
        for path, front in fronts.items()
        if front.get("type") == "stream" and front.get("stream") == name
    ]
    if len(notes) != 1:
        raise VaultError(f"expected exactly one stream note for {name!r}; found {len(notes)}")
    note = notes[0]
    repos = frontmatter_list(fronts[note], "repos")
    if not repos:
        raise VaultError(f"{note.name} lists no repos: — the merge cannot be verified")
    text = note.read_text(encoding="utf-8")
    members = tuple(path for path, front in fronts.items() if path != note and front.get("stream") == name)
    faults = _membership_faults(vault, note, text, members)
    if faults:
        raise VaultError(
            f"{note.name} disagrees with the front matter that owns membership:\n"
            + "\n".join(f"- {fault}" for fault in faults)
        )
    return Stream(name, note, repos, _evidence(text), _execute(text), members)


def _execute(text: str) -> bool:
    match = EXECUTE_RE.search(section(text, "Promotion"))
    return bool(match and match.group("box").lower() == "x")


def clone_for(vault: Path, root: Path, config: Config, name: str) -> Path:
    """The canonical clone for `name` — the vault itself when `name` is the vault's own folder.

    Every other repo is a fetch-only clone at `<root>/<repos>/<name>`; the vault sits directly
    under `root` instead (AGENTS.md §1), so a stream that lists the vault by its own folder
    name is verified against the live vault clone, never a stale mirror under `repos/`.
    """
    return vault if name == vault.name else root / config.repos / name


def verify_merged(vault: Path, root: Path, config: Config, stream: Stream) -> tuple[str, ...]:
    """Repositories whose recorded `stream/<name>` tip is not provably an ancestor of its target.

    Branch absence is never death: only ancestry of the recorded tip counts, and an
    unknown ref or a failed fetch preserves the stream.
    """
    branch = f"stream/{stream.name}"
    failures: list[str] = []
    for name in stream.repos:
        clone = clone_for(vault, root, config, name)
        if not (clone / ".git").exists():
            failures.append(f"{name}: no canonical clone at {clone}")
            continue
        repo = Repo(clone)
        record = stream.evidence.get(name)
        if record is None:
            failures.append(f"{name}: the stream note records no merge evidence for {branch}")
            continue
        tip, target = record
        if not repo.ok("fetch", "--quiet", "origin"):
            failures.append(f"{name}: fetch failed — the merge stays unverified")
        elif not repo.ok("rev-parse", "--verify", "--quiet", f"{tip}^{{commit}}"):
            failures.append(f"{name}: unknown commit {tip}")
        elif not repo.ok("rev-parse", "--verify", "--quiet", f"{target}^{{commit}}"):
            failures.append(f"{name}: unknown merge target {target}")
        elif not repo.ok("merge-base", "--is-ancestor", tip, target):
            failures.append(f"{name}: {tip} is not an ancestor of {target} — {branch} is not merged")
    return tuple(failures)


def _require_merged(vault: Path, root: Path, config: Config, stream: Stream) -> None:
    failures = verify_merged(vault, root, config, stream)
    if failures:
        raise VaultError(
            "merge unverified — the stream is preserved:\n" + "\n".join(f"- {line}" for line in failures)
        )


def to_promotion(vault: Path, config: Config, root: Path, name: str) -> str:
    """Phase one: move a merged stream's card into `promotion`."""
    repo = prepare(vault, [config.board])
    stream = load_stream(vault, config, name)
    _require_merged(vault, root, config, stream)
    return move_and_push(repo, config, stream.note.stem, PROMOTION)


def execute(vault: Path, config: Config, root: Path, name: str) -> str:
    """Phase two: delete the stream note, its card and every front-matter member in one commit."""
    repo = prepare(vault, [config.board, *config.tasks])
    stream = load_stream(vault, config, name)
    _require_merged(vault, root, config, stream)
    if not stream.execute:
        raise VaultError(f"the Promotion section of {stream.note.name} has no ticked Execute box")
    owned = [config.board, *(path.relative_to(vault).as_posix() for path in stream.doomed)]
    board = vault / config.board
    title = stream.note.stem
    swept = remove_card(board.read_text(encoding="utf-8"), title, PROMOTION)
    inbound = referrers(tuple(path for path in note_paths(vault) if path != board), stream.doomed, vault)
    hits = links_into(swept, board, stream.doomed, vault)
    if hits:
        inbound[board] = hits
    if inbound:
        raise VaultError(
            "notes outside the stream still reference it:\n" + render_referrers(inbound, vault)
        )

    def reapply() -> None:
        upstream = repo.git("show", f"origin/main:{config.board}").stdout
        board.write_text(remove_card(upstream, title, PROMOTION), encoding="utf-8")
        for note in stream.doomed:
            note.unlink(missing_ok=True)

    board.write_text(swept, encoding="utf-8")
    for note in stream.doomed:
        note.unlink()
    repo.commit(owned, f"kanban: sweep stream {name}")
    repo.push(owned, reapply)
    return f"swept stream {name!r}: {len(stream.doomed)} note(s) and one card"
