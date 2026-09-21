"""The note-size gate: one cap table, refusing only a staged note that grows past it — a ratchet."""

from __future__ import annotations

import shlex
import subprocess
from pathlib import Path

import pytest

from vaulttools import hook
from vaulttools.board import Repo, VaultError

from .conftest import git

CAPS = {"root": 15000, "tasks/": 10000, "doctrine/": 15000}


@pytest.mark.parametrize(
    ("relative", "expected"),
    [
        ("tasks/Task note.md", 10000),
        ("08 Tasks/Legacy note.md", None),
        ("doctrine/SKILLS - Coding.md", 15000),
        ("doctrine/skills/Nested.md", 15000),
        ("AGENTS.md", 15000),
        ("temp/scratch.md", None),
        ("tasks/data.json", None),
    ],
)
def test_the_cap_follows_the_folder_holding_the_note(relative, expected):
    assert hook.cap_for(relative, CAPS) == expected


def test_the_transitional_tasks_folder_keeps_the_task_cap():
    assert hook.cap_for("08 Tasks/Legacy note.md", {"08 Tasks/": 10000}) == 10000


def test_a_staged_task_note_over_its_cap_is_refused(bench):
    """A new note counts as growth from 0, so any new over-cap note refuses."""
    bench.write("tasks/Oversized.md", "x" * 10_001)
    subprocess.run(("git", "-C", str(bench.vault), "add", "-A"), check=True)
    breaches = hook.staged_breaches(Repo(bench.vault), bench.config)
    assert breaches == ("tasks/Oversized.md: 10001 chars over the 10000 cap (grew from 0)",)


def test_a_staged_doctrine_note_between_the_two_caps_passes(bench):
    bench.write("doctrine/Long.md", "x" * 12_000)
    subprocess.run(("git", "-C", str(bench.vault), "add", "-A"), check=True)
    assert hook.staged_breaches(Repo(bench.vault), bench.config) == ()


def test_the_installed_hook_refuses_the_commit_that_bypasses_the_cap(bench):
    hook.install(bench.vault)
    bench.write("tasks/Oversized.md", "y" * 10_500)
    subprocess.run(("git", "-C", str(bench.vault), "add", "-A"), check=True)
    result = subprocess.run(
        ("git", "-C", str(bench.vault), "commit", "-m", "bypass"),
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    output = result.stdout + result.stderr
    assert "tasks/Oversized.md: 10500 chars over the 10000 cap (grew from 0)" in output


def test_the_installed_hook_lets_a_note_within_its_cap_commit(bench):
    hook.install(bench.vault)
    bench.write("tasks/Small.md", "fine\n")
    subprocess.run(("git", "-C", str(bench.vault), "add", "-A"), check=True)
    result = subprocess.run(
        ("git", "-C", str(bench.vault), "commit", "-m", "within cap"), capture_output=True, text=True
    )
    assert result.returncode == 0


def test_a_note_shrunk_after_staging_is_refused_by_its_staged_size(bench):
    """Mutation caught: sizing the working-tree file, which a post-`git add` shrink slips past."""
    bench.write("tasks/Oversized.md", "x" * 10_001)
    git(bench.vault, "add", "-A")
    bench.write("tasks/Oversized.md", "small\n")
    assert hook.staged_breaches(Repo(bench.vault), bench.config) == (
        "tasks/Oversized.md: 10001 chars over the 10000 cap (grew from 0)",
    )


def test_an_over_cap_note_that_grows_further_is_refused(bench):
    bench.write("tasks/Legacy.md", "x" * 10_500)
    bench.commit("bench: legacy over-cap note")
    bench.write("tasks/Legacy.md", "x" * 10_600)
    git(bench.vault, "add", "-A")
    assert hook.staged_breaches(Repo(bench.vault), bench.config) == (
        "tasks/Legacy.md: 10600 chars over the 10000 cap (grew from 10500)",
    )


def test_an_over_cap_note_that_stays_the_same_size_is_allowed(bench):
    bench.write("tasks/Legacy.md", "x" * 10_500)
    bench.commit("bench: legacy over-cap note")
    bench.write("tasks/Legacy.md", "y" * 10_500)
    git(bench.vault, "add", "-A")
    assert hook.staged_breaches(Repo(bench.vault), bench.config) == ()


def test_an_over_cap_note_that_shrinks_is_allowed(bench):
    bench.write("tasks/Legacy.md", "x" * 10_500)
    bench.commit("bench: legacy over-cap note")
    bench.write("tasks/Legacy.md", "x" * 10_200)
    git(bench.vault, "add", "-A")
    assert hook.staged_breaches(Repo(bench.vault), bench.config) == ()


def test_a_note_crossing_the_cap_from_under_it_is_refused(bench):
    bench.write("tasks/Growing.md", "x" * 9_500)
    bench.commit("bench: under-cap note")
    bench.write("tasks/Growing.md", "x" * 10_500)
    git(bench.vault, "add", "-A")
    assert hook.staged_breaches(Repo(bench.vault), bench.config) == (
        "tasks/Growing.md: 10500 chars over the 10000 cap (grew from 9500)",
    )


def test_deleting_an_over_cap_note_is_allowed(bench):
    bench.write("tasks/Legacy.md", "x" * 10_500)
    bench.commit("bench: legacy over-cap note")
    subprocess.run(("git", "-C", str(bench.vault), "rm", "-q", "tasks/Legacy.md"), check=True)
    assert hook.staged_breaches(Repo(bench.vault), bench.config) == ()


def test_adding_a_status_line_to_an_over_cap_note_is_allowed(bench):
    """`status:` is tool-written derived metadata (written by `vault sync`), not counted content."""
    body = "x" * 10_600
    bench.write("tasks/Legacy.md", f"---\ntype: stream\nstream: legacy\nblocked:\n---\n{body}")
    bench.commit("bench: legacy stream note")
    bench.write(
        "tasks/Legacy.md", f"---\ntype: stream\nstream: legacy\nstatus: in progress\nblocked:\n---\n{body}"
    )
    git(bench.vault, "add", "-A")
    assert hook.staged_breaches(Repo(bench.vault), bench.config) == ()


def test_the_installed_hook_lets_a_status_line_land_on_an_over_cap_note(bench):
    """The actual bug: `vault sync` writing `status:` onto an already over-cap note must commit."""
    body = "x" * 10_600
    bench.write("tasks/Legacy.md", f"---\ntype: stream\nstream: legacy\nblocked:\n---\n{body}")
    bench.commit("bench: legacy stream note")
    hook.install(bench.vault)
    bench.write(
        "tasks/Legacy.md", f"---\ntype: stream\nstream: legacy\nstatus: in progress\nblocked:\n---\n{body}"
    )
    subprocess.run(("git", "-C", str(bench.vault), "add", "-A"), check=True)
    result = subprocess.run(
        ("git", "-C", str(bench.vault), "commit", "-m", "sync: status"), capture_output=True, text=True
    )
    assert result.returncode == 0


def test_changing_an_existing_status_value_on_an_over_cap_note_is_allowed(bench):
    body = "x" * 10_600
    bench.write(
        "tasks/Legacy.md", f"---\ntype: stream\nstream: legacy\nstatus: planned\nblocked:\n---\n{body}"
    )
    bench.commit("bench: legacy stream note")
    bench.write(
        "tasks/Legacy.md", f"---\ntype: stream\nstream: legacy\nstatus: landed\nblocked:\n---\n{body}"
    )
    git(bench.vault, "add", "-A")
    assert hook.staged_breaches(Repo(bench.vault), bench.config) == ()


def test_growing_the_body_of_an_over_cap_note_is_still_refused(bench):
    front = "---\ntype: stream\nstream: legacy\nblocked:\n---\n"
    bench.write("tasks/Legacy.md", front + "x" * 10_600)
    bench.commit("bench: legacy stream note")
    bench.write("tasks/Legacy.md", front + "x" * 10_700)
    git(bench.vault, "add", "-A")
    assert hook.staged_breaches(Repo(bench.vault), bench.config) == (
        "tasks/Legacy.md: 10700 chars over the 10000 cap (grew from 10600)",
    )


def test_a_note_whose_body_alone_exceeds_the_cap_is_a_breach_with_front_matter_excluded(bench):
    """The reported size is the BODY's length, not body-plus-front-matter."""
    body = "x" * 10_500
    bench.write("tasks/Oversized.md", f"---\ntype: task\nstream:\nblocked:\n---\n{body}")
    git(bench.vault, "add", "-A")
    assert hook.staged_breaches(Repo(bench.vault), bench.config) == (
        "tasks/Oversized.md: 10500 chars over the 10000 cap (grew from 0)",
    )


def test_a_dash_fence_later_in_the_body_is_not_mistaken_for_front_matter(bench):
    """`FRONTMATTER_RE` is anchored and non-greedy, so a later `---` (e.g. a horizontal rule)
    stays part of the body instead of truncating it away."""
    front = "---\ntype: task\nstream:\nblocked:\n---\n"
    body = "intro\n\n---\n\n" + "x" * 10_500
    bench.write("tasks/Oversized.md", front + body)
    git(bench.vault, "add", "-A")
    assert hook.staged_breaches(Repo(bench.vault), bench.config) == (
        f"tasks/Oversized.md: {len(body)} chars over the 10000 cap (grew from 0)",
    )


def test_a_note_with_no_front_matter_is_measured_whole(bench):
    """No leading `---` fence: nothing to strip, so the whole file is the body."""
    bench.write("tasks/Oversized.md", "x" * 10_001)
    git(bench.vault, "add", "-A")
    assert hook.staged_breaches(Repo(bench.vault), bench.config) == (
        "tasks/Oversized.md: 10001 chars over the 10000 cap (grew from 0)",
    )


def test_an_empty_front_matter_block_does_not_swallow_the_body_up_to_a_later_fence(bench):
    """Mutation caught: a non-greedy `(.*?)\\r?\\n---\\r?\\n` finds no `\\n---\\n` for an empty,
    zero-length capture against adjacent `---`/`---` lines, so it backtracks past the entire
    empty block to the NEXT `---` anywhere in the file -- reporting 0 and letting the real body
    escape the cap entirely."""
    trailing_fence = "\n---\n"
    body = "x" * 10_500 + trailing_fence
    bench.write("tasks/Oversized.md", f"---\n---\n{body}")
    git(bench.vault, "add", "-A")
    assert hook.staged_breaches(Repo(bench.vault), bench.config) == (
        f"tasks/Oversized.md: {len(body)} chars over the 10000 cap (grew from 0)",
    )


def test_a_metadata_only_note_measures_zero_with_or_without_a_trailing_newline(bench):
    """A closing `---` at end-of-file has no following `\\r?\\n` for the old pattern to match,
    so it went undetected and the whole metadata-only note counted as body."""
    with_newline = "---\ntype: task\nstream:\nblocked:\n---\n"
    without_newline = "---\ntype: task\nstream:\nblocked:\n---"
    bench.write("tasks/A.md", with_newline)
    bench.write("tasks/B.md", without_newline)
    git(bench.vault, "add", "-A")
    assert hook.staged_breaches(Repo(bench.vault), bench.config) == ()


def test_crlf_front_matter_is_still_stripped_to_its_body(bench):
    front = "---\r\ntype: task\r\nstream:\r\nblocked:\r\n---\r\n"
    body = "x" * 10_500
    bench.write("tasks/Oversized.md", front + body)
    git(bench.vault, "add", "-A")
    assert hook.staged_breaches(Repo(bench.vault), bench.config) == (
        "tasks/Oversized.md: 10500 chars over the 10000 cap (grew from 0)",
    )


def test_the_hook_body_quotes_paths_so_a_spaced_one_stays_a_single_argument():
    """Mutation caught: interpolating raw paths, which word-splits any path holding a space."""
    body = hook.hook_body(Path("/opt/vault tools"), "/usr/bin/py thon")
    exec_line = next(line for line in body.splitlines() if line.startswith("exec "))
    assert shlex.split(exec_line) == [
        "exec",
        "env",
        "PYTHONPATH=/opt/vault tools",
        "/usr/bin/py thon",
        "-m",
        "vaulttools.cli",
        "hook",
        "check",
    ]


def test_installing_over_an_existing_pre_commit_is_refused_without_force(bench):
    """Mutation caught: an install that silently overwrites a hook someone else put there."""
    hooks = bench.vault / ".git" / "hooks"
    hooks.mkdir(parents=True, exist_ok=True)
    (hooks / "pre-commit").write_text("#!/bin/sh\necho theirs\n", encoding="utf-8")
    with pytest.raises(VaultError, match="already exists"):
        hook.install(bench.vault)
    assert "echo theirs" in (hooks / "pre-commit").read_text(encoding="utf-8")
    hook.install(bench.vault, force=True)
    assert "vaulttools.cli hook check" in (hooks / "pre-commit").read_text(encoding="utf-8")


def test_installing_from_a_linked_worktree_gates_that_worktree_s_commits(bench, tmp_path):
    """Mutation caught: resolving `.git` by hand, which writes into a worktree git dir git never runs."""
    linked = tmp_path / "linked"
    git(bench.vault, "worktree", "add", "-q", "-b", "side", str(linked))
    installed = hook.install(linked)
    assert installed == (bench.vault / ".git" / "hooks" / "pre-commit").resolve()
    (linked / "tasks").mkdir(parents=True, exist_ok=True)
    (linked / "tasks" / "Oversized.md").write_text("z" * 10_500, encoding="utf-8")
    git(linked, "add", "-A")
    result = subprocess.run(
        ("git", "-C", str(linked), "commit", "-m", "bypass"), capture_output=True, text=True
    )
    assert result.returncode != 0
    output = result.stdout + result.stderr
    assert "tasks/Oversized.md: 10500 chars over the 10000 cap (grew from 0)" in output
