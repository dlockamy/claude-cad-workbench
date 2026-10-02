#!/usr/bin/env python3
"""Drive an MCP server over stdio by hand: initialize -> tools/list -> tools/call.

Do this BEFORE restarting your client. MCP config is read at client startup, so
you cannot test a new bridge by calling its tools; this finds every install
problem while it is still cheap, and shows the real (namespaced) tool names.

    mcp_probe.py list  -- uvx gimp-agent-mcp serve
    mcp_probe.py call gimp_status '{}' -- uvx gimp-agent-mcp serve
    mcp_probe.py list  -- uvx freecad-mcp --freecadcmd /path/to/freecadcmd

stdlib only. Messages are newline-delimited JSON-RPC 2.0.
"""
import json
import subprocess
import sys


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
            print(json.dumps(res.get("result", res), indent=2)[:4000])
        else:
            sys.exit(__doc__)
    finally:
        p.terminate()


main()
