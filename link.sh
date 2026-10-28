#!/bin/sh
set -eu

repo=$(CDPATH= cd "$(dirname "$0")" && pwd -P)
opencode_config=${XDG_CONFIG_HOME:-"$HOME/.config"}/opencode
mkdir -p "$HOME/.codex/skills" "$HOME/.claude/skills" "$opencode_config/skills"

# Remove the links this repository created, so a skill that moved or was deleted
# heals on the next run instead of leaving a dead link behind.
unlink_repo_link() {
  [ -L "$1" ] || return 0

  case "$(readlink "$1")" in
    "$repo" | "$repo"/*) rm -f "$1" ;;
  esac
}

for dir in "$HOME/.codex/skills" "$HOME/.claude/skills" "$opencode_config/skills"; do
  for link in "$dir"/*; do
    unlink_repo_link "$link"
  done
done

unlink_repo_link "$HOME/.codex/AGENTS.md"
unlink_repo_link "$HOME/.claude/CLAUDE.md"
unlink_repo_link "$opencode_config/AGENTS.md"

link_path() {
  if [ -e "$2" ] || [ -L "$2" ]; then
    printf 'Cannot link %s: path already exists\n' "$2" >&2
    return 1
  fi

  ln -s "$1" "$2"
}

link_path "$repo/AGENTS.md" "$HOME/.codex/AGENTS.md"
link_path "$repo/AGENTS.md" "$HOME/.claude/CLAUDE.md"
link_path "$repo/AGENTS.md" "$opencode_config/AGENTS.md"

for skill_dir in "$repo"/skills/*/; do
  [ -f "${skill_dir}SKILL.md" ] || continue
  skill=$(basename "$skill_dir")

  for skills_dir in "$HOME/.codex/skills" "$HOME/.claude/skills" "$opencode_config/skills"; do
    link_path "$skill_dir" "$skills_dir/$skill"
  done
done
