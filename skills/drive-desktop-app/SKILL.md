---
name: drive-desktop-app
description: Install, audit and verify an MCP bridge that lets Claude operate a real desktop application (GIMP, FreeCAD, a DAW). Use when a task needs to *operate* an app whose useful surface is far larger than its CLI, when choosing between competing bridges, or when a bridge is installed but its tools are missing, hung, or reporting success for no-ops.
---

# Drive a desktop app from Claude

Use a bridge when the app's useful surface is bigger than its CLI. **Don't** use
one for work a plain CLI already does (format conversion → ImageMagick; headless
part generation → the `parametric-cad-verify` skill). A bridge costs startup
latency, a running process and a local code-execution surface. Make it earn that.

## Procedure

1. **Pick on evidence, not the first search hit.** Most bridges are abandoned.
   ```sh
   for r in owner/repo-a owner/repo-b; do
     gh api repos/$r --jq '[.full_name,.stargazers_count,.pushed_at,.archived]|@tsv'
   done
   ```
   A big star gap plus a recent `pushed_at` usually settles it. Confirm by
   reading source, not the README.

2. **Audit before installing — it is local code execution.** That is the
   feature, but know what you are accepting:
   ```sh
   grep -rn "bind\|listen\|0\.0\.0\.0\|127\.0\.0\.1\|token\|secrets\." <pkg>/
   grep -rn "urlopen\|requests\.\|http[s]*://\|subprocess\|exec(\|eval(" <pkg>/
   ```
   Want: loopback-only bind, a per-install token, no outbound HTTP. Expect an
   `exec`-style endpoint. Tell the user both, plainly, before proceeding.

3. **Establish headless-vs-GUI before committing.** READMEs mislead here. A
   `headless` module can mean "a tool that shells out to a headless
   subprocess", not "a headless server". Look for GUI imports at module scope:
   ```sh
   grep -n "^import .*Gui\|getMainWindow\|QApplication" <addon>/*.py
   ```
   A module-level GUI import means the window must stay open and every tool
   dies when it closes. That decides whether the capability can run unattended.

4. **Install pinned, in isolation.** `uvx` is what most upstream docs assume; a
   dedicated venv works without installing anything globally, and the client
   config then points at the venv binary by absolute path. Check
   `requires-python` first — the system `python3` is often too old.

5. **Eliminate every manual UI step.** If the flow says "click Start Server",
   look for an autostart preference. A capability that needs a human click is
   not automatable.

6. **Wire tool paths explicitly.** A CLI shipped inside a macOS `.app` bundle is
   not on `PATH`; pass its full path as a server argument.

7. **Prove it over stdio before restarting the client.** MCP config is read at
   client startup, so you cannot test by calling the tools yet. Drive the server
   directly: `initialize` → `notifications/initialized` → `tools/list` →
   `tools/call`. Cheap to fix now, and it shows the real tool names.

8. **Verify by measuring, never by "the call succeeded".** Every bridge will
   report success for a no-op. Close the loop with the domain's own evidence,
   checked against an independent calculation:
   - geometry → read volume / solid count / bounding box back, compare to a
     hand-computed number
   - images → render back and *look*; measure pixels
   - documents → re-read the field you just wrote

## Gotchas

- **Tool names are namespaced** (`gimp_new_image`, not `new_image`). Read
  `tools/list`, don't guess from the README.
- **Scripting conventions don't transfer.** One bridge returns the value of a
  variable named `result`; another returns only `print()` output and silently
  discards `result`. Probe with a one-liner before a long script.
- **Pass object identity explicitly.** Bridges don't track "the focused
  document". Capture the id the create call returns and thread it through.
- **Validation errors are the fast path.** Typed bridges name the misspelled
  parameter exactly. Read the message.
- **`remove_*` may destroy, not detach.** To reorder, create in the right place.
- **The session is not durable.** A bridge process does not survive a reboot.
  Prefer one with an explicit relaunch tool, and test recovery by killing it.
- **The app's raw batch mode often just hangs** with no output and no exit. That
  is usually why the bridge exists. Use a timeout if you must try it.
- **The client must restart** before new MCP tools appear. Finish stdio
  verification first, then tell the user.

## Backend adapter

| | Raster — GIMP 3.2 via `gimp-agent-mcp` | CAD — FreeCAD via `neka-nat/freecad-mcp` |
|---|---|---|
| Headless server? | **Yes** — `gimp_launch(mode="headless")` | **No** — GUI addon; GUI must stay open |
| Transport | stdio → token-authed loopback TCP → in-app plugin | stdio → loopback XML-RPC `:9875` → GUI addon |
| Arbitrary code | `gimp_run_python` (returns `result`) | `execute_code` (returns `print()` output only) |
| Heavy/unattended | recipes, folder batching | `execute_code_headless` → shells out to `freecadcmd` |
| See the result | `gimp_render` | `get_view` / `include_screenshot` |
| Measure | `gimp_measure` | `execute_code` reading `Shape` properties |
| Discover API | `gimp_pdb_search`, `gimp_filter_search` | `get_objects`, FreeCAD Python API |
| Health | `gimp_status` | `get_rpc_status` |

When swapping a backend, ask in order: headless or not; what is the
code-execution convention; how do I *see* the result; how do I *measure* it.
A backend that can't answer the last two is a black box — step 8 becomes
impossible, so it isn't a substitute.
