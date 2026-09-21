"""Hygiene: blocking rows refuse the action, report rows never do."""

from __future__ import annotations

from vaulttools import hygiene

from .conftest import VAULT_TOML, git

DAY = 86400


def _rows(bench, now=None):
    return {row.name: row for row in hygiene.check(bench.vault, bench.config, bench.root, now=now)}


def _live_stream(bench, merged=False, column="in progress"):
    tip = bench.repo("alpha-repo", "alpha", merged=merged)
    bench.write(
        "tasks/Alpha stream.md",
        f"---\ntype: stream\nstream: alpha\nrepos: [alpha-repo]\nblocked:\n---\n"
        f"Merge evidence:\n- alpha-repo: {tip} -> origin/main\n",
    )
    bench.card("Alpha stream", column)
    bench.publish("bench: live stream")
    return tip


def test_a_clean_root_produces_no_blocking_finding(bench):
    rows = hygiene.check(bench.vault, bench.config, bench.root)
    assert not hygiene.blocked(rows)
    assert "ok  worktrees" in hygiene.render(rows)


def test_a_worktree_without_a_live_stream_card_blocks(bench):
    _live_stream(bench)
    clone = bench.root / "repos" / "alpha-repo"
    git(clone, "worktree", "add", "-q", "-b", "experiment", str(bench.root / "work" / "loose"), "main")
    rows = _rows(bench)
    assert hygiene.blocked(tuple(rows.values()))
    assert any("experiment" in finding for finding in rows["worktrees"].findings)


def test_a_worktree_on_a_live_stream_branch_is_not_a_leftover(bench):
    _live_stream(bench)
    clone = bench.root / "repos" / "alpha-repo"
    git(clone, "worktree", "add", "-q", "-b", "lane/alpha/build", str(bench.root / "work" / "lane"), "main")
    assert _rows(bench)["worktrees"].findings == ()


def test_an_edited_canonical_clone_blocks(bench):
    _live_stream(bench)
    (bench.root / "repos" / "alpha-repo" / "README.md").write_text("edited\n", encoding="utf-8")
    assert _rows(bench)["canonical clones"].findings


def test_scratch_left_under_temp_blocks(bench):
    (bench.vault / "temp").mkdir()
    (bench.vault / "temp" / "probe.log").write_text("noise\n", encoding="utf-8")
    rows = _rows(bench)
    assert rows["temp"].findings == ("temp/probe.log",)
    assert hygiene.blocked(tuple(rows.values()))


def test_a_live_stream_card_without_its_branch_on_any_remote_blocks(bench):
    _live_stream(bench)
    rows = _rows(bench)
    assert rows["stream branches"].findings
    assert "stream/alpha is on no remote" in rows["stream branches"].findings[0]


def test_a_backlog_stream_has_no_branch_by_design_and_does_not_block(bench):
    """Doctrine (AGENTS.md §5): the branch publishes on entry to `open`, so a `backlog`
    stream carries none yet — the branch check skips it, though it still counts as a
    live stream for membership and caps."""
    _live_stream(bench, column="backlog")
    rows = _rows(bench)
    assert rows["stream branches"].findings == ()
    assert not hygiene.blocked(tuple(rows.values()))


def test_an_open_stream_without_its_branch_on_any_remote_blocks(bench):
    _live_stream(bench, column="open")
    rows = _rows(bench)
    assert rows["stream branches"].findings
    assert "stream/alpha is on no remote" in rows["stream branches"].findings[0]


def test_a_note_over_its_cap_reports_but_never_blocks(bench):
    """The hygiene row lists the over-cap backlog; only the pre-commit hook ratchets it."""
    bench.write("tasks/Oversized.md", "x" * 10_001)
    bench.publish("bench: oversized note")
    rows = _rows(bench)
    assert rows["note caps"].findings and not rows["note caps"].blocking
    assert not hygiene.blocked(tuple(rows.values()))


def test_promotion_age_and_backlog_age_are_reports_not_refusals(bench):
    tip = bench.repo("alpha-repo", "alpha")
    bench.stream("alpha", "Alpha stream", tip, "alpha-repo")
    bench.write("tasks/Loose.md", "---\ntype: task\nstream:\nrepos: []\nblocked:\n---\nidle\n")
    bench.publish("bench: loose backlog note")
    later = float(git(bench.vault, "log", "-1", "--format=%ct").strip()) + 200 * DAY
    rows = _rows(bench, now=later)
    assert rows["promotion"].findings and not rows["promotion"].blocking
    assert rows["backlog age"].findings and not rows["backlog age"].blocking
    assert not hygiene.blocked(tuple(rows.values()))


def test_the_promotion_bound_is_reported_when_too_many_cards_sit_there(bench):
    for index in range(6):
        bench.write(
            f"tasks/Stream {index}.md",
            f"---\ntype: stream\nstream: s{index}\nrepos: []\nblocked:\n---\n",
        )
        bench.card(f"Stream {index}", "promotion")
    bench.publish("bench: six promotion cards")
    findings = _rows(bench)["promotion"].findings
    assert any("over the bound of 5" in finding for finding in findings)


def test_a_stream_branch_on_only_one_of_two_repositories_blocks(bench):
    """Mutation caught: accepting the branch on any listed repo, so a half-published stream passes."""
    bench.repo("alpha-repo", "alpha", merged=False, keep=True)
    bench.repo("beta-repo", "alpha", merged=False)
    bench.write(
        "tasks/Alpha stream.md",
        "---\ntype: stream\nstream: alpha\nrepos: [alpha-repo, beta-repo]\nblocked:\n---\n",
    )
    bench.card("Alpha stream", "in progress")
    bench.publish("bench: a two-repo stream")
    assert _rows(bench)["stream branches"].findings == (
        "Alpha stream: stream/alpha is on no remote of beta-repo",
    )


def test_a_merge_worktree_is_exempt_only_while_the_config_names_its_prefix(bench):
    """Mutation caught: a hard-coded `merge-` exemption no deployment can see or retarget."""
    _live_stream(bench)
    clone = bench.root / "repos" / "alpha-repo"
    git(clone, "worktree", "add", "-q", "-b", "merge-alpha", str(bench.root / "work" / "merge"), "main")
    assert _rows(bench)["worktrees"].findings == ()
    bench.write("vault.toml", 'merge_branch_prefix = "land-"\n' + VAULT_TOML)
    assert any("merge-alpha" in finding for finding in _rows(bench)["worktrees"].findings)
