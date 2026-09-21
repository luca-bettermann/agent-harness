"""One resolver: every supported link syntax is seen, and nothing else is."""

from __future__ import annotations

from vaulttools.links import link_targets, referrers

SYNTAXES = {
    "[[Plain]]": "Plain",
    "[[tasks/Path qualified]]": "tasks/Path qualified",
    "[[Aliased|shown text]]": "Aliased",
    "[[Headed#Section]]": "Headed",
    "[[tasks/Both#Section|shown]]": "tasks/Both",
    "[text](tasks/Markdown link.md)": "tasks/Markdown link",
    "[text](tasks/Escaped%20link.md)": "tasks/Escaped link",
}


def test_the_resolver_sees_every_supported_link_syntax():
    for source, expected in SYNTAXES.items():
        found = link_targets(source)
        assert found, f"{source} produced no target"
        assert found[0].removesuffix(".md") == expected, source


def test_the_resolver_ignores_external_and_non_note_links():
    text = "[site](https://example.com/page.md) [image](figure.png) [[#local heading]]"
    assert link_targets(text) == ()


def test_referrers_names_the_outside_note_and_the_target_it_uses(tmp_path):
    vault = tmp_path
    (vault / "tasks").mkdir()
    doomed = vault / "tasks" / "Member.md"
    doomed.write_text("member\n", encoding="utf-8")
    outside = vault / "Concept.md"
    outside.write_text("see [[tasks/Member]]\n", encoding="utf-8")
    found = referrers([outside, doomed], [doomed], vault)
    assert found == {outside: ("tasks/Member",)}


def test_referrers_excludes_links_inside_the_deletion_set(tmp_path):
    vault = tmp_path
    (vault / "tasks").mkdir()
    stream = vault / "tasks" / "Stream.md"
    member = vault / "tasks" / "Member.md"
    stream.write_text("tasks: [[Member]]\n", encoding="utf-8")
    member.write_text("back to [[Stream]]\n", encoding="utf-8")
    assert referrers([stream, member], [stream, member], vault) == {}


def test_referrers_still_names_a_target_that_is_already_deleted(tmp_path):
    vault = tmp_path
    (vault / "tasks").mkdir()
    doomed = vault / "tasks" / "Member.md"
    outside = vault / "Concept.md"
    outside.write_text("see [[Member]]\n", encoding="utf-8")
    assert referrers([outside], [doomed], vault) == {outside: ("Member",)}
