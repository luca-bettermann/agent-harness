"""The hygiene checker: nothing created outlives its step unless promoted."""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path

from .board import Card, Config, Repo, frontmatter_list, note_paths, read_cards, read_frontmatter
from .hook import tracked_breaches
from .sweep import PROMOTION, task_notes

DAY = 86400
OPEN = "open"


@dataclass(frozen=True)
class Row:
    """One class of hygiene finding; only blocking rows refuse the action that called the check."""

    name: str
    blocking: bool
    findings: tuple[str, ...]


def _clones(root: Path, config: Config) -> tuple[Path, ...]:
    canonical = root / config.repos
    if not canonical.is_dir():
        return ()
    return tuple(sorted(path for path in canonical.iterdir() if (path / ".git").exists()))


def _note_for(vault: Path, config: Config, title: str) -> Path | None:
    for folder in config.tasks:
        path = vault / folder / f"{title}.md"
        if path.is_file():
            return path
    return None


def live_streams(vault: Path, config: Config) -> dict[str, Card]:
    """Stream name to its card, for every stream card left of `promotion`."""
    board = (vault / config.board).read_text(encoding="utf-8")
    cutoff = config.columns.index(PROMOTION)
    live: dict[str, Card] = {}
    for card in read_cards(board):
        if card.column not in config.columns or config.columns.index(card.column) >= cutoff:
            continue
        note = _note_for(vault, config, card.title)
        front = read_frontmatter(note) if note else {}
        name = front.get("stream")
        if front.get("type") == "stream" and isinstance(name, str) and name:
            live[name] = card
    return live


def _worktrees(root: Path, config: Config, live: dict[str, Card]) -> tuple[str, ...]:
    """Worktrees whose branch belongs to no live stream card and is no merge branch."""
    findings: list[str] = []
    for clone in _clones(root, config):
        listing = Repo(clone).git("worktree", "list", "--porcelain").stdout
        for entry in listing.split("\n\n"):
            path, branch = "", ""
            for line in entry.splitlines():
                if line.startswith("worktree "):
                    path = line[len("worktree "):]
                elif line.startswith("branch "):
                    branch = line[len("branch "):].removeprefix("refs/heads/")
            if not path or Path(path).resolve() == clone.resolve():
                continue
            kind, _, rest = branch.partition("/")
            if branch.startswith(config.merge_branch_prefix) or (kind == "stream" and rest in live):
                continue
            if kind == "lane" and rest.split("/")[0] in live:
                continue
            findings.append(f"{clone.name}: worktree {path} on {branch or 'a detached HEAD'}")
    return tuple(findings)


def _clone_edits(root: Path, config: Config) -> tuple[str, ...]:
    """Canonical clones are fetch-only; a tracked change in one is a blocking failure."""
    findings: list[str] = []
    for clone in _clones(root, config):
        dirty = Repo(clone).git("status", "--porcelain", "--untracked-files=no").stdout.strip()
        if dirty:
            detail = dirty.replace("\n", "\n          ")
            findings.append(f"{clone.name}: canonical clone edited\n          {detail}")
    return tuple(findings)


def _temp(vault: Path, config: Config) -> tuple[str, ...]:
    temp = vault / config.temp
    if not temp.is_dir():
        return ()
    return tuple(
        path.relative_to(vault).as_posix() for path in sorted(temp.rglob("*")) if path.is_file()
    )


def _missing_branches(vault: Path, config: Config, root: Path, live: dict[str, Card]) -> tuple[str, ...]:
    """Live stream cards whose `stream/<name>` branch is missing from any listed repository.

    Every participating repository must carry the branch: one of several is not a live stream.
    The branch publishes on entry to `open` (AGENTS.md §5), so this only applies from `open`
    up to (excluding) `promotion`; a `backlog` stream has no branch by design and is skipped
    here, though it still counts as a live stream for membership and caps.
    """
    open_index = config.columns.index(OPEN)
    findings: list[str] = []
    for name, card in live.items():
        if config.columns.index(card.column) < open_index:
            continue
        note = _note_for(vault, config, card.title)
        repos = frontmatter_list(read_frontmatter(note), "repos") if note else ()
        if not repos:
            findings.append(f"{card.title}: lists no repos, so stream/{name} can be on no remote")
            continue
        missing = [
            repo
            for repo in repos
            if not Repo(root / config.repos / repo)
            .git("ls-remote", "--heads", "origin", f"stream/{name}", check=False)
            .stdout.strip()
        ]
        if missing:
            findings.append(f"{card.title}: stream/{name} is on no remote of {', '.join(missing)}")
    return tuple(findings)


def _promotion(vault: Path, config: Config, now: float) -> tuple[str, ...]:
    board = (vault / config.board).read_text(encoding="utf-8")
    cards = [card for card in read_cards(board) if card.column == PROMOTION]
    repo = Repo(vault)
    findings: list[str] = []
    if len(cards) > config.promotion_bound:
        findings.append(f"{len(cards)} cards in {PROMOTION}, over the bound of {config.promotion_bound}")
    for card in cards:
        note = _note_for(vault, config, card.title)
        if note is None:
            continue
        stamp = repo.last_commit_time(note.relative_to(vault).as_posix())
        age = int((now - stamp) // DAY) if stamp else 0
        if age > config.promotion_days:
            findings.append(
                f"{card.title}: {age} days since the note last changed,"
                f" over the {config.promotion_days}-day {PROMOTION} bound"
            )
    return tuple(findings)


def _stale_backlog(vault: Path, config: Config, now: float) -> tuple[str, ...]:
    """Task notes with no stream whose note last changed longer ago than the backlog bound."""
    repo = Repo(vault)
    findings: list[str] = []
    for note in task_notes(vault, config):
        front = read_frontmatter(note)
        if front.get("type") != "task" or front.get("stream"):
            continue
        stamp = repo.last_commit_time(note.relative_to(vault).as_posix())
        age = int((now - stamp) // DAY) if stamp else 0
        if age > config.backlog_days:
            findings.append(f"{note.name}: {age} days since the note last changed")
    return tuple(findings)


def check(vault: Path, config: Config, root: Path, now: float | None = None) -> tuple[Row, ...]:
    """Every hygiene row for one root and its vault."""
    moment = time.time() if now is None else now
    live = live_streams(vault, config)
    return (
        Row("canonical clones", True, _clone_edits(root, config)),
        Row("worktrees", True, _worktrees(root, config, live)),
        Row("temp", True, _temp(vault, config)),
        Row("stream branches", True, _missing_branches(vault, config, root, live)),
        Row("note caps", False, tracked_breaches(vault, config, note_paths(vault))),
        Row(PROMOTION, False, _promotion(vault, config, moment)),
        Row("backlog age", False, _stale_backlog(vault, config, moment)),
    )


def render(rows: tuple[Row, ...]) -> str:
    """One summary line per row class, with its findings beneath."""
    lines: list[str] = []
    for row in rows:
        if not row.findings:
            lines.append(f"    ok  {row.name}")
            continue
        label = "FAIL" if row.blocking else "note"
        lines.append(f"  {label}  {row.name}: {len(row.findings)} finding(s)")
        lines.extend(f"        - {finding}" for finding in row.findings)
    return "\n".join(lines)


def blocked(rows: tuple[Row, ...]) -> bool:
    """Whether a blocking row has findings, which refuses the calling action."""
    return any(row.blocking and row.findings for row in rows)
