"""Exercise the core logic against a throwaway DB (no MCP transport)."""

import os
import tempfile

# point storage at a temp file BEFORE importing the module
_tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
_tmp.close()
os.environ["TODO_DB"] = _tmp.name
os.remove(_tmp.name)  # start with no file at all

import todo_server as t

assert t.show() == "No todos.", t.show()
assert t.add("write the report") == "Added #1: write the report"
assert t.add("call the bank") == "Added #2: call the bank"
assert t.complete(1) == "Completed #1: write the report"

out = t.show()
assert out == "[x] #1 write the report\n[ ] #2 call the bank", repr(out)

assert t.show(include_done=False) == "[ ] #2 call the bank", t.show(include_done=False)
assert t.complete(99) == "No todo with id #99."
assert t.remove(2) == "Removed #2."
assert t.remove(2) == "No todo with id #99.".replace("99", "2")

# ids keep counting up off the max, so they don't collide after removals
assert t.add("third item") == "Added #2: third item"
assert t.complete(2).startswith("Completed #2")
# #1 was completed earlier and never removed, so 2 done items remain here
assert t.clear_completed() == "Cleared 2 completed todo(s)."
assert t.show() == "No todos."

os.remove(os.environ["TODO_DB"])
print("logic OK")
