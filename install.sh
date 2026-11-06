#!/bin/sh
# Install agent-harness for the current account (Claude Code and Codex).
# Usage: install.sh [path/to/INSTANCE.md]   (remembered for later runs)
# Rerun after updating the checkout. A foreign or edited entry file is moved aside as *.pre-harness[.N].
set -eu
src=$(cd "$(dirname "$0")" && pwd)
dst=$HOME/.agent-harness
f=$HOME/.claude/settings.json
die() { echo "install.sh: $*" >&2; exit 1; }
trap 'rm -rf "$dst.new" "$f.tmp"' EXIT

# Check everything before writing anything.
command -v jq >/dev/null || die "needs jq"
[ ! -e "$f" ] || jq empty "$f" 2>/dev/null || die "$f is not valid JSON"
inst=${1:-$(cat "$dst/instance-path" 2>/dev/null || true)}
if [ -n "$inst" ]; then
  [ -f "$inst" ] || die "no INSTANCE file at $inst"
  inst=$(cd "$(dirname "$inst")" && pwd)/$(basename "$inst")
fi

# Build: AGENTS, hook, knowledge, and the skills with their addenda appended.
rm -rf "$dst.new"
mkdir -p "$dst.new/skills"
cp -r "$src/AGENTS.md" "$src/hooks" "$src/knowledge" "$dst.new/"
for d in "$src"/upstream/skills/engineering/*/ "$src"/upstream/skills/productivity/*/ "$src"/engineering/*/ "$src"/knowledge/*/; do
  n=$(basename "$d")
  [ -f "$d/SKILL.md" ] || continue
  # The tracker mapping lives in the installation repo (INSTANCE); no per-repo copies.
  [ "$n" = setup-matt-pocock-skills ] && continue
  if [ -e "$dst.new/skills/$n" ]; then die "two skills named $n (second: $d)"; fi
  cp -r "$d" "$dst.new/skills/$n"
  a="$src/engineering/addenda/$n.md"
  if [ -f "$a" ]; then printf '\n' >> "$dst.new/skills/$n/SKILL.md"; cat "$a" >> "$dst.new/skills/$n/SKILL.md"; fi
done
for a in "$src"/engineering/addenda/*.md; do
  [ -d "$dst.new/skills/$(basename "$a" .md)" ] || echo "warning: addendum without skill: $a" >&2
done
[ -n "$inst" ] && echo "$inst" > "$dst.new/instance-path"
[ -d "$dst/written" ] && mv "$dst/written" "$dst.new/"
mkdir -p "$dst.new/written"
rm -rf "$dst"
mv "$dst.new" "$dst"

# Skill links: only links into $dst are ours to replace or remove.
ours() { [ -L "$1" ] && case $(readlink "$1") in "$dst"/*) true;; *) false;; esac; }
link() {
  if [ -e "$2" ] || [ -L "$2" ]; then
    ours "$2" || { echo "skipped $2: not made by this install" >&2; return 0; }
  fi
  ln -sfn "$1" "$2"
}
mkdir -p "$HOME/.claude/skills" "$HOME/.codex/skills"
for s in "$dst"/skills/*/; do
  n=$(basename "$s")
  link "$dst/skills/$n" "$HOME/.claude/skills/$n"
  link "$dst/skills/$n" "$HOME/.codex/skills/$n"
done
for l in "$HOME"/.claude/skills/* "$HOME"/.codex/skills/*; do
  if ours "$l" && [ ! -e "$l" ]; then rm "$l"; fi
done

# Entry points: AGENTS plus the installation's INSTANCE. A file that isn't
# exactly what this script last wrote (foreign, symlinked or edited) is moved aside.
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
mkdir -p "$HOME/.claude" "$HOME/.codex"
{ echo "$mark"; echo "@$dst/AGENTS.md"; [ -n "$inst" ] && echo "@$inst"; } | entry claude "$HOME/.claude/CLAUDE.md"
{ echo "$mark"; cat "$dst/AGENTS.md"; [ -n "$inst" ] && printf '\nRead %s in full before any work: it binds this harness to this installation.\n' "$inst"; } | entry codex "$HOME/.codex/AGENTS.md"

# Claude Code: re-inject AGENTS and INSTANCE after compaction and resume.
[ -s "$f" ] || echo '{}' > "$f"
c=$dst/hooks/reload.sh
q="\"$c\""
jq --arg c "$c" --arg q "$q" '.hooks.SessionStart = ([.hooks.SessionStart[]? | select(.hooks[0].command != $c and .hooks[0].command != $q)]
  + [{matcher: "compact|resume", hooks: [{type: "command", command: $q}]}])' "$f" > "$f.tmp"
cat "$f.tmp" > "$f"
echo "installed into $dst"
