#!/bin/sh
# Install agent-harness for the current account (Claude Code and Codex).
# Rerun after updating the checkout. Never replaces a file it did not create.
set -eu
src=$(cd "$(dirname "$0")" && pwd)
dst=$HOME/.agent-harness

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
link "$dst/AGENTS.md" "$HOME/.claude/CLAUDE.md"
link "$dst/AGENTS.md" "$HOME/.codex/AGENTS.md"

# Claude Code: re-inject AGENTS after compaction and resume.
f=$HOME/.claude/settings.json
[ -f "$f" ] || echo '{}' > "$f"
c=$dst/hooks/reload.sh
jq --arg c "$c" '.hooks.SessionStart = ([.hooks.SessionStart[]? | select(.hooks[0].command != $c)]
  + [{matcher: "compact|resume", hooks: [{type: "command", command: $c}]}])' "$f" > "$f.tmp"
cat "$f.tmp" > "$f"
rm "$f.tmp"
echo "installed into $dst"
