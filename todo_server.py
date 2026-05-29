"""A minimal TODO MCP server.

Storage is a flat JSON file (~/.todos.json by default; override with $TODO_DB).
Each tool is a thin wrapper over a plain helper function so the logic stays
unit-testable without going through the MCP transport.
"""

import json
import os
import pathlib

from mcp.server.fastmcp import FastMCP

DB = pathlib.Path(os.environ.get("TODO_DB", pathlib.Path.home() / ".todos.json"))

mcp = FastMCP("todo")


# --- storage -------------------------------------------------------------

def _load() -> list[dict]:
    if DB.exists():
        return json.loads(DB.read_text())
    return []


def _save(todos: list[dict]) -> None:
    DB.write_text(json.dumps(todos, indent=2))


def _next_id(todos: list[dict]) -> int:
    return max((t["id"] for t in todos), default=0) + 1


def _render(todos: list[dict]) -> str:
    if not todos:
        return "No todos."
    return "\n".join(
        f"[{'x' if t['done'] else ' '}] #{t['id']} {t['text']}" for t in todos
    )


# --- core logic (testable, transport-agnostic) ---------------------------

def add(text: str) -> str:
    todos = _load()
    todo = {"id": _next_id(todos), "text": text, "done": False}
    todos.append(todo)
    _save(todos)
    return f"Added #{todo['id']}: {text}"


def show(include_done: bool = True) -> str:
    todos = _load()
    if not include_done:
        todos = [t for t in todos if not t["done"]]
    return _render(todos)


def complete(id: int) -> str:
    todos = _load()
    for t in todos:
        if t["id"] == id:
            t["done"] = True
            _save(todos)
            return f"Completed #{id}: {t['text']}"
    return f"No todo with id #{id}."


def remove(id: int) -> str:
    todos = _load()
    kept = [t for t in todos if t["id"] != id]
    if len(kept) == len(todos):
        return f"No todo with id #{id}."
    _save(kept)
    return f"Removed #{id}."


def clear_completed() -> str:
    todos = _load()
    kept = [t for t in todos if not t["done"]]
    removed = len(todos) - len(kept)
    _save(kept)
    return f"Cleared {removed} completed todo(s)."


# --- MCP tools (thin wrappers) -------------------------------------------

@mcp.tool()
def add_todo(text: str) -> str:
    """Add a new todo item."""
    return add(text)


@mcp.tool()
def list_todos(include_done: bool = True) -> str:
    """List todos. Set include_done=False to show only open items."""
    return show(include_done)


@mcp.tool()
def complete_todo(id: int) -> str:
    """Mark the todo with the given id as done."""
    return complete(id)


@mcp.tool()
def remove_todo(id: int) -> str:
    """Delete the todo with the given id."""
    return remove(id)


@mcp.tool()
def clear_completed_todos() -> str:
    """Delete all todos that are marked done."""
    return clear_completed()


if __name__ == "__main__":
    mcp.run()  # stdio transport
