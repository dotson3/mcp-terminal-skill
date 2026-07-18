#!/usr/bin/env python3
"""
mcp_terminal.py — a minimal, SAFE MCP (Model Context Protocol) server that lets
an AI agent run a small allowlist of read-only shell commands.

Implements just enough of the MCP stdio JSON-RPC protocol to be useful:
  - initialize
  - tools/list        -> lists the safe commands
  - tools/call        -> runs a listed command (blocked otherwise)

SAFETY: only commands in ALLOWED run. No arbitrary shell. No writes.
Pipe JSON-RPC over stdin/stdout (one JSON object per line).

Stdlib only. Python 3.8+.
"""
import json, os, subprocess, sys

ALLOWED = {
    "list_files":   ["ls", "-la"],
    "disk_usage":   ["df", "-h"],
    "mem_info":     ["free", "-h"],
    "processes":    ["ps", "aux"],
    "network":      ["ip", "addr"],
    "uptime":       ["uptime"],
    "whoami":       ["whoami"],
    "date":         ["date"],
}

def handle(req):
    method = req.get("method")
    rid = req.get("id")
    if method == "initialize":
        return {"jsonrpc": "2.0", "id": rid, "result": {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "safe-terminal", "version": "1.0"}}}
    if method == "tools/list":
        tools = [{"name": k, "description": "Safe read-only: " + " ".join(v),
                  "inputSchema": {"type": "object", "properties": {}}}
                 for k, v in ALLOWED.items()]
        return {"jsonrpc": "2.0", "id": rid, "result": {"tools": tools}}
    if method == "tools/call":
        params = req.get("params", {})
        name = params.get("name")
        if name not in ALLOWED:
            return {"jsonrpc": "2.0", "id": rid, "result": {
                "content": [{"type": "text", "text": f"REFUSED: '{name}' not in allowlist"}],
                "isError": True}}
        try:
            out = subprocess.run(ALLOWED[name], capture_output=True, text=True, timeout=10)
            text = (out.stdout or "") + (out.stderr or "")
            return {"jsonrpc": "2.0", "id": rid, "result": {
                "content": [{"type": "text", "text": text or "(no output)"}]}}
        except Exception as e:
            return {"jsonrpc": "2.0", "id": rid, "result": {
                "content": [{"type": "text", "text": f"ERROR: {e}"}], "isError": True}}
    return {"jsonrpc": "2.0", "id": rid, "error": {"code": -32601, "message": "method not found"}}

def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue
        resp = handle(req)
        if resp:
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
