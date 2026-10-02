#!/usr/bin/env bash
# Install the skills and the CAD agent into ~/.claude so every Claude Code
# session can use them. Symlinks by default, so `git pull` updates them.
#
#   ./install.sh              symlink skills + agent into ~/.claude
#   ./install.sh --copy       copy instead of symlink
#   ./install.sh --uninstall  remove what this script installed
#
# Set CLAUDE_HOME to target a different directory (used by the tests).
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST="${CLAUDE_HOME:-$HOME/.claude}"
MODE=link
case "${1:-}" in
  --copy) MODE=copy ;;
  --uninstall) MODE=uninstall ;;
  "") ;;
  *) echo "usage: $0 [--copy|--uninstall]" >&2; exit 2 ;;
esac

put() {  # put <src> <dst>
  local src="$1" dst="$2"
  if [ "$MODE" = uninstall ]; then
    # Only remove symlinks into this checkout (a --copy install is removed by hand).
    if [ -L "$dst" ] && [[ "$(readlink "$dst")" == "$HERE"/* ]]; then rm -f "$dst"; echo "removed  $dst"; fi
    return
  fi
  mkdir -p "$(dirname "$dst")"
  # Never clobber something we did not put there: a real file/dir, or a symlink
  # that points anywhere other than into this checkout.
  if [ -L "$dst" ]; then
    case "$(readlink "$dst")" in
      "$HERE"/*) ;;                                  # ours — safe to replace
      *) echo "SKIP     $dst is a symlink to $(readlink "$dst") — not ours; move it aside first" >&2; return ;;
    esac
  elif [ -e "$dst" ]; then
    echo "SKIP     $dst exists and is not a symlink — move it aside first" >&2; return
  fi
  rm -f "$dst"
  if [ "$MODE" = copy ]; then cp -R "$src" "$dst"; else ln -s "$src" "$dst"; fi
  echo "$MODE  $dst"
}

for s in "$HERE"/skills/*/; do
  name="$(basename "$s")"
  put "${s%/}" "$DEST/skills/$name"
done
for a in "$HERE"/agents/*.md; do
  put "$a" "$DEST/agents/$(basename "$a")"
done

[ "$MODE" = uninstall ] && exit 0
cat <<MSG

Done — see any SKIP lines above. Target: $DEST
Next: ./tools/doctor.sh   (checks FreeCAD, GIMP, uv, and the MCP bridges)
MSG
