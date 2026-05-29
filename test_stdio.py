"""Drive the server over a real MCP stdio session using the MCP client SDK."""

import asyncio
import os
import pathlib
import sys
import tempfile

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER = str(pathlib.Path(__file__).with_name("todo_server.py"))


async def main() -> None:
    tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
    tmp.close()
    os.remove(tmp.name)

    params = StdioServerParameters(
        command=sys.executable,          # same interpreter -> mcp is importable
        args=[SERVER],
        env={**os.environ, "TODO_DB": tmp.name},
    )

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            names = sorted(t.name for t in tools.tools)
            print("tools:", names)
            assert names == [
                "add_todo",
                "clear_completed_todos",
                "complete_todo",
                "list_todos",
                "remove_todo",
            ], names

            r = await session.call_tool("add_todo", {"text": "ship the MCP server"})
            print("add ->", r.content[0].text)

            r = await session.call_tool("list_todos", {})
            print("list ->", r.content[0].text)
            assert "ship the MCP server" in r.content[0].text

            r = await session.call_tool("complete_todo", {"id": 1})
            print("complete ->", r.content[0].text)

            r = await session.call_tool("list_todos", {})
            assert "[x] #1" in r.content[0].text, r.content[0].text

    os.path.exists(tmp.name) and os.remove(tmp.name)
    print("stdio OK")


asyncio.run(main())
