"""The one resolver for every link syntax a vault note can use to name another note."""

from __future__ import annotations

import re
from collections.abc import Iterable
from pathlib import Path
from urllib.parse import unquote

WIKILINK_RE = re.compile(r"\[\[([^\[\]\n]+?)\]\]")
MDLINK_RE = re.compile(r"\[[^\]\n]*\]\(\s*<?([^)>\n]+?)>?\s*\)")


def link_targets(text: str) -> tuple[str, ...]:
    """Every note a text names: wikilinks stripped of alias and heading, Markdown `.md` links."""
    targets: list[str] = []
    for raw in WIKILINK_RE.findall(text):
        target = raw.split("|", 1)[0].split("#", 1)[0].strip()
        if target:
            targets.append(target)
    for raw in MDLINK_RE.findall(text):
        target = unquote(raw.split("#", 1)[0]).strip()
        if target and "://" not in target and target.lower().endswith(".md"):
            targets.append(target)
    return tuple(targets)


def note_names(note: Path, vault: Path) -> frozenset[str]:
    """Every string that names `note`: its title, and its vault-relative path with and without suffix."""
    relative = note.relative_to(vault)
    return frozenset({note.stem, relative.as_posix(), relative.with_suffix("").as_posix()})


def resolve(target: str, origin: Path, vault: Path) -> Path | None:
    """The note `target` addresses from `origin`, by note-relative or vault-relative path."""
    candidate = target if target.lower().endswith(".md") else f"{target}.md"
    for base in (origin.parent, vault):
        path = base / candidate
        if path.is_file():
            return path.resolve()
    return None


def links_into(text: str, origin: Path, deleted: Iterable[Path], vault: Path) -> tuple[str, ...]:
    """The targets in `text` naming a note in `deleted`, whether or not that note still exists.

    Text rather than a path, so the guard can read a board the sweep has not written yet.
    """
    doomed = {path.resolve() for path in deleted}
    names = {name for path in doomed for name in note_names(path, vault)}
    return tuple(
        sorted(
            {
                target
                for target in link_targets(text)
                if target in names or resolve(target, origin, vault) in doomed
            }
        )
    )


def referrers(
    notes: Iterable[Path], deleted: Iterable[Path], vault: Path
) -> dict[Path, tuple[str, ...]]:
    """Notes outside `deleted` that name something inside it, mapped to the offending targets."""
    doomed = {path.resolve() for path in deleted}
    found: dict[Path, tuple[str, ...]] = {}
    for note in notes:
        if not note.is_file() or note.resolve() in doomed:
            continue
        hits = links_into(note.read_text(encoding="utf-8"), note, deleted, vault)
        if hits:
            found[note] = hits
    return found


def render_referrers(found: dict[Path, tuple[str, ...]], vault: Path) -> str:
    """The refusal body listing each referring note and the targets it names."""
    return "\n".join(
        f"- {note.relative_to(vault).as_posix()} -> {', '.join(targets)}"
        for note, targets in sorted(found.items())
    )
