#!/usr/bin/env bash
# Read-only check of the whole setup. Changes nothing. Exit 1 if anything required is missing.
ok()   { printf '  \033[32mok\033[0m    %s\n' "$*"; }
miss() { printf '  \033[31mMISSING\033[0m %s\n' "$*"; BAD=1; }
note() { printf '  --    %s\n' "$*"; }
BAD=0

echo "FreeCAD (headless)"
FC="$(command -v freecadcmd || command -v FreeCADCmd || true)"
[ -z "$FC" ] && [ -x /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd ] && FC=/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd
if [ -n "$FC" ]; then
  ver="$("$FC" --version 2>&1 | grep -m1 '^FreeCAD' || true)"; ok "freecadcmd: $FC  ($ver)"
  mod="$("$FC" -c "import os; print('MOD=' + os.path.join(FreeCAD.getUserAppDataDir(), 'Mod'))" 2>&1 | sed -n 's/^MOD=//p')"
  [ -n "$mod" ] && note "addon directory: $mod"
  [ -d "$mod/FreeCADMCP" ] && ok "FreeCAD MCP addon installed" || note "FreeCAD MCP addon not installed (only needed for the live-GUI bridge)"
else
  miss "freecadcmd not found (install FreeCAD; the GUI install includes the CLI)"
fi

echo "GIMP 3 (only needed for raster work)"
gv=""
[ -d /Applications/GIMP.app ] && gv="$(defaults read /Applications/GIMP.app/Contents/Info CFBundleShortVersionString 2>/dev/null)"
[ -z "$gv" ] && command -v flatpak >/dev/null && gv="$(flatpak info org.gimp.GIMP 2>/dev/null | sed -n 's/^ *Version: *//p')"
[ -z "$gv" ] && command -v gimp >/dev/null && gv="$(gimp --version 2>/dev/null | awk '{print $NF}')"
case "$gv" in
  3.*) ok "GIMP $gv" ;;
  "")  note "GIMP not found" ;;
  *)   miss "GIMP $gv — the bridge needs GIMP 3.2.x (2.10 is unsupported)" ;;
esac

echo "Tooling"
command -v uvx    >/dev/null && ok "uv/uvx: $(uv --version 2>&1)" || miss "uv not found (https://docs.astral.sh/uv/) — both bridges launch through uvx"
command -v claude >/dev/null && ok "claude: $(claude --version 2>&1 | head -1)" || miss "Claude Code not found"

echo "MCP bridges registered with Claude Code"
if command -v claude >/dev/null; then
  list="$(claude mcp list 2>&1 || true)"
  echo "$list" | grep -qi 'gimp'    && ok "gimp configured"    || note "gimp not configured    →  claude mcp add gimp -- uvx gimp-agent-mcp serve"
  echo "$list" | grep -qi 'freecad' && ok "freecad configured" || note "freecad not configured →  claude mcp add freecad -- uvx freecad-mcp --freecadcmd \"$FC\""
fi

echo "Installed skills/agent"
for s in drive-desktop-app parametric-cad-verify raster-compositing multi-material-print-handoff; do
  [ -e "$HOME/.claude/skills/$s/SKILL.md" ] && ok "skill $s" || note "skill $s not installed (./install.sh)"
done
[ -e "$HOME/.claude/agents/mechanical-cad-engineer.md" ] && ok "agent mechanical-cad-engineer" || note "agent not installed (./install.sh)"

exit $BAD
