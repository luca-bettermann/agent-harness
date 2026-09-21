"""Derive each stream note's lifecycle `status` from GitLab and git facts and write it back.

`status` is a materialisation, not a hand-edited field: every run recomputes it and overwrites
the note's front matter. A stream lands through GitLab's native merge with delete-source-branch
on, so the `stream/<name>` branch is gone once it has landed while GitLab keeps the merge-request
record. Detection per repository:

- `landed` — the latest merge request whose source branch is `stream/<name>` is merged and the
  branch is gone; a live branch is never landed, so an old merged MR under a reused name cannot
  mark a newer incarnation landed.
- `in progress` — the `stream/<name>` branch still exists, or the latest such MR is open.
- `planned` — neither.

A stream's status is the least-advanced of its repositories'. The MR state is read with `glab`
against each repository's GitLab project; branch existence is a local ref check. `--local` is the
offline path: it cannot tell a landed stream (its branch gone) from a planned one, so it derives
and writes no status — running hygiene only — rather than persisting a guess over a correct value.

`vault sync` neither pulls nor commits: its caller owns refreshing the vault and the agent
owns committing. Sync only derives statuses (fetching each repository once in the
default, remote mode) and writes them into the working tree, in three ordered phases —
preflight derives every status, commit writes the notes whose bytes changed, postflight runs
hygiene. A derivation fault raises in preflight, so no note is ever left half-written.
"""

from __future__ import annotations

import json
import re
import subprocess
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

from . import hygiene
from .board import FRONTMATTER_RE, Config, Repo, VaultError, frontmatter_list, read_frontmatter
from .sweep import clone_for, task_notes

PLANNED = "planned"
IN_PROGRESS = "in progress"
LANDED = "landed"
# Least-advanced wins: a stream is only as far along as its most-behind repository.
_RANK = {PLANNED: 0, IN_PROGRESS: 1, LANDED: 2}
_STATUS_RE = re.compile(r"^status\s*:", re.IGNORECASE)
# GitLab merge-request states this tool reads (the API's own vocabulary).
MR_MERGED = "merged"
MR_OPENED = "opened"
# The full state vocabulary; a record outside it is a malformed, unreliable response.
_KNOWN_MR_STATES = frozenset({MR_MERGED, MR_OPENED, "closed", "locked"})


@dataclass(frozen=True)
class Report:
    """One sync run: notes skipped without a git-derived status, and the hygiene rows after."""

    notices: tuple[str, ...]
    rows: tuple[hygiene.Row, ...]


def _origin_url(clone: Path) -> str:
    """The `origin` remote URL of a canonical clone; a clone without one fails loud."""
    return Repo(clone).git("remote", "get-url", "origin").stdout.strip()


def _origin_host(url: str) -> str:
    """The lower-cased hostname of a remote URL, from a URL or scp-like (`git@host:path`) form.

    Classification keys on the host alone: `git@gitlab.example.org:mirrors/github.com/x.git` is a
    GitLab remote, so a substring test on the whole URL would wrongly reject it.
    """
    if "://" in url:
        return (urlparse(url).hostname or "").lower()
    host_path = url.partition("@")[2] or url  # drop any scp-form user, keeping [host]:path
    if host_path.startswith("["):
        return host_path[1 : host_path.find("]")].lower()  # unwrap a bracketed IPv6 literal host
    return host_path.split(":", 1)[0].lower()


def _run_glab(clone: Path, name: str) -> str:
    """Raw `glab` JSON for every MR whose source branch is `stream/<name>` in the clone's project.

    Run inside the canonical clone so glab resolves the GitLab project from its `origin` remote.
    A glab that will not launch (missing binary) or exits non-zero (auth, network, not a GitLab
    project) raises loud — a lifecycle fact is never guessed from a failed query.
    """
    argv = ("glab", "mr", "list", "--source-branch", f"stream/{name}", "--all", "--output", "json")
    try:
        result = subprocess.run(argv, cwd=clone, capture_output=True, text=True)
    except OSError as error:
        raise VaultError(
            f"{clone.name}: could not launch glab ({error}) — install the GitLab CLI and put it on PATH"
        ) from error
    if result.returncode:
        raise VaultError(f"{clone.name}: glab mr list failed: {(result.stderr or result.stdout).strip()}")
    return result.stdout


def _latest_state(payload: str, repo: str) -> str | None:
    """The newest MR's state in a glab JSON list — highest `iid` wins — or None for a valid empty list.

    `iid` is the GitLab project-scoped, monotonically increasing MR number, so the highest is the
    latest incarnation; selecting by it stops an old merged MR under a reused branch name from
    outvoting a newer one. An empty, whitespace-only or undecodable response is not "no MRs" — it is
    an unreliable query and raises, distinct from a valid empty list `[]` that legitimately means
    none. A record lacking an integer `iid` or a known `state` is malformed and also raises,
    never a KeyError.
    """
    if not payload.strip():
        raise VaultError(f"{repo}: glab returned an empty response — the MR query is unreliable")
    try:
        records = json.loads(payload)
    except json.JSONDecodeError as error:
        raise VaultError(
            f"{repo}: glab returned undecodable JSON — the MR query is unreliable ({error})"
        ) from error
    if not isinstance(records, list):
        raise VaultError(f"{repo}: glab returned a non-list MR response — the query is unreliable")
    if not records:
        return None
    for mr in records:
        if (
            not isinstance(mr, dict)
            or not isinstance(mr.get("iid"), int)
            or isinstance(mr.get("iid"), bool)
            or not isinstance(mr.get("state"), str)
            or mr.get("state") not in _KNOWN_MR_STATES
        ):
            raise VaultError(
                f"{repo}: glab returned a malformed MR record {mr!r} — the MR query is unreliable"
            )
    return max(records, key=lambda mr: mr["iid"])["state"]


def _mr_state(clone: Path, name: str) -> str | None:
    """The latest `stream/<name>` MR state in the clone's GitLab project, or None when there is none.

    The single seam onto GitLab. A non-GitLab origin host raises loud rather than reading as no MR,
    so a GitHub-hosted repo can never be silently mistaken for an unstarted stream.
    """
    host = _origin_host(_origin_url(clone))
    if host == "github.com":
        raise VaultError(
            f"{clone.name}: origin host {host} is GitHub, not GitLab — landed is unreadable via glab"
        )
    return _latest_state(_run_glab(clone, name), clone.name)


def _repo_status(repo: Repo, clone: Path, name: str) -> str:
    """This repository's contribution to the stream status.

    A live `stream/<name>` branch means the stream has not landed — landing merges through GitLab
    with delete-source-branch on, removing it — so branch existence is decided first and no merged
    MR under a reused name can mark a live branch landed. With the branch gone, the latest MR's
    state decides: merged is landed, open is in progress, anything else is planned.
    """
    if repo.ok("rev-parse", "--verify", "--quiet", f"origin/stream/{name}^{{commit}}"):
        return IN_PROGRESS
    state = _mr_state(clone, name)
    if state == MR_MERGED:
        return LANDED
    return IN_PROGRESS if state == MR_OPENED else PLANNED


def stream_status(vault: Path, config: Config, root: Path, name: str, repos: Sequence[str]) -> str:
    """The least-advanced `stream/<name>` state across every listed repository."""
    contributions: list[str] = []
    for repo_name in repos:
        clone = clone_for(vault, root, config, repo_name)
        if not (clone / ".git").exists():
            raise VaultError(f"{repo_name}: no canonical clone at {clone}")
        contributions.append(_repo_status(Repo(clone), clone, name))
    return min(contributions, key=_RANK.__getitem__)


def _fetch_all(vault: Path, config: Config, root: Path, repos: Iterable[str]) -> None:
    """Refresh each unique repository's refs once; a failed fetch refuses stale-ref derivation."""
    for repo_name in sorted(set(repos)):
        clone = clone_for(vault, root, config, repo_name)
        if not (clone / ".git").exists():
            raise VaultError(f"{repo_name}: no canonical clone at {clone}")
        if not Repo(clone).ok("fetch", "--quiet", "--prune", "origin"):
            raise VaultError(f"{repo_name}: fetch failed — refusing to derive status from stale refs")


def with_status(text: str, value: str) -> str:
    """The note text with `status: <value>` in its front matter, updated in place or appended.

    Surgical: only the front-matter block is touched — no key is reordered and the body is left
    untouched — so a rerun that derives the same value reproduces the file byte for byte. The
    note's own line separator is preserved, so a CRLF note stays CRLF.
    """
    match = FRONTMATTER_RE.match(text)
    if not match:
        raise VaultError("a stream note has no front matter to hold its status")
    newline = "\r\n" if "\r\n" in match.group(0) else "\n"
    lines = match.group(1).split(newline)
    for index, line in enumerate(lines):
        if _STATUS_RE.match(line):
            lines[index] = f"status: {value}"
            break
    else:
        lines.append(f"status: {value}")
    return text[: match.start(1)] + newline.join(lines) + text[match.end(1) :]


def run(vault: Path, config: Config, root: Path, local: bool = False) -> Report:
    """Recompute and write every stream note's status (offline `--local` writes none), then return
    skip notices and hygiene rows."""
    notices: list[str] = []
    derivable: list[tuple[Path, str, tuple[str, ...]]] = []
    for note in task_notes(vault, config):
        front = read_frontmatter(note)
        if front.get("type") != "stream":
            continue
        name = front.get("stream")
        if not isinstance(name, str) or not name:
            notices.append(f"{note.name}: a stream note with no stream: value — skipped")
            continue
        repos = frontmatter_list(front, "repos")
        if not repos:
            notices.append(f"{note.name}: stream {name!r} lists no repos — no git-derived status")
            continue
        derivable.append((note, name, repos))

    if local:
        # Offline and report-only: sync cannot tell a landed stream (branch gone) from a planned
        # one, so it derives and writes no status — persisting a guess would overwrite a correct
        # committed value — and runs hygiene only.
        return Report(tuple(notices), hygiene.check(vault, config, root))

    _fetch_all(vault, config, root, (repo for _, _, repos in derivable for repo in repos))
    plan = [(note, stream_status(vault, config, root, name, repos)) for note, name, repos in derivable]
    for note, status in plan:
        text = note.read_text(encoding="utf-8")
        updated = with_status(text, status)
        if updated != text:
            note.write_text(updated, encoding="utf-8")
    return Report(tuple(notices), hygiene.check(vault, config, root))
