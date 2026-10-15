#!/bin/sh
set -eu

repo=$(CDPATH= cd "$(dirname "$0")" && pwd -P)
opencode_config=${XDG_CONFIG_HOME:-"$HOME/.config"}/opencode
mkdir -p "$HOME/.codex/skills" "$HOME/.claude/skills" "$opencode_config/skills"

link_path() {
  if [ -L "$2" ] && [ "$(readlink "$2")" = "$1" ]; then
    return
  fi

  if [ -e "$2" ] || [ -L "$2" ]; then
    printf 'Cannot link %s: path already exists\n' "$2" >&2
    return 1
  fi

  ln -s "$1" "$2"
}

link_path "$repo/AGENTS.md" "$HOME/.codex/AGENTS.md"
link_path "$repo/AGENTS.md" "$HOME/.claude/CLAUDE.md"
link_path "$repo/AGENTS.md" "$opencode_config/AGENTS.md"

for skill_dir in "$repo"/*/; do
  [ -f "${skill_dir}SKILL.md" ] || continue
  skill=$(basename "$skill_dir")

  for skills_dir in "$HOME/.codex/skills" "$HOME/.claude/skills" "$opencode_config/skills"; do
    link_path "$skill_dir" "$skills_dir/$skill"
  done
done
