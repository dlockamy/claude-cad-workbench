# Part 8: FreeCAD's live bridge, and proving a bridge before you restart

**Goal:** add a live FreeCAD window Claude can see and drive, and prove it over stdio first. **Time:** 20 minutes.
**Needs:** the FreeCAD GUI, `uv`, Python 3.12+ for the server. **Previous:** [Part 7](07-the-gimp-bridge.md). **Next:** [Part 9](09-what-this-cannot-tell-you.md).

[`neka-nat/freecad-mcp`](https://github.com/neka-nat/freecad-mcp) (MIT) gives Claude a live FreeCAD window: create objects, screenshot the
viewport, run code. It is the most-used of the FreeCAD bridges (about 2,600 stars and an active push when checked in September), which is
why it was picked. Still read its source before installing anything that exists to execute code on your machine.

## The load-bearing fact: it needs the GUI open

The addon runs inside FreeCAD and imports the GUI at module scope. Line 2 of `rpc_server.py` is `import FreeCADGui` (checked in 0.1.25,
not just the 0.1.24 first audited), so **every tool dies when you close the window.** A file called `test_headless.py` does not mean the
server is headless: it is a tool that shells out to `freecadcmd` for heavy jobs (`execute_code_headless`, genuinely useful, because a
native OpenCascade crash only kills the helper and not your GUI session).

So: **the live bridge is for *looking*, never for unattended or CI work.** That is the gap [part 3](03-write-a-part-that-checks-itself.md)'s
headless path fills.

## Install the addon where FreeCAD says

```sh
freecadcmd -c "import os, FreeCAD; print(os.path.join(FreeCAD.getUserAppDataDir(), 'Mod'))"
```

Ask, because the table lies: the bridge's docs list a versioned directory for FreeCAD 1.0 on macOS, and on a 1.0.2 install FreeCAD
reported the plain unversioned one. [`tools/install-freecad-addon.sh`](../../tools/install-freecad-addon.sh) does the asking, clones the
addon, and copies it in. It never writes anywhere but where FreeCAD said, and takes `--dest` for a dry run.

```sh
./tools/install-freecad-addon.sh
```

## Auto-start is a decision, not a default

The RPC server only runs once someone clicks *Start RPC Server* in the *MCP Addon* workbench. A capability that needs a human click is not
automatable, so there is an opt-in: `./tools/install-freecad-addon.sh --autostart` writes `"auto_start_rpc": true` into
`freecad_mcp_settings.json` and leaves every other setting alone, including an auth token if you set one. With it, the server comes up on
`127.0.0.1:9875` a few seconds after FreeCAD opens, with no clicks.

**Think before turning it on.** That server has an `execute_code` tool: **arbitrary code, with your user's permissions, on a port that
exists every time FreeCAD is open, with no auth token by default.** Loopback-only limits it to local processes, which is still every
process on your machine. The conservative default, and the recommendation here, is **no auto-start**: start the
server per session, or set the addon's auth token if you want it always on. Do not enable *Remote Connections* without a token.

Register the bridge, pointing it at the real `freecadcmd` so the headless tool works:

```sh
claude mcp add freecad -- uvx freecad-mcp --freecadcmd /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd
```

## Prove it over stdio before you restart the client

MCP config is read when the client starts, so you cannot test a new bridge by calling its tools. Drive the server directly first: send
`initialize`, then `notifications/initialized`, then `tools/list`, then a `tools/call`. It finds every install problem while it is still
cheap to fix, and `tools/list` gives you the *real* tool names. They are namespaced (`gimp_new_image`, not `new_image`), and guessing from
the README is how you lose an hour.

[`tools/mcp_probe.py`](../../tools/mcp_probe.py) does exactly this with the standard library only. Against the GIMP bridge:

```sh
python3 tools/mcp_probe.py list -- uvx gimp-agent-mcp serve
```

```
server: gimp-agent-mcp
39 tools
  gimp_help
  gimp_status
  ...
```

39, matching the README. Because GIMP keeps running between calls, you can then launch headless, open the render from [part 5](05-look-at-the-part.md)
and read a pixel back:

```sh
python3 tools/mcp_probe.py call gimp_launch '{"mode":"headless"}' -- uvx gimp-agent-mcp serve
python3 tools/mcp_probe.py call gimp_open '{"path":"docs/img/mount-plate-iso.png"}' -- uvx gimp-agent-mcp serve
python3 tools/mcp_probe.py call gimp_measure '{"kind":"color","image_id":1,"x":5,"y":5}' -- uvx gimp-agent-mcp serve
```

The image came back 1400 × 1400, which is what the renderer writes, and the pixel at (5, 5) read `[18, 18, 20, 255]`, the exact background
colour the renderer paints. That is the independent check: **a value you knew in advance, read back through the bridge, matching.**

## Verify by measuring, never by "the call succeeded"

Both bridges will report success for a no-op. Driving FreeCAD's live session, the code built an 80 × 60 × 8 plate, fused a Ø28 × 26 boss, and
cut a Ø14 bore through both. The expected volume was computed separately, before running it, as `80·60·8 + π·14²·26 − π·7²·34`:

```
EXPECTED 49175.7
ACTUAL   49175.7   solids=1 shells=1 valid=True faces=9
```

The same part through `execute_code_headless` (a separate `freecadcmd` process) gave 49175.7 again: two code paths and one hand
calculation agreeing. That agreement is the evidence. The tool saying "created" is not.

## Three differences from the GIMP bridge that bite if you assume they do not exist

- **Different return convention.** FreeCAD's `execute_code` returns what you `print()` and silently discards a variable named `result`;
  GIMP's does the opposite. Probe with a one-liner before a long script.
- **Pass object identity explicitly.** Neither bridge tracks "the focused document". Capture the id the create call returns and thread it through.
- **Security.** Both expose an arbitrary-code endpoint (`execute_code`, `gimp_run_python`) with your user's permissions. They bind to
  loopback, which is the right default.

## Check

- [ ] `python3 tools/mcp_probe.py list -- uvx freecad-mcp --freecadcmd <path>` lists 17 tools with the FreeCAD window open.
- [ ] A volume read back through the bridge matches one you computed by hand.
- [ ] You made a deliberate choice about auto-start, and if it is on, about the auth token.
