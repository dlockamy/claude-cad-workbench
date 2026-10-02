#!/usr/bin/env bash
# Install the FreeCAD MCP addon (neka-nat/freecad-mcp) into the directory FreeCAD
# itself reports — not into a path copied from a table.
#
#   ./tools/install-freecad-addon.sh                 install into FreeCAD's own Mod dir
#   ./tools/install-freecad-addon.sh --autostart     ...and start the RPC server on every launch
#   ./tools/install-freecad-addon.sh --dest DIR      install somewhere else (dry runs)
#
# --autostart sets "auto_start_rpc": true in freecad_mcp_settings.json (read from
# the addon's own source: InitGui.py + rpc_server/settings.py), which is what the
# "FreeCAD MCP -> Auto-Start Server" menu checkbox writes. It leaves every other
# setting alone — including the auth token and remote-connection switches.
set -euo pipefail

DEST="" AUTOSTART=0
while [ $# -gt 0 ]; do
  case "$1" in
    --dest) DEST="${2:?--dest needs a directory}"; shift 2 ;;
    --autostart) AUTOSTART=1; shift ;;
    *) echo "usage: $0 [--autostart] [--dest DIR]" >&2; exit 2 ;;
  esac
done

FC="$(command -v freecadcmd || command -v FreeCADCmd || true)"
[ -z "$FC" ] && [ -x /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd ] && FC=/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd
[ -n "$FC" ] || { echo "freecadcmd not found" >&2; exit 1; }

if [ -n "$DEST" ]; then
  MOD="$DEST"
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

if [ "$AUTOSTART" = 1 ]; then
  SETTINGS="$(dirname "$MOD")/freecad_mcp_settings.json"
  python3 - "$SETTINGS" <<'PY'
import json, os, sys
path = sys.argv[1]
cfg = json.load(open(path)) if os.path.exists(path) else {}
cfg["auto_start_rpc"] = True
json.dump(cfg, open(path, "w"), indent=2)
print("auto-start enabled →", path)
PY
  echo "restart FreeCAD; the RPC server starts by itself on 127.0.0.1:9875."
else
  echo "restart FreeCAD, select the 'MCP Addon' workbench, then tick FreeCAD MCP → Auto-Start Server"
  echo "(or re-run with --autostart to set that for you)."
fi
