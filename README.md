# mcp-terminal-skill

A minimal, **safe** MCP (Model Context Protocol) server that lets an AI agent run a
small **allowlist** of read-only shell commands. No arbitrary shell. No writes.

## Why
DesktopCommander-style MCP servers grant broad terminal access. This one grants
*only* what you list — `ls`, `df`, `free`, `ps`, `ip`, `uptime`, `whoami`, `date`.
Anything else is refused. Good for demos, CI, or sandboxing an agent.

## Run
```
python3 mcp_terminal.py
```
Pipe MCP JSON-RPC (one JSON object per line) over stdin/stdout. Works with any
MCP client (Claude Desktop, etc.) configured for stdio.

## Protocol
- `initialize` → handshake
- `tools/list` → lists the 8 allowed commands
- `tools/call` → runs a listed command; refuses anything not in the allowlist

## Tested
```
initialize        -> ok
tools/list        -> 8 commands
tools/call uptime -> real output returned
tools/call sudo   -> REFUSED (not in allowlist)
```

## ☕ Support
Free and open. If it helped: https://www.paypal.com/paypalme/ddotson321
