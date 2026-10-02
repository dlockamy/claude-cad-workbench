#!/usr/bin/env bash
# Install the FreeCAD MCP addon (neka-nat/freecad-mcp) into the directory FreeCAD
# itself reports — not into a path copied from a table.
#
#   ./tools/install-freecad-addon.sh              install into FreeCAD's own Mod dir
#   ./tools/install-freecad-addon.sh --dest DIR   install somewhere else (dry runs)
#
# You still do two things by hand, once, inside FreeCAD:
#   1. pick the "MCP Addon" workbench
#   2. FreeCAD MCP menu → tick "Auto-Start Server"
set -euo pipefail

FC="$(command -v freecadcmd || command -v FreeCADCmd || true)"
[ -z "$FC" ] && [ -x /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd ] && FC=/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd
[ -n "$FC" ] || { echo "freecadcmd not found" >&2; exit 1; }

if [ "${1:-}" = "--dest" ]; then
  MOD="${2:?--dest needs a directory}"
else
  MOD="$("$FC" -c "import os; print('MOD=' + os.path.join(FreeCAD.getUserAppDataDir(), 'Mod'))" 2>&1 | sed -n 's/^MOD=//p')"
  [ -n "$MOD" ] || { echo "could not ask FreeCAD for its addon directory" >&2; exit 1; }
fi

TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
git clone --quiet --depth 1 https://github.com/neka-nat/freecad-mcp.git "$TMP/freecad-mcp"
[ -f "$TMP/freecad-mcp/addon/FreeCADMCP/InitGui.py" ] || { echo "unexpected addon layout upstream" >&2; exit 1; }

mkdir -p "$MOD"
rm -rf "$MOD/FreeCADMCP"                     # no second FreeCADMCP level inside it
cp -R "$TMP/freecad-mcp/addon/FreeCADMCP" "$MOD/FreeCADMCP"
echo "installed addon → $MOD/FreeCADMCP"
echo "restart FreeCAD, select the 'MCP Addon' workbench, then tick FreeCAD MCP → Auto-Start Server."
