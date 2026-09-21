"""The stream sweep: ancestry proves death, front matter proves membership, links refuse deletion."""

from __future__ import annotations

import pytest

from vaulttools import sweep
from vaulttools.board import VaultError, read_cards

from .conftest import git


def _staged(bench, name="alpha", title="Alpha stream", merged=True, execute=True):
    tip = bench.repo("alpha-repo", name, merged=merged)
    bench.stream(name, title, tip, "alpha-repo", execute=execute)
    return tip


def test_a_merged_stream_moves_to_promotion(bench):
    tip = bench.repo("alpha-repo", "alpha")
    bench.stream("alpha", "Alpha stream", tip, "alpha-repo")
    board = bench.vault / "kanban.md"
    board.write_text(
        board.read_text(encoding="utf-8").replace(
            "## promotion\n\n- [ ] [[Alpha stream]] #example", "## promotion\n"
        ),
        encoding="utf-8",
    )
    bench.card("Alpha stream", "in progress")
    bench.publish("bench: card into in progress")
    message = sweep.to_promotion(bench.vault, bench.config, bench.root, "alpha")
    assert "in progress -> promotion" in message
    cards = read_cards((bench.vault / "kanban.md").read_text(encoding="utf-8"))
    assert [card.column for card in cards if card.title == "Alpha stream"] == ["promotion"]


def test_a_stream_naming_the_vault_by_its_own_folder_name_verifies_against_the_vault_clone(bench):
    """Mutation caught: resolving every repo name under `repos/`, missing the vault's own clone."""
    tip = git(bench.vault, "rev-parse", "HEAD").strip()
    bench.write(
        f"tasks/{bench.vault.name} stream.md",
        f"---\ntype: stream\nstream: selfname\nrepos: [{bench.vault.name}]\nblocked:\n---\n"
        f"Owner: example\n\nStream description: the selfname stream.\n\n"
        f"Merge evidence:\n- {bench.vault.name}: {tip} -> origin/main\n\n"
        f"Tasks:\n\nMR link:\n\nPromotion:\n- [ ] Execute\n",
    )
    bench.card(f"{bench.vault.name} stream", "in progress")
    bench.publish("bench: vault-named stream")
    message = sweep.to_promotion(bench.vault, bench.config, bench.root, "selfname")
    assert "in progress -> promotion" in message


def test_a_deleted_but_unmerged_branch_is_refused(bench):
    _staged(bench, merged=False)
    with pytest.raises(VaultError, match="is not merged"):
        sweep.to_promotion(bench.vault, bench.config, bench.root, "alpha")
    assert (bench.vault / "tasks" / "Alpha stream.md").is_file()


def test_merge_evidence_naming_an_unknown_commit_is_refused(bench):
    tip = _staged(bench)
    note = bench.vault / "tasks" / "Alpha stream.md"
    unknown = "0123456789abcdef0123456789abcdef01234567"
    note.write_text(note.read_text(encoding="utf-8").replace(tip, unknown), encoding="utf-8")
    bench.publish("bench: bogus evidence")
    with pytest.raises(VaultError, match="unknown commit"):
        sweep.execute(bench.vault, bench.config, bench.root, "alpha")


def test_a_stream_without_merge_evidence_for_a_repo_is_refused(bench):
    tip = bench.repo("alpha-repo", "alpha")
    bench.stream("alpha", "Alpha stream", tip, "alpha-repo")
    note = bench.vault / "tasks" / "Alpha stream.md"
    note.write_text(note.read_text(encoding="utf-8").replace("Merge evidence:", "Notes:"), encoding="utf-8")
    bench.publish("bench: evidence removed")
    with pytest.raises(VaultError, match="records no merge evidence"):
        sweep.execute(bench.vault, bench.config, bench.root, "alpha")


def test_execute_is_refused_while_the_execute_box_is_unticked(bench):
    _staged(bench, execute=False)
    with pytest.raises(VaultError, match="no ticked Execute box"):
        sweep.execute(bench.vault, bench.config, bench.root, "alpha")
    assert (bench.vault / "tasks" / "Alpha stream two.md").is_file()


def test_execute_is_refused_while_an_outside_note_links_into_the_stream(bench):
    _staged(bench)
    bench.write("doctrine/Concept.md", "grounded in [[Alpha stream two]]\n")
    bench.publish("bench: outside reference")
    with pytest.raises(VaultError, match="still reference it"):
        sweep.execute(bench.vault, bench.config, bench.root, "alpha")
    assert (bench.vault / "tasks" / "Alpha stream two.md").is_file()


def test_execute_deletes_the_note_its_card_and_every_front_matter_member_in_one_commit(bench):
    _staged(bench)
    before = git(bench.vault, "rev-list", "--count", "HEAD").strip()
    message = sweep.execute(bench.vault, bench.config, bench.root, "alpha")
    assert "swept stream 'alpha'" in message
    for name in ("Alpha stream.md", "Alpha stream one.md", "Alpha stream two.md"):
        assert not (bench.vault / "tasks" / name).exists()
    assert read_cards((bench.vault / "kanban.md").read_text(encoding="utf-8")) == ()
    assert int(git(bench.vault, "rev-list", "--count", "HEAD").strip()) == int(before) + 1
    head = git(bench.vault, "rev-parse", "HEAD").strip()
    assert head == git(bench.vault, "rev-parse", "origin/main").strip()


def test_membership_comes_from_the_front_matter_of_every_task_note(bench):
    _staged(bench)
    stream = sweep.load_stream(bench.vault, bench.config, "alpha")
    assert {path.stem for path in stream.members} == {"Alpha stream one", "Alpha stream two"}


def _rewrite(bench, old: str, new: str, message: str) -> None:
    note = bench.vault / "tasks" / "Alpha stream.md"
    note.write_text(note.read_text(encoding="utf-8").replace(old, new), encoding="utf-8")
    bench.publish(message)


def test_a_task_list_entry_that_is_no_front_matter_member_refuses_the_sweep(bench):
    """Mutation caught: a hand-maintained task list drifting past the membership authority."""
    _staged(bench)
    bench.write("tasks/Beta task.md", "---\ntype: task\nstream: beta\nrepos: []\nblocked:\n---\nbeta\n")
    _rewrite(bench, "MR link:", "- [ ] [[Beta task]]\n\nMR link:", "bench: a foreign entry")
    with pytest.raises(VaultError, match="Beta task: listed under Tasks but no front-matter member"):
        sweep.execute(bench.vault, bench.config, bench.root, "alpha")
    assert (bench.vault / "tasks" / "Beta task.md").is_file()


def test_a_front_matter_member_missing_from_the_task_list_refuses_the_sweep(bench):
    """Mutation caught: a member deleted without ever appearing on the card it belonged to."""
    _staged(bench)
    _rewrite(bench, "- [ ] [[Alpha stream two]]\n", "", "bench: member dropped from the list")
    with pytest.raises(VaultError, match="Alpha stream two: a front-matter member .* not listed"):
        sweep.execute(bench.vault, bench.config, bench.root, "alpha")
    assert (bench.vault / "tasks" / "Alpha stream two.md").is_file()


def test_a_member_note_in_a_tasks_subfolder_is_found_and_swept(bench):
    """Mutation caught: discovering task notes with `glob`, which never descends a subfolder."""
    _staged(bench)
    bench.write(
        "tasks/deep/Alpha stream three.md",
        "---\ntype: task\nstream: alpha\nrepos: [alpha-repo]\nblocked:\n---\ndeep\n",
    )
    _rewrite(
        bench,
        "- [ ] [[Alpha stream two]]\n",
        "- [ ] [[Alpha stream two]]\n- [ ] [[tasks/deep/Alpha stream three]]\n",
        "bench: a member in a subfolder",
    )
    sweep.execute(bench.vault, bench.config, bench.root, "alpha")
    assert not (bench.vault / "tasks" / "deep" / "Alpha stream three.md").exists()


def test_the_sweep_rebases_before_it_reads_the_execute_tick(bench):
    """Mutation caught: reading the stream note before `sync`, so a pushed tick is invisible."""
    _staged(bench, execute=False)
    other = bench.other_writer()
    note = other / "tasks" / "Alpha stream.md"
    note.write_text(note.read_text(encoding="utf-8").replace("- [ ] Execute", "- [x] Execute"), "utf-8")
    git(other, "commit", "-qam", "other: tick Execute")
    git(other, "push", "-q", "origin", "main")
    assert "swept stream 'alpha'" in sweep.execute(bench.vault, bench.config, bench.root, "alpha")


def test_an_uncommitted_change_to_a_task_note_is_refused_by_its_own_message(bench):
    """Mutation caught: dropping the clean-target check, leaving only git's rebase complaint."""
    _staged(bench)
    (bench.vault / "tasks" / "Alpha stream two.md").write_text("edited\n", encoding="utf-8")
    with pytest.raises(VaultError, match="uncommitted changes in the paths this action rewrites"):
        sweep.execute(bench.vault, bench.config, bench.root, "alpha")
    assert (bench.vault / "tasks" / "Alpha stream two.md").is_file()


def test_a_prose_line_never_ends_a_section_so_a_later_execute_tick_is_seen():
    """Mutation caught: ending a section at any prose line, hiding the Execute tick below it."""
    text = "Promotion:\n- [ ] a concept candidate\nAll candidates agreed with the operator\n- [x] Execute\n"
    assert sweep._execute(text)


def test_merge_evidence_after_a_prose_line_keeps_the_second_repository():
    """Mutation caught: ending a section at any prose line, dropping the second repo's evidence."""
    text = (
        "Merge evidence:\n- alpha-repo: 1234567 -> origin/main\n"
        "Verified against both remotes\n- beta-repo: 89abcde -> origin/main\n\nTasks:\n"
    )
    assert set(sweep._evidence(text)) == {"alpha-repo", "beta-repo"}


def test_a_task_note_of_another_stream_is_left_alone(bench):
    _staged(bench)
    bench.write("tasks/Beta task.md", "---\ntype: task\nstream: beta\nrepos: []\nblocked:\n---\nbeta\n")
    bench.publish("bench: foreign member")
    sweep.execute(bench.vault, bench.config, bench.root, "alpha")
    assert (bench.vault / "tasks" / "Beta task.md").is_file()


def test_the_promotion_section_is_read_apart_from_the_rest_of_the_note():
    text = "Tasks:\n- [x] Execute\n\nPromotion:\n- [ ] candidate\n- [ ] Execute\n"
    assert sweep.section(text, "Promotion").strip().endswith("- [ ] Execute")
    assert not sweep._execute(text)


def test_a_surviving_card_linking_a_member_refuses_before_anything_is_deleted(bench):
    """Mutation caught: an inbound guard that skips the board, catching this only after deletion."""
    _staged(bench)
    bench.card("Alpha stream one", "backlog")
    bench.publish("bench: a second card links a member note")
    with pytest.raises(VaultError, match="still reference it"):
        sweep.execute(bench.vault, bench.config, bench.root, "alpha")
    assert (bench.vault / "tasks" / "Alpha stream one.md").is_file()
    assert git(bench.vault, "rev-parse", "HEAD") == git(bench.vault, "rev-parse", "origin/main")
