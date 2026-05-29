# todo-mcp

A minimal [Model Context Protocol](https://modelcontextprotocol.io) server for
managing a personal TODO list. ~110 lines of Python: [FastMCP](https://github.com/modelcontextprotocol/python-sdk)
plus a flat JSON file for storage. No database, no build step.

## Tools

| Tool | Arguments | Description |
|------|-----------|-------------|
| `add_todo` | `text: str` | Add a new todo item |
| `list_todos` | `include_done: bool = True` | List todos (set `include_done=False` for open items only) |
| `complete_todo` | `id: int` | Mark a todo as done |
| `remove_todo` | `id: int` | Delete a todo |
| `clear_completed_todos` | – | Delete all completed todos |

## Storage

Todos are **per project**. The server writes `.todos.json` in its current
working directory, and an MCP stdio server is launched with its cwd set to the
project you started the client in — so each project keeps its own list:

```
~/code/app-a/.todos.json     # app-a's todos
~/code/app-b/.todos.json     # app-b's todos
```

Override the path with the `TODO_DB` environment variable (e.g. to force a
single shared list). IDs count up from the current maximum, so they never
collide after a removal.

Since `.todos.json` lands inside each project, add it to your **global**
gitignore so it never clutters `git status`:

```bash
echo '.todos.json' >> ~/.config/git/ignore
```

(Or commit it intentionally if you want project todos to travel with the repo.)

## Requirements

- Python 3.10+
- [`uv`](https://docs.astral.sh/uv/) (recommended) — or plain `pip`

## Install

```bash
git clone https://github.com/robert-johansson/todo-mcp.git
cd todo-mcp
```

### Register with Claude Code

With `uv` (dependencies are fetched and cached automatically — nothing to
install):

```bash
claude mcp add todo --scope user -- \
  uv run --with "mcp[cli]" python /absolute/path/to/todo-mcp/todo_server.py
```

`--scope user` makes the server available in every project. Drop it to register
only for the current project, or use `--scope project` to write a shared
`.mcp.json` into the repo.

Verify it connected:

```bash
claude mcp list   # todo: ... - ✓ Connected
```

MCP servers are loaded when a session starts, so **restart Claude Code** (or
start a new session) before the tools appear.

To remove it later:

```bash
claude mcp remove todo --scope user
```

### Use with other MCP clients

Any MCP client can launch it over stdio. The command is:

```
uv run --with "mcp[cli]" python /absolute/path/to/todo_server.py
```

For example, in a `claude_desktop_config.json` (Claude Desktop):

```json
{
  "mcpServers": {
    "todo": {
      "command": "uv",
      "args": ["run", "--with", "mcp[cli]", "python", "/absolute/path/to/todo_server.py"]
    }
  }
}
```

### Without `uv`

Install the dependency into a virtualenv and point the client at that
interpreter:

```bash
python -m venv .venv
.venv/bin/pip install "mcp[cli]"

claude mcp add todo --scope user -- /absolute/path/to/todo-mcp/.venv/bin/python /absolute/path/to/todo-mcp/todo_server.py
```

## Run the tests

```bash
uv run --with "mcp[cli]" python test_logic.py    # core logic against a temp DB
uv run --with "mcp[cli]" python test_stdio.py    # full MCP stdio round-trip
```

## Notes

- The stdio transport uses **stdout** for the JSON-RPC protocol stream, so the
  server only ever logs to stderr. If you extend it, never `print()` to stdout.
- Each tool is a thin wrapper over a plain helper function, so the logic is
  unit-testable without going through the transport.

## License

MIT
