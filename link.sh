#!/bin/sh
set -eu

repo=$(CDPATH= cd "$(dirname "$0")" && pwd -P)
opencode_config=${XDG_CONFIG_HOME:-"$HOME/.config"}/opencode
antigravity_config="$HOME/.gemini/config"
mkdir -p "$HOME/.codex/skills" "$HOME/.claude/skills" "$opencode_config/skills" "$antigravity_config/skills"

# Remove the links this repository created, so a skill that moved or was deleted
# heals on the next run instead of leaving a dead link behind.
unlink_repo_link() {
  [ -L "$1" ] || return 0

  case "$(readlink "$1")" in
    "$repo" | "$repo"/*) rm -f "$1" ;;
  esac
}

link_path() {
  if [ -e "$2" ] || [ -L "$2" ]; then
    printf 'Cannot link %s: path already exists\n' "$2" >&2
    return 1
  fi

  ln -s "$1" "$2"
}

for dir in "$HOME/.codex/skills" "$HOME/.claude/skills" "$opencode_config/skills" "$antigravity_config/skills"; do
  for link in "$dir"/*; do
    unlink_repo_link "$link"
  done
done

for file in "$HOME/.codex/AGENTS.md" "$HOME/.claude/CLAUDE.md" "$opencode_config/AGENTS.md" "$antigravity_config/AGENTS.md"; do
  unlink_repo_link "$file"
  link_path "$repo/AGENTS.md" "$file"
done

for skill_dir in "$repo"/skills/*/; do
  [ -f "${skill_dir}SKILL.md" ] || continue
  skill=$(basename "$skill_dir")

  for skills_dir in "$HOME/.codex/skills" "$HOME/.claude/skills" "$opencode_config/skills" "$antigravity_config/skills"; do
    link_path "$skill_dir" "$skills_dir/$skill"
  done
done
