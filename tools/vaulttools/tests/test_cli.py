"""The one CLI: exit codes carry the gate."""

from __future__ import annotations

from vaulttools.board import read_cards
from vaulttools.cli import main

from .conftest import git


def test_hygiene_exits_non_zero_on_a_blocking_row(bench, capsys):
    (bench.vault / "temp").mkdir()
    (bench.vault / "temp" / "probe.log").write_text("noise\n", encoding="utf-8")
    assert main(["--vault", str(bench.vault), "hygiene", "--root", str(bench.root)]) == 1
    assert "FAIL  temp" in capsys.readouterr().out


def test_an_explicit_root_overrides_auto_detection(bench, capsys):
    """Mutation caught: auto-detecting the root even when `--root` is passed explicitly."""
    alt_root = bench.root.parent / "alt-root"
    clone = alt_root / "repos" / "alpha-repo"
    clone.mkdir(parents=True)
    git(clone, "init", "-q", "-b", "main")
    settings = (("user.email", "bench@example.com"), ("user.name", "Bench"), ("commit.gpgsign", "false"))
    for key, value in settings:
        git(clone, "config", key, value)
    (clone / "README.md").write_text("base\n", encoding="utf-8")
    git(clone, "add", "-A")
    git(clone, "commit", "-q", "-m", "base")
    (clone / "README.md").write_text("edited\n", encoding="utf-8")

    assert main(["--vault", str(bench.vault), "hygiene"]) == 0
    capsys.readouterr()
    assert main(["--vault", str(bench.vault), "hygiene", "--root", str(alt_root)]) == 1
    assert "FAIL  canonical clones" in capsys.readouterr().out


def test_report_only_hygiene_never_exits_non_zero(bench, capsys):
    (bench.vault / "temp").mkdir()
    (bench.vault / "temp" / "probe.log").write_text("noise\n", encoding="utf-8")
    assert main(["--vault", str(bench.vault), "hygiene", "--root", str(bench.root), "--report-only"]) == 0
    assert "temp" in capsys.readouterr().out


def test_global_config_load_rejects_the_legacy_scope_shape(bench, capsys):
    bench.write("vault.toml", '[scopes]\nwork = "../work"\n')

    assert main(["--vault", str(bench.vault), "hygiene", "--report-only"]) == 1
    assert "old string form" in capsys.readouterr().err


def test_a_refused_sweep_reports_and_exits_non_zero(bench, capsys):
    tip = bench.repo("alpha-repo", "alpha", merged=False)
    bench.stream("alpha", "Alpha stream", tip, "alpha-repo")
    code = main(["--vault", str(bench.vault), "sweep", "alpha", "--root", str(bench.root), "--execute"])
    assert code == 1
    assert "is not merged" in capsys.readouterr().err
    assert (bench.vault / "tasks" / "Alpha stream.md").is_file()


def test_hook_check_exits_non_zero_on_a_staged_oversized_note(bench, capsys):
    bench.write("tasks/Oversized.md", "x" * 10_001)
    git(bench.vault, "add", "-A")
    assert main(["--vault", str(bench.vault), "hook", "check"]) == 1
    assert "REFUSED" in capsys.readouterr().out


def _pushed_board(bench) -> str:
    return git(bench.vault, "show", "origin/main:kanban.md")


def test_move_pushes_the_card_into_its_new_column(bench):
    """Mutation caught: a mover that rewrites the board locally and never publishes it."""
    bench.write("tasks/Alpha stream.md", "---\ntype: stream\nstream: alpha\nrepos: []\nblocked:\n---\n")
    bench.card("Alpha stream", "open")
    bench.publish("bench: a card to move")
    assert main(["--vault", str(bench.vault), "move", "Alpha stream", "in progress"]) == 0
    columns = [card.column for card in read_cards(_pushed_board(bench)) if card.title == "Alpha stream"]
    assert columns == ["in progress"]


def test_move_drops_only_the_tags_it_is_given(bench):
    """Mutation caught: a mover that ignores `--drop`, carrying `#blocked` into the next column."""
    bench.write("tasks/Alpha stream.md", "---\ntype: stream\nstream: alpha\nrepos: []\nblocked:\n---\n")
    bench.card("Alpha stream", "open", tags="#example #blocked")
    bench.publish("bench: a blocked card")
    assert main(
        ["--vault", str(bench.vault), "move", "Alpha stream", "in progress", "--drop", "blocked"]
    ) == 0
    pushed = _pushed_board(bench)
    assert "#blocked" not in pushed
    assert "- [ ] [[Alpha stream]] #example" in pushed


def test_an_unreachable_remote_preserves_the_stream_and_exits_non_zero(bench, capsys):
    """Mutation caught: treating a failed fetch as a verified merge, deleting an unmerged stream."""
    tip = bench.repo("alpha-repo", "alpha")
    bench.stream("alpha", "Alpha stream", tip, "alpha-repo")
    git(bench.root / "repos" / "alpha-repo", "remote", "set-url", "origin", str(bench.root / "gone.git"))
    code = main(["--vault", str(bench.vault), "sweep", "alpha", "--root", str(bench.root), "--execute"])
    assert code == 1
    assert "fetch failed" in capsys.readouterr().err
    for name in ("Alpha stream.md", "Alpha stream one.md", "Alpha stream two.md"):
        assert (bench.vault / "tasks" / name).is_file()
