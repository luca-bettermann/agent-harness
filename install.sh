#!/bin/sh
# Install agent-harness into a workspace root for Claude Code and Codex. Nothing is written outside that root,
# so the harness applies only to sessions working under it, whichever account runs them.
# Usage: install.sh <workspace-root> [path/to/INSTANCE.md]   (INSTANCE is remembered for later runs)
# Rerun after updating the checkout. A foreign or edited entry file is moved aside as *.pre-harness[.N].
set -eu
src=$(cd "$(dirname "$0")" && pwd)
die() { echo "install.sh: $*" >&2; exit 1; }
[ $# -ge 1 ] || die "usage: install.sh <workspace-root> [INSTANCE.md]"
[ -d "$1" ] || die "no workspace root at $1"
root=$(cd "$1" && pwd)
# Entry files at or above a home directory would reach every session of that account.
case $HOME/ in "${root%/}"/*) die "$root contains $HOME: install into a workspace root, never account-wide";; esac
dst=$root/.agent-harness
f=$root/.claude/settings.json
trap 'rm -rf "$dst.new" "$f.tmp" "$root/.codex/hooks.json.tmp"' EXIT

# Check everything before writing anything.
command -v jq >/dev/null || die "needs jq"
for x in "$f" "$root/.codex/hooks.json"; do [ ! -e "$x" ] || jq empty "$x" 2>/dev/null || die "$x is not valid JSON"; done
inst=${2:-$(readlink "$dst/INSTANCE.md" 2>/dev/null || true)}
if [ -n "$inst" ]; then
  [ -f "$inst" ] || die "no INSTANCE file at $inst"
  inst=$(cd "$(dirname "$inst")" && pwd)/$(basename "$inst")
fi

# Build: AGENTS, hooks, launcher, knowledge, and the skills with their addenda appended.
rm -rf "$dst.new"
mkdir -p "$dst.new/skills"
cp -r "$src/AGENTS.md" "$src/hooks" "$src/bin" "$src/knowledge" "$dst.new/"
for d in "$src"/upstream/skills/engineering/*/ "$src"/upstream/skills/productivity/*/ "$src"/engineering/*/ "$src"/knowledge/*/; do
  n=$(basename "$d")
  [ -f "$d/SKILL.md" ] || continue
  if [ -e "$dst.new/skills/$n" ]; then die "two skills named $n (second: $d)"; fi
  cp -r "$d" "$dst.new/skills/$n"
  a="$src/engineering/addenda/$n.md"
  if [ -f "$a" ]; then printf '\n' >> "$dst.new/skills/$n/SKILL.md"; cat "$a" >> "$dst.new/skills/$n/SKILL.md"; fi
done
# The installation's docs/agents/*.md with skill frontmatter are skills too, linked so each stays one file.
if [ -n "$inst" ]; then
  for m in "$(dirname "$inst")"/docs/agents/*.md; do
    [ "$(head -n 1 "$m" 2>/dev/null)" = --- ] || continue
    n=$(basename "$m" .md)
    if [ -e "$dst.new/skills/$n" ]; then die "two skills named $n (second: $m)"; fi
    mkdir "$dst.new/skills/$n" && ln -s "$m" "$dst.new/skills/$n/SKILL.md"
  done
fi
for a in "$src"/engineering/addenda/*.md; do
  [ -d "$dst.new/skills/$(basename "$a" .md)" ] || echo "warning: addendum without skill: $a" >&2
done
[ -n "$inst" ] && ln -s "$inst" "$dst.new/INSTANCE.md"
[ -d "$dst/written" ] && mv "$dst/written" "$dst.new/"
mkdir -p "$dst.new/written"
rm -rf "$dst"
mv "$dst.new" "$dst"

# Links: only links into $dst are ours to replace or remove.
ours() { [ -L "$1" ] && case $(readlink "$1") in "$dst"/*) true;; *) false;; esac; }
link() {
  if [ -e "$2" ] || [ -L "$2" ]; then
    ours "$2" || { echo "skipped $2: not made by this install" >&2; return 0; }
  fi
  ln -sfn "$1" "$2"
}
# Skills: Claude Code reads .claude/skills, Codex .agents/skills, from the project root.
mkdir -p "$root/.claude/skills" "$root/.agents/skills"
for s in "$dst"/skills/*/; do
  n=$(basename "$s")
  link "$dst/skills/$n" "$root/.claude/skills/$n"
  link "$dst/skills/$n" "$root/.agents/skills/$n"
done
# Claude Code reads CLAUDE.local.md in every directory above the session, nested repositories included.
[ -n "$inst" ] && link "$dst/INSTANCE.md" "$root/CLAUDE.local.md"
for l in "$root"/.claude/skills/* "$root"/.agents/skills/* "$root/.claude/agents/"* "$root/CLAUDE.local.md"; do
  if ours "$l" && [ ! -e "$l" ]; then rm "$l"; fi
done

# Entry points. Claude Code reads CLAUDE.md upward from any nested repository, but skips @imports outside
# that repository, so AGENTS is written in full. A file that isn't exactly what this script last wrote
# (foreign, symlinked or edited) is moved aside.
mark='<!-- written by agent-harness install.sh; edits here are moved aside on the next install -->'
entry() { # entry <name> <path>, content on stdin
  cat > "$dst/written/$1.new"
  if [ -L "$2" ] || { [ -e "$2" ] && ! cmp -s "$2" "$dst/written/$1" && ! cmp -s "$2" "$dst/written/$1.new"; }; then
    b=$2.pre-harness; i=0
    while [ -e "$b" ] || [ -L "$b" ]; do i=$((i + 1)); b=$2.pre-harness.$i; done
    mv "$2" "$b"; echo "moved $2 to $b" >&2
  fi
  cp "$dst/written/$1.new" "$2"
  mv "$dst/written/$1.new" "$dst/written/$1"
}
{ echo "$mark"; cat "$dst/AGENTS.md"; } | entry claude "$root/CLAUDE.md"
{ echo "$mark"; cat "$dst/AGENTS.md"; [ -n "$inst" ] && printf '\nRead %s in full before any work: it binds this harness to this installation.\n' "$inst"; } | entry codex "$root/AGENTS.md"

# Hooks, in the workspace's project settings of both clients (same format): the skill-loading rule on every prompt,
# subagent start, and session start after compaction or resume. Earlier entries pointing into $dst/hooks are
# dropped first, so reruns don't duplicate and retired hooks go. Codex runs project hooks only once the account
# trusts the workspace and has reviewed them (`/hooks`).
for x in "$f" "$root/.codex/hooks.json"; do
  mkdir -p "$(dirname "$x")"; [ -s "$x" ] || echo '{}' > "$x"
  jq --arg d "\"$dst/hooks/" --arg s "\"$dst/hooks/load-skills.sh\"" '
    def put($ev; $matcher): .hooks[$ev] += [({matcher: $matcher} | with_entries(select(.value != null))) + {hooks: [{type: "command", command: $s}]}];
    .hooks //= {} | .hooks |= (map_values(map(select(all(.hooks[]?; .command // "" | startswith($d) | not)))) | with_entries(select(.value != [])))
    | put("UserPromptSubmit"; null) | put("SubagentStart"; null) | put("SessionStart"; "compact|resume")' "$x" > "$x.tmp"
  cat "$x.tmp" > "$x"; rm -f "$x.tmp"
done
echo "installed into $root; below it, start agents with $dst/bin/claude or $dst/bin/codex"
