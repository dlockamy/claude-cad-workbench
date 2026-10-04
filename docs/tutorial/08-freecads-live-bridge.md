# Part 8: FreeCAD's live bridge

*Part 8 of 12 · about 15 minutes · in this part: add a live FreeCAD window Claude can see, and decide deliberately about auto-start.*

[`neka-nat/freecad-mcp`](https://github.com/neka-nat/freecad-mcp) (MIT) gives Claude a live FreeCAD window: create objects, screenshot the viewport, run code. It is the most-used FreeCAD bridge, which is why we picked it. As with GIMP's, read the source before installing something built to run code on your machine.

## The one fact that decides how you use it

**This bridge needs the GUI open.** The addon runs inside FreeCAD and imports the GUI at module scope (`import FreeCADGui` on line 2 of `rpc_server.py`, checked in 0.1.25), so every tool dies when you close the window. A file named `test_headless.py` doesn't change that: it is a helper that shells out to `freecadcmd` for heavy jobs (`execute_code_headless`, useful because a native crash only kills the helper, not your session).

So the live bridge is for *looking*, never for unattended or CI work. That is the gap part 3's headless path already fills.

## Install the addon where FreeCAD says

```sh
./tools/install-freecad-addon.sh
```

The script asks FreeCAD for its data directory (part 2, trap 3), clones the addon, and copies it there. It never writes anywhere else, and `--dest` gives you a dry run. Then start FreeCAD, pick the *MCP Addon* workbench, and press *Start RPC Server*.

## Auto-start is a decision

A server you must click on every launch isn't automatable, so there is an opt-in: `./tools/install-freecad-addon.sh --autostart` writes `"auto_start_rpc": true` into `freecad_mcp_settings.json` and leaves everything else alone. Then the server comes up on `127.0.0.1:9875` within seconds of FreeCAD opening.

Think before you do that. The server has an `execute_code` tool: **arbitrary code with your user's permissions, on a port that exists whenever FreeCAD is open, with no auth token by default.** Loopback limits it to local processes, which is still every process on your machine. Our recommendation is **no auto-start**: start it per session, or set the addon's auth token if you want it always on. Never enable *Remote Connections* without a token.

## Register it

```sh
claude mcp add freecad -- uvx freecad-mcp --freecadcmd /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd
```

Pointing it at the real `freecadcmd` is what makes the headless tool work. Don't restart Claude yet: part 9 proves the bridge first.

## Check

- [ ] With the server running, FreeCAD's *MCP Addon* workbench shows it started.
- [ ] You made a deliberate choice about auto-start, and, if it is on, about the token.

---

**Next: [Part 9: Prove a bridge before you trust it](09-prove-a-bridge-before-you-trust-it.md)**

[← Part 7: The GIMP bridge](07-the-gimp-bridge.md) · [Series index](README.md)
