"""The shared board parser and its refusals."""

from __future__ import annotations

import pytest

from vaulttools import board
from vaulttools.board import (
    Repo,
    VaultError,
    find_root,
    load_config,
    move_card,
    note_paths,
    read_cards,
    read_frontmatter,
    remove_card,
)

from .conftest import VAULT_TOML, git

BOARD = "## open\n\n- [ ] [[Alpha]] #example\n- [ ] [[Alpha two]] #example\n\n## promotion\n\n"


def test_cards_carry_the_column_heading_above_them():
    cards = read_cards(BOARD)
    assert [(card.title, card.column) for card in cards] == [("Alpha", "open"), ("Alpha two", "open")]


def test_moving_an_exact_title_wins_over_the_substring_match():
    text, previous = move_card(BOARD, "Alpha", "promotion")
    assert previous == "open"
    assert read_cards(text)[-1].column == "promotion"


def test_an_ambiguous_substring_title_is_refused():
    with pytest.raises(VaultError, match="ambiguous"):
        move_card(BOARD, "Alph", "promotion")


def test_removing_a_card_from_the_wrong_column_is_refused():
    with pytest.raises(VaultError, match="not 'promotion'"):
        remove_card(BOARD, "Alpha", "promotion")


def test_front_matter_reads_flow_and_block_lists_the_same_way(tmp_path):
    flow = tmp_path / "flow.md"
    block = tmp_path / "block.md"
    flow.write_text("---\ntype: stream\nrepos: [one, two]\n---\n", encoding="utf-8")
    block.write_text("---\ntype: stream\nrepos:\n  - one\n  - two\n---\n", encoding="utf-8")
    assert read_frontmatter(flow) == read_frontmatter(block) == {"type": "stream", "repos": ["one", "two"]}


def test_vault_toml_overrides_the_built_in_caps_and_board(bench):
    config = load_config(bench.vault)
    assert config.board == "kanban.md"
    assert config.caps["tasks/"] == 10000


def test_a_cap_key_naming_no_folder_fails_loud(bench):
    """Mutation caught: an unvalidated key like `tasks` that silently caps nothing."""
    bench.write("vault.toml", VAULT_TOML + "tasks = 10000\n")
    with pytest.raises(VaultError, match="names no folder"):
        load_config(bench.vault)


def test_a_default_cap_is_removed_by_setting_it_to_false(bench):
    """Mutation caught: reading `false` as `int(False)`, capping the folder at zero chars."""
    bench.write("vault.toml", VAULT_TOML + '"08 Tasks/" = false\n')
    assert "08 Tasks/" not in load_config(bench.vault).caps


def test_the_clean_check_ignores_dirt_outside_the_paths_it_is_given(bench):
    """Mutation caught: a clean check run without its pathspec, refusing a routinely dirty vault."""
    bench.write("doctrine/AGENTS.md", "edited elsewhere\n")
    repo = Repo(bench.vault)
    repo.require_clean(["kanban.md"])
    with pytest.raises(VaultError, match="uncommitted changes"):
        repo.require_clean(["doctrine/AGENTS.md"])


def test_a_failed_reapply_aborts_the_rebase_it_started(bench):
    """Mutation caught: a reapply that raises mid-rebase and leaves the vault in a rebase."""
    other = bench.other_writer()
    (other / "shared.md").write_text("theirs\n", encoding="utf-8")
    git(other, "add", "-A")
    git(other, "commit", "-qm", "other: shared")
    git(other, "push", "-q", "origin", "main")
    bench.write("shared.md", "mine\n")
    bench.commit("mine: shared")

    def reapply() -> None:
        raise VaultError("refused during the reapply")

    with pytest.raises(VaultError, match="refused during the reapply"):
        Repo(bench.vault).push(["shared.md"], reapply)
    assert not (bench.vault / ".git" / "rebase-merge").exists()
    assert not (bench.vault / ".git" / "rebase-apply").exists()


def test_every_git_call_decodes_its_output_as_utf_8(bench, monkeypatch):
    """Mutation caught: `text=True` alone, which decodes git output in the ambient locale."""
    seen: dict[str, object] = {}
    real = board.subprocess.run

    def spy(args, **kwargs):
        seen.update(kwargs)
        return real(args, **kwargs)

    monkeypatch.setattr(board.subprocess, "run", spy)
    Repo(bench.vault).git("status", "--porcelain")
    assert seen["encoding"] == "utf-8"


def test_a_non_ascii_note_name_survives_the_git_listing(bench):
    """Mutation caught: listing notes without `-z`, which returns octal-quoted paths."""
    note = bench.write("tasks/\u00dcber note.md", "grounded\n")
    bench.commit("bench: a non-ascii note")
    assert note in note_paths(bench.vault)


def test_root_is_the_vaults_parent_when_repos_sits_directly_there(bench):
    """The old layout: the vault at the workspace root, `repos/` beside it."""
    (bench.root / "repos").mkdir()
    assert find_root(bench.vault, bench.config) == bench.root


def test_root_is_found_higher_up_when_the_vault_is_nested_deeper(bench):
    """The new layout: the vault moved under a folder of its own, `repos/` staying put above it."""
    (bench.root / "repos").mkdir()
    nested_vault = bench.root / "knowledge-base" / "agents"
    nested_vault.mkdir(parents=True)
    assert find_root(nested_vault, bench.config) == bench.root


def test_root_falls_back_to_the_vaults_parent_when_no_repos_directory_exists_above_it(bench):
    """Mutation caught: raising instead of falling back when no ancestor has `repos/`."""
    lonely_vault = bench.root / "lonely" / "vault"
    lonely_vault.mkdir(parents=True)
    assert find_root(lonely_vault, bench.config) == lonely_vault.parent
