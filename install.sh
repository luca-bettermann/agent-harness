#!/bin/sh
# Install agent-harness for the current account (Claude Code and Codex).
# Usage: install.sh [path/to/INSTANCE.md]   (remembered for later runs)
# Rerun after updating the checkout. Moves a foreign entry file aside as *.pre-harness.
set -eu
src=$(cd "$(dirname "$0")" && pwd)
dst=$HOME/.agent-harness
inst=${1:-$(cat "$dst/instance-path" 2>/dev/null || true)}

# Build: AGENTS, hook, knowledge, and the skills with their addenda appended.
rm -rf "$dst.new"
mkdir -p "$dst.new/skills"
cp -r "$src/AGENTS.md" "$src/hooks" "$src/knowledge" "$dst.new/"
for d in "$src"/upstream/skills/engineering/*/ "$src"/upstream/skills/productivity/*/ "$src"/engineering/*/; do
  n=$(basename "$d")
  [ "$n" = addenda ] && continue
  cp -r "$d" "$dst.new/skills/$n"
  a="$src/engineering/addenda/$n.md"
  if [ -f "$a" ]; then printf '\n' >> "$dst.new/skills/$n/SKILL.md"; cat "$a" >> "$dst.new/skills/$n/SKILL.md"; fi
done
[ -n "$inst" ] && echo "$inst" > "$dst.new/instance-path"
rm -rf "$dst"
mv "$dst.new" "$dst"

link() {
  if [ -e "$2" ] && [ ! -L "$2" ]; then echo "skipped $2: a file not made by this install" >&2; return; fi
  ln -sfn "$1" "$2"
}
mkdir -p "$HOME/.claude/skills" "$HOME/.codex/skills"
for s in "$dst"/skills/*/; do
  n=$(basename "$s")
  link "$dst/skills/$n" "$HOME/.claude/skills/$n"
  link "$dst/skills/$n" "$HOME/.codex/skills/$n"
done
find "$HOME/.claude/skills" "$HOME/.codex/skills" -maxdepth 1 -xtype l -delete
# Entry points: AGENTS plus the installation's INSTANCE.
mark='<!-- written by agent-harness install.sh -->'
entry() {
  if [ -L "$1" ]; then rm "$1"
  elif [ -e "$1" ] && ! grep -qF "$mark" "$1"; then mv "$1" "$1.pre-harness"; echo "moved $1 to $1.pre-harness" >&2; fi
  cat > "$1"
}
{ echo "$mark"; echo "@$dst/AGENTS.md"; [ -n "$inst" ] && echo "@$inst"; } | entry "$HOME/.claude/CLAUDE.md"
{ echo "$mark"; cat "$dst/AGENTS.md"; [ -n "$inst" ] && printf '\nRead %s in full before any work: it binds this harness to this installation.\n' "$inst"; } | entry "$HOME/.codex/AGENTS.md"

# Claude Code: re-inject AGENTS after compaction and resume.
f=$HOME/.claude/settings.json
[ -f "$f" ] || echo '{}' > "$f"
c=$dst/hooks/reload.sh
jq --arg c "$c" '.hooks.SessionStart = ([.hooks.SessionStart[]? | select(.hooks[0].command != $c)]
  + [{matcher: "compact|resume", hooks: [{type: "command", command: $c}]}])' "$f" > "$f.tmp"
cat "$f.tmp" > "$f"
rm "$f.tmp"
echo "installed into $dst"
