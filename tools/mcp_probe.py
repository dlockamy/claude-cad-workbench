#!/usr/bin/env python3
"""Drive an MCP server over stdio by hand: initialize -> tools/list -> tools/call.

Do this BEFORE restarting your client. MCP config is read at client startup, so
you cannot test a new bridge by calling its tools; this finds every install
problem while it is still cheap, and shows the real (namespaced) tool names.

    mcp_probe.py list  -- uvx gimp-agent-mcp serve
    mcp_probe.py call gimp_status '{}' -- uvx gimp-agent-mcp serve
    mcp_probe.py list  -- uvx freecad-mcp --freecadcmd /path/to/freecadcmd

Text results are printed (long ones truncated). Image results are decoded and
written to files -- under $MCP_PROBE_OUT, or a fresh temp dir -- and the path is
printed, because a base64 screenshot in a terminal is just noise.

stdlib only. Messages are newline-delimited JSON-RPC 2.0.
"""
import base64
import json
import os
import subprocess
import sys
import tempfile


def show(res):
    if "result" not in res:
        print(json.dumps(res, indent=2)[:4000])
        return
    result = res["result"]
    if result.get("isError"):
        print("isError: true")
    out = os.environ.get("MCP_PROBE_OUT") or tempfile.mkdtemp(prefix="mcp_probe_")
    os.makedirs(out, exist_ok=True)
    for i, c in enumerate(result.get("content", [])):
        if c.get("type") == "image":
            ext = (c.get("mimeType") or "image/png").split("/")[-1]
            path = os.path.join(out, "image_%d.%s" % (i, ext))
            with open(path, "wb") as f:
                f.write(base64.b64decode(c["data"]))
            print("image saved: %s" % path)
        elif c.get("type") == "text":
            text = c["text"]
            print(text if len(text) <= 4000 else text[:4000] + "\n... [truncated %d chars]" % (len(text) - 4000))
        else:
            print(json.dumps(c)[:500])


def main():
    argv = sys.argv[1:]
    if "--" not in argv or not argv:
        sys.exit(__doc__)
    split = argv.index("--")
    mode_args, cmd = argv[:split], argv[split + 1:]
    mode = mode_args[0]

    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         stderr=subprocess.DEVNULL, text=True, bufsize=1)
    n = 0

    def send(method, params=None, notify=False):
        nonlocal n
        msg = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            msg["params"] = params
        if not notify:
            n += 1
            msg["id"] = n
        p.stdin.write(json.dumps(msg) + "\n")
        p.stdin.flush()
        if notify:
            return None
        while True:                      # skip server notifications until our reply
            line = p.stdout.readline()
            if not line:
                sys.exit("server closed the connection")
            reply = json.loads(line)
            if reply.get("id") == n:
                return reply

    try:
        init = send("initialize", {"protocolVersion": "2024-11-05", "capabilities": {},
                                   "clientInfo": {"name": "mcp_probe", "version": "0.1"}})
        info = init["result"]["serverInfo"]
        print("server: %s %s" % (info.get("name"), info.get("version", "")))
        send("notifications/initialized", notify=True)

        tools = send("tools/list", {})["result"]["tools"]
        if mode == "list":
            print("%d tools" % len(tools))
            for t in tools:
                print("  " + t["name"])
        elif mode == "call":
            name = mode_args[1]
            args = json.loads(mode_args[2]) if len(mode_args) > 2 else {}
            if name not in {t["name"] for t in tools}:
                sys.exit("no such tool %r (tools are namespaced -- try `list`)" % name)
            res = send("tools/call", {"name": name, "arguments": args})
            show(res)
        else:
            sys.exit(__doc__)
    finally:
        p.terminate()


main()
