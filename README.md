# claude-cad-workbench

Skills, a CAD agent and a self-checking example for designing 3D-printable
parts with **Claude Code**, **FreeCAD** and **GIMP**.

The idea in one line: Claude writes the CAD as *code*, runs it headless, and the
code **fails loudly** when the geometry is wrong — so "it exported without an
error" is never the bar.

The long version, with the reasoning and the things that bit us, is the blog
post: *Setting up FreeCAD, GIMP and Claude to design 3D models*
(<https://dlockamy.com/blog/>).

![A mounting plate generated and verified by examples/mount-plate](docs/img/mount-plate-iso.png)

## Quick start

```sh
git clone https://github.com/dlockamy/claude-cad-workbench && cd claude-cad-workbench

./install.sh          # symlink the skills + agent into ~/.claude
./tools/doctor.sh     # read-only: what's installed, what's missing

# Prove the headless path works — no bridge, no GUI needed:
freecadcmd examples/mount-plate/mount_plate.py          # all checks pass, exit 0
MOUNT_PLATE_BREAK=1 freecadcmd examples/mount-plate/mount_plate.py   # must FAIL, exit 1
```

On macOS `freecadcmd` is at
`/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd`.

`install.sh` only ever replaces symlinks it created; it skips anything else
and tells you. `./install.sh --uninstall` removes exactly what it added.

Prefer not to touch `~/.claude`? The repo is also a Claude Code plugin
(`claude plugin validate .` passes):
`claude --plugin-dir /path/to/claude-cad-workbench` loads the skills and agent
for that session only.

## What's in here

| Path | What it is |
|---|---|
| `skills/parametric-cad-verify/` | Headless FreeCAD generation + the verification discipline, and the `freecadcmd` traps (exit codes, double-run, unflushed stdout). |
| `skills/drive-desktop-app/` | Choosing, auditing, installing and proving an MCP bridge to a desktop app. Headless-vs-GUI table for GIMP and FreeCAD. |
| `skills/raster-compositing/` | Layered, repeatable GIMP 3 images; what a raster editor can't do. |
| `skills/multi-material-print-handoff/` | CAD → a multi-colour slicer project. STL can't carry colour. |
| `agents/mechanical-cad-engineer.md` | A subagent that implements a part spec and won't call it done until it has read the geometry back. |
| `examples/mount-plate/` | The reference part. Build, verify, re-import, and a switch that breaks it on purpose. |
| `tools/doctor.sh` | Read-only environment check. |
| `tools/install-freecad-addon.sh` | Installs the FreeCAD MCP addon into the directory FreeCAD itself reports. |
| `tools/mcp_probe.py` | Stdlib-only stdio client: `initialize` → `tools/list` → `tools/call`, to prove a bridge before restarting Claude. |
| `tools/render_stl_iso.py` | ~100-line z-buffered STL preview (numpy + Pillow) for display-less machines. |
| `mcp/mcp.json.example` | A project-level `.mcp.json` for both bridges. |

The skills are real Claude Code skills (`SKILL.md` with frontmatter), so Claude
loads them when their description matches the task.

## The two MCP bridges (optional)

You do **not** need a bridge to generate parts — the headless path above does
that. A bridge adds a *live window*: seeing the model, or editing an image
interactively. Both are third-party projects; read their source before
installing, because each exists to run code on your machine.

| | GIMP | FreeCAD |
|---|---|---|
| Project | [`gimp-agent-mcp`](https://github.com/SarutobiSasuke8/gimp-agent-mcp) (Apache-2.0) | [`neka-nat/freecad-mcp`](https://github.com/neka-nat/freecad-mcp) (MIT) |
| Needs | GIMP 3.2.x, Python 3.11+, `uv` | FreeCAD, `uv`, Python 3.12+ for the server |
| Headless | **Yes** (`gimp_launch(mode="headless")`) | **No** — the GUI must stay open (`execute_code_headless` shells out to `freecadcmd` for heavy jobs) |
| Add to Claude Code | `claude mcp add gimp -- uvx gimp-agent-mcp serve` | `claude mcp add freecad -- uvx freecad-mcp --freecadcmd <path>` |

GIMP: `uvx gimp-agent-mcp install-plugin`, restart GIMP, then
*Filters → Development → Start Agent Bridge*.
FreeCAD: `./tools/install-freecad-addon.sh --autostart` (installs into the
directory FreeCAD itself reports and enables auto-start), then restart FreeCAD —
the RPC server comes up on `127.0.0.1:9875` with no clicks. Without
`--autostart`, pick the *MCP Addon* workbench and tick *Auto-Start Server* by hand.

**Security:** both bridges bind to loopback and expose an arbitrary-code
endpoint (`gimp_run_python`, `execute_code`) that runs with your user's
permissions. That is the feature. Only connect clients you trust, and don't turn
on the FreeCAD addon's *Remote Connections* without setting an auth token.

## Verified on

| Date | What | Where |
|---|---|---|
| 2026-10-02 | `mount_plate.py` (good + deliberately broken), `doctor.sh`, `install.sh`, `install-freecad-addon.sh --dest`, `render_stl_iso.py` | FreeCAD 1.0.2, macOS |
| 2026-10-02 | GIMP bridge 0.5.0: `install-plugin`, `doctor`, `smoke` (24 checks, headless), `mcp_probe.py` (39 tools; opened an image, read a pixel back to the known value) | GIMP 3.2.6, macOS |
| 2026-10-02 | Both bridges as native Claude Code tools after restart: committed STEP loaded live = 24957.05 mm³ (hand-computed 24957.05); GIMP pixel read-back and grid-overlay render |
| 2026-10-02 | FreeCAD bridge 0.1.25: addon installed with `--autostart`, 17 tools, plate+boss−bore volume 49175.7 mm³ vs hand-computed 49175.7 through both `execute_code` and `execute_code_headless`; `get_view` screenshot | FreeCAD 1.0.2, macOS |
| 2026-09-19 | `gimp-agent-mcp` 0.5.0 and `freecad-mcp` 0.1.24 driven over stdio; geometry read back and compared to a hand-computed volume | GIMP 3.2.6, FreeCAD 1.1.3, macOS |
| 2026-09-26 | Headless and GUI FreeCAD, GIMP batch, Bambu Studio | Flatpak GIMP 3.2.6 + FreeCAD 1.1.3, Ubuntu 24.04 |

Not claimed: Windows; GIMP 2.10 (unsupported by the bridge, and Python-Fu is
gone on current distros); anything about a slicer other than Bambu Studio.

## A real project that uses this

[`slash-builder/hw-2015-dial-panel`](https://github.com/slash-builder/hw-2015-dial-panel)
— a wall-mounted smart-home panel — generates all of its parts from one
parametric script with the same self-checking approach, then slices every plate
as a test.

## License

Apache-2.0. See [LICENSE](LICENSE). The bridges above are separate projects under
their own licenses.
