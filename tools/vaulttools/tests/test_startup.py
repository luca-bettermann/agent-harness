"""Real Git journeys for the bounded mounted-repository startup kernel."""

from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path

import pytest

from vaulttools import startup
from vaulttools.board import Config, Scope, VaultError
from vaulttools.cli import main

from .conftest import git


def _configure(repo: Path) -> None:
    for key, value in (
        ("user.email", "startup@example.com"),
        ("user.name", "Startup"),
        ("commit.gpgsign", "false"),
    ):
        git(repo, "config", key, value)


def _repository(tmp_path: Path, name: str) -> tuple[Path, Path, Path]:
    remote = tmp_path / "remotes" / f"{name}.git"
    seed = tmp_path / "seeds" / name
    clone = tmp_path / "vault" / name
    remote.parent.mkdir(parents=True, exist_ok=True)
    seed.mkdir(parents=True, exist_ok=True)
    subprocess.run(("git", "init", "-q", "--bare", str(remote)), check=True)
    subprocess.run(("git", "init", "-q", "-b", "main", str(seed)), check=True)
    _configure(seed)
    (seed / ".gitignore").write_text("ignored/\n", encoding="utf-8")
    (seed / "base.txt").write_text("base\n", encoding="utf-8")
    git(seed, "add", "-A")
    git(seed, "commit", "-q", "-m", "base")
    git(seed, "remote", "add", "origin", str(remote))
    git(seed, "push", "-q", "-u", "origin", "main")
    subprocess.run(
        ("git", "clone", "-q", "--branch", "main", str(remote), str(clone)),
        check=True,
        env={**os.environ, "GIT_LFS_SKIP_SMUDGE": "1"},
    )
    _configure(clone)
    return seed, remote, clone


def _publish(seed: Path, relative: str, content: str) -> str:
    path = seed / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    git(seed, "add", "-A")
    git(seed, "commit", "-q", "-m", relative)
    git(seed, "push", "-q", "origin", "main")
    return git(seed, "rev-parse", "HEAD").strip()


def _pull_without_smudge(clone: Path) -> None:
    subprocess.run(
        ("git", "-C", str(clone), "pull", "-q", "--ff-only"),
        check=True,
        env={**os.environ, "GIT_LFS_SKIP_SMUDGE": "1"},
    )


def _scope(name: str, path: Path, vault: Path, *, pin: str | None = None) -> Scope:
    relative = os.path.relpath(path, vault)
    return Scope(name, relative, pin=pin) if pin else Scope(name, relative, branch="main")


def test_state_model_advances_only_the_clean_configured_branch(tmp_path):
    vault = tmp_path / "vault"
    vault.mkdir()
    scopes: list[Scope] = []
    expected: dict[str, tuple[str, str]] = {}
    originals: dict[str, str] = {}

    seed, _, clone = _repository(tmp_path, "behind")
    target = _publish(seed, "remote.txt", "remote\n")
    scopes.append(_scope("behind", clone, vault))
    expected["behind"] = ("behind", "advanced")

    seed, _, clone = _repository(tmp_path, "current")
    scopes.append(_scope("current", clone, vault))
    expected["current"] = ("current", "current")

    seed, _, clone = _repository(tmp_path, "dirty")
    _publish(seed, "remote.txt", "remote\n")
    (clone / "base.txt").write_text("private edit\n", encoding="utf-8")
    git(clone, "config", "--replace-all", "remote.origin.fetch", "+refs/heads/*:refs/heads/fetched/*")
    originals["dirty"] = git(clone, "rev-parse", "HEAD").strip()
    scopes.append(_scope("dirty", clone, vault))
    expected["dirty"] = ("dirty", "preserved")

    seed, _, clone = _repository(tmp_path, "untracked")
    _publish(seed, "remote.txt", "remote\n")
    (clone / "untracked.txt").write_text("private\n", encoding="utf-8")
    originals["untracked"] = git(clone, "rev-parse", "HEAD").strip()
    scopes.append(_scope("untracked", clone, vault))
    expected["untracked"] = ("dirty", "preserved")

    seed, _, clone = _repository(tmp_path, "ahead")
    (clone / "local.txt").write_text("local\n", encoding="utf-8")
    git(clone, "add", "-A")
    git(clone, "commit", "-q", "-m", "local")
    originals["ahead"] = git(clone, "rev-parse", "HEAD").strip()
    scopes.append(_scope("ahead", clone, vault))
    expected["ahead"] = ("ahead", "preserved")

    seed, _, clone = _repository(tmp_path, "diverged")
    _publish(seed, "remote.txt", "remote\n")
    (clone / "local.txt").write_text("local\n", encoding="utf-8")
    git(clone, "add", "-A")
    git(clone, "commit", "-q", "-m", "local")
    originals["diverged"] = git(clone, "rev-parse", "HEAD").strip()
    scopes.append(_scope("diverged", clone, vault))
    expected["diverged"] = ("diverged", "preserved")

    seed, _, clone = _repository(tmp_path, "other")
    _publish(seed, "remote.txt", "remote\n")
    git(clone, "checkout", "-q", "-b", "contribution")
    originals["other"] = git(clone, "rev-parse", "HEAD").strip()
    scopes.append(_scope("other", clone, vault))
    expected["other"] = ("other-branch", "preserved")

    seed, _, clone = _repository(tmp_path, "collision")
    incoming = seed / "ignored" / "local.txt"
    incoming.parent.mkdir()
    incoming.write_text("incoming\n", encoding="utf-8")
    git(seed, "add", "-f", "ignored/local.txt")
    git(seed, "commit", "-q", "-m", "incoming ignored path")
    git(seed, "push", "-q", "origin", "main")
    occupant = clone / "ignored" / "local.txt"
    occupant.parent.mkdir()
    occupant.write_text("keep me\n", encoding="utf-8")
    originals["collision"] = git(clone, "rev-parse", "HEAD").strip()
    scopes.append(_scope("collision", clone, vault))
    expected["collision"] = ("local-path-blocked", "preserved")

    seed, _, clone = _repository(tmp_path, "pin-match")
    pin = git(clone, "rev-parse", "HEAD").strip()
    _publish(seed, "later.txt", "later\n")
    scopes.append(_scope("pin-match", clone, vault, pin=pin))
    expected["pin-match"] = ("pin-match", "current")

    seed, _, clone = _repository(tmp_path, "pin-mismatch")
    old_pin = git(clone, "rev-parse", "HEAD").strip()
    new_pin = _publish(seed, "later.txt", "later\n")
    originals["pin-mismatch"] = old_pin
    scopes.append(_scope("pin-mismatch", clone, vault, pin=new_pin))
    expected["pin-mismatch"] = ("pin-mismatch", "preserved")

    seed, _, clone = _repository(tmp_path, "operation")
    _publish(seed, "remote.txt", "remote\n")
    merge_head = Path(git(clone, "rev-parse", "--git-path", "MERGE_HEAD").strip())
    if not merge_head.is_absolute():
        merge_head = clone / merge_head
    merge_head.write_text(git(clone, "rev-parse", "HEAD"), encoding="utf-8")
    originals["operation"] = git(clone, "rev-parse", "HEAD").strip()
    scopes.append(_scope("operation", clone, vault))
    expected["operation"] = ("operation-active", "preserved")

    report = startup.run(vault, Config(scopes=tuple(scopes)), timeout=5, deadline=60)
    rows = {row.name: row for row in report.rows}

    assert report.complete
    assert {name: (rows[name].relation, rows[name].refresh) for name in expected} == expected
    assert rows["behind"].final_head == target
    assert (vault / "collision" / "ignored" / "local.txt").read_text() == "keep me\n"
    for name, original in originals.items():
        assert git(vault / name, "rev-parse", "HEAD").strip() == original
    assert (
        subprocess.run(
            ("git", "-C", str(vault / "dirty"), "show-ref", "--verify", "refs/heads/fetched/main"),
            check=False,
            capture_output=True,
        ).returncode
        != 0
    )
    assert startup.render(report).startswith("REPORT COMPLETED — ATTENTION")


def test_active_mutation_hook_preserves_checkout_without_fetch(tmp_path):
    vault = tmp_path / "vault"
    vault.mkdir()
    seed, _, clone = _repository(tmp_path, "hooked")
    _publish(seed, "remote.txt", "remote\n")
    hook = Path(git(clone, "rev-parse", "--git-path", "hooks/reference-transaction").strip())
    if not hook.is_absolute():
        hook = clone / hook
    hook.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    hook.chmod(0o755)
    before = git(clone, "rev-parse", "refs/remotes/origin/main").strip()

    report = startup.run(vault, Config(scopes=(_scope("hooked", clone, vault),)))
    row = report.rows[0]

    assert (row.relation, row.refresh) == ("hook-blocked", "preserved")
    assert git(clone, "rev-parse", "refs/remotes/origin/main").strip() == before


def test_spoofed_lfs_comment_is_an_unknown_active_hook_and_blocks_fetch(tmp_path):
    vault = tmp_path / "vault"
    vault.mkdir()
    seed, _, clone = _repository(tmp_path, "spoofed-hook")
    _publish(seed, "remote.txt", "remote\n")
    hook = Path(git(clone, "rev-parse", "--git-path", "hooks/post-merge").strip())
    if not hook.is_absolute():
        hook = clone / hook
    hook.write_text("#!/bin/sh\n# git lfs post-merge\nexit 99\n", encoding="utf-8")
    hook.chmod(0o755)
    before = git(clone, "rev-parse", "refs/remotes/origin/main").strip()

    report = startup.run(vault, Config(scopes=(_scope("spoofed", clone, vault),)))
    row = report.rows[0]

    assert (row.relation, row.refresh) == ("hook-blocked", "preserved")
    assert git(clone, "rev-parse", "refs/remotes/origin/main").strip() == before


def test_exact_git_lfs_generated_post_merge_hook_keeps_fast_forward_supported(tmp_path):
    vault = tmp_path / "vault"
    vault.mkdir()
    seed, _, clone = _repository(tmp_path, "lfs-hook")
    target = _publish(seed, "remote.txt", "remote\n")
    git(clone, "lfs", "install", "--local")

    report = startup.run(vault, Config(scopes=(_scope("lfs", clone, vault),)))
    row = report.rows[0]

    assert row.refresh == "advanced"
    assert row.final_head == target


def test_captured_target_does_not_move_when_origin_advances_mid_run(tmp_path, monkeypatch):
    vault = tmp_path / "vault"
    vault.mkdir()
    seed, _, clone = _repository(tmp_path, "moving")
    captured = _publish(seed, "first.txt", "first\n")
    original = startup._incoming_blockers
    moved = False

    def move_after_capture(repo, head, target, budget):
        nonlocal moved
        if not moved:
            moved = True
            _publish(seed, "second.txt", "second\n")
        return original(repo, head, target, budget)

    monkeypatch.setattr(startup, "_incoming_blockers", move_after_capture)
    report = startup.run(vault, Config(scopes=(_scope("moving", clone, vault),)))

    assert report.rows[0].target == captured
    assert git(clone, "rev-parse", "HEAD").strip() == captured
    assert not (clone / "second.txt").exists()


def test_live_collision_recheck_catches_an_ignored_file_created_after_snapshot(tmp_path, monkeypatch):
    vault = tmp_path / "vault"
    vault.mkdir()
    seed, _, clone = _repository(tmp_path, "late-collision")
    incoming = seed / "ignored" / "late.txt"
    incoming.parent.mkdir()
    incoming.write_text("incoming\n", encoding="utf-8")
    git(seed, "add", "-f", "ignored/late.txt")
    git(seed, "commit", "-q", "-m", "incoming")
    git(seed, "push", "-q", "origin", "main")
    original_head = git(clone, "rev-parse", "HEAD").strip()
    original = startup._incoming_blockers
    calls = 0

    def create_on_recheck(repo, head, target, budget):
        nonlocal calls
        calls += 1
        if calls == 2:
            occupant = repo.root / "ignored" / "late.txt"
            occupant.parent.mkdir()
            occupant.write_text("appeared late\n", encoding="utf-8")
        return original(repo, head, target, budget)

    monkeypatch.setattr(startup, "_incoming_blockers", create_on_recheck)
    report = startup.run(vault, Config(scopes=(_scope("late", clone, vault),)))

    assert report.rows[0].relation == "local-path-blocked"
    assert git(clone, "rev-parse", "HEAD").strip() == original_head
    assert (clone / "ignored" / "late.txt").read_text() == "appeared late\n"


def test_a_changed_populated_submodule_is_preserved_without_recursive_fetch(tmp_path):
    vault = tmp_path / "vault"
    vault.mkdir()
    sub_remote = tmp_path / "remotes" / "sub.git"
    sub_seed = tmp_path / "seeds" / "sub"
    sub_seed.mkdir(parents=True)
    subprocess.run(("git", "init", "-q", "--bare", str(sub_remote)), check=True)
    subprocess.run(("git", "init", "-q", "-b", "main", str(sub_seed)), check=True)
    _configure(sub_seed)
    (sub_seed / "version.txt").write_text("one\n", encoding="utf-8")
    git(sub_seed, "add", "-A")
    git(sub_seed, "commit", "-q", "-m", "one")
    git(sub_seed, "remote", "add", "origin", str(sub_remote))
    git(sub_seed, "push", "-q", "-u", "origin", "main")
    git(sub_remote, "symbolic-ref", "HEAD", "refs/heads/main")

    seed, _, clone = _repository(tmp_path, "super")
    subprocess.run(
        (
            "git",
            "-c",
            "protocol.file.allow=always",
            "-C",
            str(seed),
            "submodule",
            "add",
            "-q",
            str(sub_remote),
            "module",
        ),
        check=True,
    )
    git(seed, "add", "-A")
    git(seed, "commit", "-q", "-m", "submodule")
    git(seed, "push", "-q", "origin", "main")
    _pull_without_smudge(clone)
    subprocess.run(
        (
            "git",
            "-c",
            "protocol.file.allow=always",
            "-C",
            str(clone),
            "submodule",
            "update",
            "--init",
        ),
        check=True,
    )
    original_head = git(clone, "rev-parse", "HEAD").strip()

    (sub_seed / "version.txt").write_text("two\n", encoding="utf-8")
    git(sub_seed, "add", "-A")
    git(sub_seed, "commit", "-q", "-m", "two")
    git(sub_seed, "push", "-q", "origin", "main")
    subprocess.run(
        (
            "git",
            "-c",
            "protocol.file.allow=always",
            "-C",
            str(seed / "module"),
            "pull",
            "-q",
            "--ff-only",
        ),
        check=True,
    )
    git(seed, "add", "module")
    git(seed, "commit", "-q", "-m", "advance submodule")
    git(seed, "push", "-q", "origin", "main")

    report = startup.run(vault, Config(scopes=(_scope("super", clone, vault),)))

    assert report.rows[0].relation == "submodule-blocked"
    assert git(clone, "rev-parse", "HEAD").strip() == original_head
    assert (clone / "module" / "version.txt").read_text() == "one\n"


def test_the_vault_checkout_is_processed_last_and_both_effects_land(tmp_path):
    seed, _, vault = _repository(tmp_path, "self")
    other_seed, _, other = _repository(tmp_path, "child")
    self_target = _publish(seed, "self-marker.txt", "self\n")
    other_target = _publish(other_seed, "other-marker.txt", "other\n")
    config = Config(
        scopes=(
            _scope("self", vault, vault),
            _scope("other", other, vault),
        )
    )

    report = startup.run(vault, config)

    assert [row.name for row in report.rows] == ["other", "self"]
    assert git(other, "rev-parse", "HEAD").strip() == other_target
    assert git(vault, "rev-parse", "HEAD").strip() == self_target
    assert (other / "other-marker.txt").read_text() == "other\n"
    assert (vault / "self-marker.txt").read_text() == "self\n"


def test_duplicate_worktree_identity_fails_before_remote_fetch(tmp_path):
    vault = tmp_path / "vault"
    vault.mkdir()
    _, _, clone = _repository(tmp_path, "duplicate")
    before = git(clone, "show-ref").strip()
    config = Config(
        scopes=(
            _scope("first", clone, vault),
            Scope("alias", os.path.relpath(clone / ".", vault), branch="main"),
        )
    )

    with pytest.raises(VaultError, match="same worktree"):
        startup.run(vault, config)
    assert git(clone, "show-ref").strip() == before


def test_only_origin_is_contacted_and_the_upstream_upload_trap_is_live(tmp_path, monkeypatch):
    vault = tmp_path / "vault"
    vault.mkdir()
    _, _, clone = _repository(tmp_path, "origin-only")
    marker = tmp_path / "upstream-fetch-attempted"
    trap = tmp_path / "upload-trap"
    trap.write_text(f"#!/bin/sh\ntouch '{marker}'\nexit 1\n", encoding="utf-8")
    trap.chmod(0o755)
    git(clone, "remote", "add", "upstream", f"ext::{trap}")
    monkeypatch.setenv("GIT_ALLOW_PROTOCOL", "file:ext")

    subprocess.run(
        ("git", "-C", str(clone), "fetch", "upstream"),
        check=False,
        capture_output=True,
        env=os.environ,
    )
    assert marker.is_file()
    marker.unlink()

    report = startup.run(vault, Config(scopes=(_scope("repo", clone, vault),)))
    assert report.complete
    assert not marker.exists()


def test_real_lfs_pointer_is_cached_and_hydrated_only_for_an_exact_clean_head(tmp_path):
    vault = tmp_path / "vault"
    vault.mkdir()
    seed, _, clone = _repository(tmp_path, "lfs-clean")
    git(seed, "lfs", "install", "--local")
    (seed / ".gitattributes").write_text(
        "[attr]asset filter=lfs diff=lfs merge=lfs -text\n"
        "assets/** asset\n"
        "assets/plain.bin -filter -diff -merge text\n",
        encoding="utf-8",
    )
    payload = b"payload-from-lfs\x00\x01"
    (seed / "assets").mkdir()
    (seed / "assets" / "model.bin").write_bytes(payload)
    (seed / "assets" / "plain.bin").write_bytes(b"plain\n")
    git(seed, "add", "-A")
    git(seed, "commit", "-q", "-m", "lfs payload")
    git(seed, "push", "-q", "origin", "main")
    target = git(seed, "rev-parse", "HEAD").strip()

    assert not (clone / "assets" / "model.bin").exists()

    report = startup.run(vault, Config(scopes=(_scope("clean", clone, vault),)))
    row = report.rows[0]
    assert row.refresh == "advanced"
    assert (row.lfs_remote, row.lfs_cache, row.assets) == (
        "fetched",
        "complete",
        "readable",
    )
    assert (clone / "assets" / "model.bin").read_bytes() == payload
    assert (clone / "assets" / "plain.bin").read_bytes() == b"plain\n"

    pin_clone = tmp_path / "vault" / "lfs-pin"
    subprocess.run(
        ("git", "clone", "-q", "--branch", "main", str(tmp_path / "remotes/lfs-clean.git"), str(pin_clone)),
        check=True,
        env={**os.environ, "GIT_LFS_SKIP_SMUDGE": "1"},
    )
    _configure(pin_clone)
    pin_report = startup.run(
        vault,
        Config(scopes=(_scope("pin", pin_clone, vault, pin=target),)),
    )
    assert pin_report.rows[0].assets == "readable"
    assert (pin_clone / "assets" / "model.bin").read_bytes() == payload


def test_dirty_lfs_checkout_may_cache_but_never_hydrates(tmp_path):
    vault = tmp_path / "vault"
    vault.mkdir()
    seed, _, clone = _repository(tmp_path, "lfs-dirty")
    git(seed, "lfs", "install", "--local")
    git(seed, "lfs", "track", "*.bin")
    (seed / "model.bin").write_bytes(b"real-payload")
    git(seed, "add", "-A")
    git(seed, "commit", "-q", "-m", "lfs")
    git(seed, "push", "-q", "origin", "main")
    _pull_without_smudge(clone)
    pointer = (clone / "model.bin").read_bytes()
    (clone / "private.txt").write_text("private\n", encoding="utf-8")

    report = startup.run(vault, Config(scopes=(_scope("dirty", clone, vault),)))
    row = report.rows[0]
    assert row.relation == "dirty"
    assert row.lfs_cache == "complete"
    assert row.assets == "preserved"
    assert (clone / "model.bin").read_bytes() == pointer


def test_deadline_kills_the_fetch_process_group_and_reports_unvisited_scope(tmp_path, monkeypatch):
    vault = tmp_path / "vault"
    vault.mkdir()
    _, _, slow = _repository(tmp_path, "slow")
    _, _, later = _repository(tmp_path, "later")
    marker = tmp_path / "orphan-survived"
    trap = tmp_path / "slow-upload"
    trap.write_text(
        f"#!/bin/sh\n(sleep 2; echo orphan > '{marker}') &\nsleep 20\n",
        encoding="utf-8",
    )
    trap.chmod(0o755)
    git(slow, "remote", "set-url", "origin", f"ext::{trap}")
    monkeypatch.setenv("GIT_ALLOW_PROTOCOL", "file:ext")

    started = time.monotonic()
    report = startup.run(
        vault,
        Config(
            scopes=(
                _scope("slow", slow, vault),
                _scope("later", later, vault),
            )
        ),
        timeout=10,
        deadline=2,
    )
    elapsed = time.monotonic() - started
    rows = {row.name: row for row in report.rows}

    assert elapsed < 3
    assert rows["slow"].refresh == "deadline"
    assert rows["later"].refresh == "unvisited"
    assert "ATTENTION" in startup.render(report)
    time.sleep(2.2)
    assert not marker.exists()


def test_inventory_deadline_is_incomplete_and_exits_124_with_real_git_process(
    tmp_path, monkeypatch
):
    vault = tmp_path / "vault"
    vault.mkdir()
    _, _, clone = _repository(tmp_path, "inventory-slow")
    wrapper_dir = tmp_path / "bin"
    wrapper_dir.mkdir()
    wrapper = wrapper_dir / "git"
    wrapper.write_text(
        "#!/bin/sh\n"
        'if [ "$3" = rev-parse ] && [ "$4" = --is-inside-work-tree ]; then sleep 20; fi\n'
        'exec /usr/bin/git "$@"\n',
        encoding="utf-8",
    )
    wrapper.chmod(0o755)
    monkeypatch.setenv("PATH", f"{wrapper_dir}:{os.environ['PATH']}")

    started = time.monotonic()
    report = startup.run(
        vault,
        Config(scopes=(_scope("slow-inventory", clone, vault),)),
        timeout=10,
        deadline=2,
    )
    elapsed = time.monotonic() - started

    assert elapsed < 3
    assert not report.complete
    assert report.exit_code == 124
    assert report.rows[0].refresh == "unvisited"
    assert startup.render(report).startswith("REPORT INCOMPLETE — DEADLINE")


def test_hard_deadline_returns_124_when_actual_state_cannot_be_inspected(tmp_path, monkeypatch):
    vault = tmp_path / "vault"
    vault.mkdir()
    _, _, clone = _repository(tmp_path, "incomplete")
    gate = tmp_path / "inspection-gate"
    trap = tmp_path / "slow-origin"
    trap.write_text(f"#!/bin/sh\ntouch '{gate}'\nsleep 20\n", encoding="utf-8")
    trap.chmod(0o755)
    git(clone, "remote", "set-url", "origin", f"ext::{trap}")
    wrapper_dir = tmp_path / "bin"
    wrapper_dir.mkdir()
    wrapper = wrapper_dir / "git"
    wrapper.write_text(
        "#!/bin/sh\n"
        f'if [ -f \'{gate}\' ] && [ "$3" = rev-parse ] && [ "$4" = HEAD ]; then sleep 20; fi\n'
        'exec /usr/bin/git "$@"\n',
        encoding="utf-8",
    )
    wrapper.chmod(0o755)
    monkeypatch.setenv("PATH", f"{wrapper_dir}:{os.environ['PATH']}")
    monkeypatch.setenv("GIT_ALLOW_PROTOCOL", "file:ext")

    report = startup.run(
        vault,
        Config(scopes=(_scope("incomplete", clone, vault),)),
        timeout=10,
        deadline=2,
    )

    assert not report.complete
    assert report.exit_code == 124
    assert startup.render(report).startswith("REPORT INCOMPLETE — DEADLINE")


def test_all_remote_failures_still_exit_zero_when_the_report_completes(tmp_path, capsys):
    vault = tmp_path / "vault"
    vault.mkdir()
    _, _, clone = _repository(tmp_path, "gone")
    git(clone, "remote", "set-url", "origin", str(tmp_path / "absent.git"))
    relative = os.path.relpath(clone, vault)
    (vault / "vault.toml").write_text(
        f'[scopes]\ngone = {{ path = "{relative}", branch = "main" }}\n',
        encoding="utf-8",
    )

    assert main(["--vault", str(vault), "startup", "--timeout", "2", "--deadline", "10"]) == 0
    output = capsys.readouterr().out
    assert output.startswith("REPORT COMPLETED — ATTENTION")
    assert "refresh=stale" in output
