"""vault sync: GitLab MR state and branch existence set each stream's status; least-advanced wins."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from vaulttools import sync
from vaulttools.board import VaultError, read_frontmatter
from vaulttools.cli import main

from .conftest import git


def _status(bench, name, repos):
    return sync.stream_status(bench.vault, bench.config, bench.root, name, repos)


def _stub_mr(monkeypatch, value):
    """Replace the single GitLab seam with a fixed MR state, recording each call."""
    calls: list[str] = []

    def fake(clone, name):
        calls.append(clone.name)
        return value

    monkeypatch.setattr(sync, "_mr_state", fake)
    return calls


# --- per-repo derivation: the MR state seam is stubbed; branch existence is a real bench ref -----


def test_the_latest_mr_merged_with_the_branch_gone_reads_landed(bench, monkeypatch):
    """A stream lands via GitLab merge with delete-source-branch on: branch gone, latest MR merged."""
    bench.repo("alpha-repo", "alpha", merged=True, keep=False)
    _stub_mr(monkeypatch, sync.MR_MERGED)
    assert _status(bench, "alpha", ["alpha-repo"]) == sync.LANDED


def test_the_latest_mr_open_reads_in_progress(bench, monkeypatch):
    bench.repo("alpha-repo", "alpha", merged=False, keep=False)  # branch gone, but the MR is open
    _stub_mr(monkeypatch, sync.MR_OPENED)
    assert _status(bench, "alpha", ["alpha-repo"]) == sync.IN_PROGRESS


def test_a_branch_that_still_exists_reads_in_progress_without_querying_glab(bench, monkeypatch):
    """Branch existence is decided first, so a live stream never reaches the network."""
    bench.repo("alpha-repo", "alpha", merged=False, keep=True)
    calls = _stub_mr(monkeypatch, None)
    assert _status(bench, "alpha", ["alpha-repo"]) == sync.IN_PROGRESS
    assert calls == []


def test_no_mr_and_no_branch_reads_planned(bench, monkeypatch):
    bench.repo("planned-repo", "unrelated")  # carries stream/unrelated, never stream/alpha
    _stub_mr(monkeypatch, None)
    assert _status(bench, "alpha", ["planned-repo"]) == sync.PLANNED


def test_a_reused_branch_present_again_is_in_progress_not_landed_despite_an_old_merged_mr(
    bench, monkeypatch
):
    """The 'latest' rule: an old merged MR must not mark a newer, live incarnation landed."""
    bench.repo("alpha-repo", "alpha", merged=True, keep=True)  # the name is live again
    _stub_mr(monkeypatch, sync.MR_MERGED)  # the surfaced MR is the old, merged one
    assert _status(bench, "alpha", ["alpha-repo"]) == sync.IN_PROGRESS


def test_the_status_is_the_least_advanced_state_across_the_repos(bench, monkeypatch):
    bench.repo("landed-repo", "alpha", merged=True, keep=False)  # branch gone -> reaches the seam
    bench.repo("behind-repo", "unrelated")  # no stream/alpha here -> reaches the seam
    states = {"landed-repo": sync.MR_MERGED, "behind-repo": None}
    monkeypatch.setattr(sync, "_mr_state", lambda clone, name: states[clone.name])
    assert _status(bench, "alpha", ["landed-repo", "behind-repo"]) == sync.PLANNED


# --- origin classification: by hostname, not a substring of the whole URL -----------------------


def test_origin_host_classifies_by_hostname_not_by_a_substring_of_the_url():
    assert sync._origin_host("git@gitlab.example.org:mirrors/github.com/demo.git") == "gitlab.example.org"
    assert sync._origin_host("https://github.com/acme/x.git") == "github.com"
    assert sync._origin_host("ssh://git@github.com/acme/x.git") == "github.com"
    assert sync._origin_host("git@github.com:acme/x.git") == "github.com"


def test_origin_host_unwraps_a_bracketed_ipv6_scp_host():
    assert sync._origin_host("git@[2001:db8::1]:group/repo.git") == "2001:db8::1"


def test_a_gitlab_origin_with_github_in_its_path_is_not_rejected(bench, monkeypatch):
    """A GitLab host whose project path contains 'github.com' must not be mistaken for GitHub."""
    bench.repo("mirror-repo", "unrelated")  # no stream/alpha -> derivation reaches the seam
    clone = bench.root / "repos" / "mirror-repo"
    git(clone, "remote", "set-url", "origin", "git@gitlab.example.org:mirrors/github.com/demo.git")
    monkeypatch.setattr(sync, "_run_glab", lambda c, n: "[]")
    assert sync._mr_state(clone, "alpha") is None


# --- _run_glab: exercised through a subprocess double returning real (returncode, stdout) --------


def test_run_glab_sends_the_expected_argv_and_cwd(monkeypatch):
    seen: dict[str, object] = {}

    def fake_run(argv, **kwargs):
        seen["argv"] = argv
        seen["cwd"] = kwargs["cwd"]
        return subprocess.CompletedProcess(argv, 0, stdout="[]", stderr="")

    monkeypatch.setattr(sync.subprocess, "run", fake_run)
    clone = Path("/root/repos/alpha-repo")
    assert sync._run_glab(clone, "alpha") == "[]"
    assert seen["argv"] == (
        "glab", "mr", "list", "--source-branch", "stream/alpha", "--all", "--output", "json",
    )
    assert seen["cwd"] == clone


def test_run_glab_raises_a_named_vaulterror_on_a_nonzero_exit(monkeypatch):
    def fake_run(argv, **kwargs):
        return subprocess.CompletedProcess(argv, 1, stdout="", stderr="not authenticated")

    monkeypatch.setattr(sync.subprocess, "run", fake_run)
    with pytest.raises(VaultError, match="alpha-repo: glab mr list failed: not authenticated"):
        sync._run_glab(Path("/root/repos/alpha-repo"), "alpha")


def test_run_glab_wraps_a_launch_failure_as_a_named_vaulterror(monkeypatch):
    def fake_run(argv, **kwargs):
        raise FileNotFoundError("glab")

    monkeypatch.setattr(sync.subprocess, "run", fake_run)
    with pytest.raises(VaultError, match="alpha-repo: could not launch glab"):
        sync._run_glab(Path("/root/repos/alpha-repo"), "alpha")


# --- _latest_state: highest iid wins in any order; empty/undecodable is unreliable, not "no MRs" -


def test_latest_state_selects_the_highest_iid_in_either_order():
    """`_latest_state` reads only `iid` and `state`; the highest iid is the latest incarnation."""
    ascending = json.dumps([{"iid": 3, "state": "merged"}, {"iid": 7, "state": "opened"}])
    descending = json.dumps([{"iid": 7, "state": "opened"}, {"iid": 3, "state": "merged"}])
    assert sync._latest_state(ascending, "r") == sync.MR_OPENED
    assert sync._latest_state(descending, "r") == sync.MR_OPENED


def test_latest_state_is_none_for_a_valid_empty_list_but_raises_for_empty_or_undecodable_output():
    assert sync._latest_state("[]", "r") is None
    with pytest.raises(VaultError, match="empty response"):
        sync._latest_state("   \n", "r")
    with pytest.raises(VaultError, match="undecodable JSON"):
        sync._latest_state("{not json", "r")
    with pytest.raises(VaultError, match="non-list"):
        sync._latest_state("null", "r")


def test_latest_state_fails_closed_on_a_malformed_record_never_keyerror_or_silent_status():
    """A record missing an integer iid or a known state is unreliable, not silently 'no MRs'."""
    assert sync._latest_state("[]", "r") is None  # a valid empty list still means "no MRs"
    with pytest.raises(VaultError, match="malformed MR record"):
        sync._latest_state("[{}]", "r")  # no iid, no state — never a KeyError
    with pytest.raises(VaultError, match="malformed MR record"):
        sync._latest_state('[{"iid": 1, "state": null}]', "r")  # null state
    with pytest.raises(VaultError, match="malformed MR record"):
        sync._latest_state('[{"iid": "x", "state": "merged"}]', "r")  # non-int iid
    with pytest.raises(VaultError, match="malformed MR record"):
        sync._latest_state('[{"iid": 1, "state": "draft"}]', "r")  # unknown state
    with pytest.raises(VaultError, match="malformed MR record"):
        sync._latest_state('["not-a-dict"]', "r")  # non-dict entry
    with pytest.raises(VaultError, match="malformed MR record"):
        sync._latest_state('[{"iid": 1, "state": []}]', "r")  # unhashable (list) state
    with pytest.raises(VaultError, match="malformed MR record"):
        sync._latest_state('[{"iid": 1, "state": {"x": 1}}]', "r")  # object-valued state


# --- loud refusals surface, never a silent planned ----------------------------------------------


def test_a_non_gitlab_origin_raises_loud_and_names_the_repo(bench):
    """A GitHub origin can never be silently mistaken for an unstarted (planned) stream."""
    bench.repo("gh-repo", "unrelated")  # no stream/alpha, so derivation reaches the seam
    clone = bench.root / "repos" / "gh-repo"
    git(clone, "remote", "set-url", "origin", "https://github.com/acme/gh-repo.git")
    with pytest.raises(VaultError, match="gh-repo"):
        _status(bench, "alpha", ["gh-repo"])


def test_a_glab_failure_propagates_loud_rather_than_reading_planned(bench, monkeypatch):
    """A failed query surfaces through the fold as a loud refusal, not a silent planned."""
    bench.repo("gl-repo", "unrelated")  # branch absent -> derivation reaches the seam

    def boom(clone, name):
        raise VaultError(f"{clone.name}: glab mr list failed: not authenticated")

    monkeypatch.setattr(sync, "_mr_state", boom)
    with pytest.raises(VaultError, match="glab mr list failed"):
        _status(bench, "alpha", ["gl-repo"])


# --- with_status: surgical front-matter write --------------------------------------------------


def test_with_status_refuses_a_note_that_has_no_front_matter(bench):
    with pytest.raises(VaultError, match="no front matter"):
        sync.with_status("a body with no front matter\n", sync.LANDED)


def test_with_status_preserves_a_crlf_note_line_separator(bench):
    text = "---\r\ntype: stream\r\nstream: a\r\nrepos: [r]\r\nblocked:\r\n---\r\nbody\r\n"
    expected = (
        "---\r\ntype: stream\r\nstream: a\r\nrepos: [r]\r\nblocked:\r\n"
        "status: landed\r\n---\r\nbody\r\n"
    )
    assert sync.with_status(text, sync.LANDED) == expected


# --- run: preflight -> commit -> postflight ---------------------------------------------------


def test_a_stream_with_no_repos_is_skipped_and_reported_not_crashed(bench):
    bench.write("tasks/Meta.md", "---\ntype: stream\nstream: meta\nrepos: []\nblocked:\n---\nbody\n")
    report = sync.run(bench.vault, bench.config, bench.root)
    assert any("Meta.md" in line and "no repos" in line for line in report.notices)
    assert "status:" not in (bench.vault / "tasks" / "Meta.md").read_text(encoding="utf-8")


def test_a_stream_note_with_no_stream_value_is_reported_and_never_aborts_the_run(bench, monkeypatch):
    tip = bench.repo("alpha-repo", "alpha", merged=True, keep=False)  # landed shape
    bench.stream("alpha", "Alpha stream", tip, "alpha-repo")  # well-formed neighbour
    _stub_mr(monkeypatch, sync.MR_MERGED)
    bench.write(
        "tasks/Malformed.md", "---\ntype: stream\nstream:\nrepos: [alpha-repo]\nblocked:\n---\nbody\n"
    )
    report = sync.run(bench.vault, bench.config, bench.root)
    assert any("Malformed.md" in line and "no stream:" in line for line in report.notices)
    assert read_frontmatter(bench.vault / "tasks" / "Alpha stream.md")["status"] == sync.LANDED
    assert "status:" not in (bench.vault / "tasks" / "Malformed.md").read_text(encoding="utf-8")


def test_remote_mode_refuses_before_any_write_when_a_fetch_fails(bench):
    """Preflight aborts on a fetch failure with no partial write."""
    tip = bench.repo("alpha-repo", "alpha", merged=False, keep=True)
    bench.stream("alpha", "Alpha stream", tip, "alpha-repo")
    note = bench.vault / "tasks" / "Alpha stream.md"
    (bench.remotes / "alpha-repo.git").rename(bench.remotes / "alpha-repo.git.moved")
    with pytest.raises(VaultError, match="fetch failed"):
        sync.run(bench.vault, bench.config, bench.root, local=False)
    assert "status:" not in note.read_text(encoding="utf-8")


def test_local_run_writes_no_status_and_leaves_a_committed_note_byte_for_byte(bench, monkeypatch):
    """Offline, sync cannot tell landed from planned, so it must persist nothing over a correct value."""
    tip = bench.repo("alpha-repo", "alpha", merged=True, keep=False)  # landed shape
    bench.stream("alpha", "Alpha stream", tip, "alpha-repo")
    note = bench.vault / "tasks" / "Alpha stream.md"
    _stub_mr(monkeypatch, sync.MR_MERGED)
    sync.run(bench.vault, bench.config, bench.root)  # a full run writes the correct landed
    landed_bytes = note.read_text(encoding="utf-8")
    assert read_frontmatter(note)["status"] == sync.LANDED

    monkeypatch.setattr(sync, "_mr_state", lambda c, n: pytest.fail("glab must not run under --local"))
    monkeypatch.setattr(sync, "_fetch_all", lambda *a, **k: pytest.fail("--local must not fetch"))
    sync.run(bench.vault, bench.config, bench.root, local=True)
    assert note.read_text(encoding="utf-8") == landed_bytes


def test_sync_writes_the_status_and_then_reproduces_the_note_byte_for_byte(bench, monkeypatch):
    tip = bench.repo("alpha-repo", "alpha", merged=True, keep=False)
    bench.stream("alpha", "Alpha stream", tip, "alpha-repo")
    _stub_mr(monkeypatch, sync.MR_MERGED)
    note = bench.vault / "tasks" / "Alpha stream.md"

    sync.run(bench.vault, bench.config, bench.root)
    first = note.read_text(encoding="utf-8")
    assert read_frontmatter(note)["status"] == sync.LANDED
    assert first.count("status:") == 1
    assert "Owner: example" in first  # the body is left untouched

    sync.run(bench.vault, bench.config, bench.root)
    assert note.read_text(encoding="utf-8") == first


def test_sync_updates_a_stale_status_in_place_without_duplicating_or_reordering_keys(bench, monkeypatch):
    tip = bench.repo("alpha-repo", "alpha", merged=True, keep=False)
    bench.stream("alpha", "Alpha stream", tip, "alpha-repo")
    _stub_mr(monkeypatch, sync.MR_MERGED)
    note = bench.vault / "tasks" / "Alpha stream.md"
    note.write_text(
        note.read_text(encoding="utf-8").replace("blocked:\n", "blocked:\nstatus: planned\n"),
        encoding="utf-8",
    )
    sync.run(bench.vault, bench.config, bench.root)
    front = read_frontmatter(note)
    assert front["status"] == sync.LANDED
    assert note.read_text(encoding="utf-8").count("status:") == 1
    assert list(front).index("blocked") < list(front).index("status")


def test_the_sync_command_prints_hygiene_writes_in_default_and_leaves_notes_untouched_under_local(
    bench, monkeypatch, capsys
):
    tip = bench.repo("alpha-repo", "alpha", merged=True, keep=False)  # landed shape
    bench.stream("alpha", "Alpha stream", tip, "alpha-repo")
    _stub_mr(monkeypatch, sync.MR_MERGED)
    note = bench.vault / "tasks" / "Alpha stream.md"
    assert main(["--vault", str(bench.vault), "sync", "--root", str(bench.root)]) == 0
    assert "canonical clones" in capsys.readouterr().out
    landed_bytes = note.read_text(encoding="utf-8")
    assert read_frontmatter(note)["status"] == sync.LANDED
    # --local runs hygiene but writes no status, so the committed landed note is left untouched
    assert main(["--vault", str(bench.vault), "sync", "--root", str(bench.root), "--local"]) == 0
    assert note.read_text(encoding="utf-8") == landed_bytes
