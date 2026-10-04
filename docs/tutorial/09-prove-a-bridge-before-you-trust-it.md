# Part 9: Prove a bridge before you trust it

*Part 9 of 12 · about 20 minutes · in this part: drive an MCP bridge directly over stdio, and verify by measuring instead of by "the call succeeded".*

MCP configuration is read when Claude starts, so you can't test a new bridge by calling its tools. Instead, drive the server yourself first: send `initialize`, then `notifications/initialized`, then `tools/list`, then a `tools/call`. It finds install problems while they are cheap to fix, and `tools/list` gives you the *real* tool names. They're namespaced (`gimp_new_image`, not `new_image`), and guessing from a README is how you lose an hour.

[`tools/mcp_probe.py`](../../tools/mcp_probe.py) does this with the standard library only. Against the GIMP bridge from part 7:

```sh
python3 tools/mcp_probe.py list -- uvx gimp-agent-mcp serve
```

```
server: gimp-agent-mcp
39 tools
  gimp_help
  ...
```

39, matching its README. GIMP stays running between calls, so we can launch headless, open the render from part 5, and read a pixel back:

```sh
python3 tools/mcp_probe.py call gimp_launch '{"mode":"headless"}' -- uvx gimp-agent-mcp serve
python3 tools/mcp_probe.py call gimp_open '{"path":"docs/img/mount-plate-iso.png"}' -- uvx gimp-agent-mcp serve
python3 tools/mcp_probe.py call gimp_measure '{"kind":"color","image_id":1,"x":5,"y":5}' -- uvx gimp-agent-mcp serve
```

The image came back 1400 × 1400, which is what the renderer writes, and pixel (5, 5) read `[18, 18, 20, 255]`, the exact background the renderer paints. **A value you knew in advance, read back through the bridge, matching:** that is the independent check.

## Verify by measuring

Both bridges will report success for a no-op. Through FreeCAD's live session we built an 80 × 60 × 8 plate, fused a Ø28 × 26 boss, and cut a Ø14 bore through both. The expected volume, worked out first as `80·60·8 + π·14²·26 − π·7²·34`:

```
EXPECTED 49175.7
ACTUAL   49175.7   solids=1 shells=1 valid=True faces=9
```

The same part through `execute_code_headless` gave 49175.7 again: two code paths and one hand calculation agreeing. That is the evidence. The tool saying "created" is not.

## Three differences between the bridges

- **Return convention.** FreeCAD's `execute_code` returns what you `print()` and silently drops a variable named `result`; GIMP's does the opposite. Probe with a one-liner first.
- **Object identity is explicit.** Neither bridge tracks the "focused document". Capture the id a create call returns and pass it along.
- **Both expose arbitrary code** (`execute_code`, `gimp_run_python`) with your permissions. Loopback is the right default.

## Check

- [ ] `mcp_probe.py list` shows the tool count the project's README promises.
- [ ] A value read back through the bridge matches one you worked out beforehand.
- [ ] Only now: restart Claude Code, and the tools appear natively.

---

**Next: [Part 10: What this setup cannot tell you](10-what-this-cannot-tell-you.md)**

[← Part 8: FreeCAD's live bridge](08-freecads-live-bridge.md) · [Series index](README.md)
