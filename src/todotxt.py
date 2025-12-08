"""todotxt"""

import argparse
import hashlib
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta

__version__ = "0.1.0"

TAG_PATTERN = re.compile(r"@\S+")
META_PATTERN = re.compile(r"(\w+):(\S+)")


class TodotxtError(Exception):
    """Error parsing todotxt file."""


@dataclass
class Todo:
    title: str
    done: bool = False
    tags: list[str] = field(default_factory=list)
    description: str = ""
    meta: dict[str, str] = field(default_factory=dict)


def read_todotxt(file):
    """Read a todo.txt file and return list of Todo objects."""
    todos = []
    current = None

    for line in file:
        if line.startswith("  "):
            if current is None:
                raise TodotxtError("Invalid todotxt: indented line without todo")
            if current.description:
                current.description += "\n"
            current.description += line[2:].rstrip()
        elif line.strip():
            current = _parse_todo_line(line.rstrip())
            todos.append(current)
        else:
            current = None

    return todos


def _parse_todo_line(line):
    """Parse a single todo line into a Todo object."""
    done = False

    if line.startswith("x "):
        done = True
        line = line[2:]

    tags = TAG_PATTERN.findall(line)
    meta = dict(META_PATTERN.findall(line))
    title = TAG_PATTERN.sub("", line)
    title = META_PATTERN.sub("", title).strip()

    return Todo(title=title, done=done, tags=tags, meta=meta)


def _todo_hash(todo):
    """Generate a short hash for a todo based on title."""
    return hashlib.sha1(todo.title.encode()).hexdigest()[:8]


def _add_recurrence(date_str, rec):
    """Add recurrence interval to a date string.

    rec can be strict (e.g., "3w") or flexible (e.g., "+3w").
    Returns the new date string.
    """
    if not date_str:
        return None
    date = datetime.strptime(date_str, "%Y-%m-%d")
    # Strip + prefix for flexible recurrence (handled by caller)
    rec_value = rec.lstrip("+")
    amount = int(rec_value[:-1])
    unit = rec_value[-1]
    if unit == "d":
        date += timedelta(days=amount)
    elif unit == "w":
        date += timedelta(weeks=amount)
    elif unit == "m":
        date = date.replace(month=date.month + amount)
    elif unit == "y":
        date = date.replace(year=date.year + amount)
    return date.strftime("%Y-%m-%d")


def process_recurring(todos):
    """Create new todos for done recurring tasks.

    For each done todo with a rec: meta field, creates a new todo
    unless one already exists with a _prev: hash pointing to it.

    Strict recurrence (e.g., "3w"): new due date based on old due date.
    Flexible recurrence (e.g., "+3w"): new due date based on done date.

    Raises TodotxtError if a done recurring task has no done: date.
    """
    existing_prev = {t.meta.get("_prev") for t in todos if "_prev" in t.meta}
    new_todos = []

    for todo in todos:
        if todo.done and "rec" in todo.meta:
            if "done" not in todo.meta:
                raise TodotxtError(
                    f"Done recurring task missing done: date: {todo.title}"
                )
            todo_hash = _todo_hash(todo)
            if todo_hash not in existing_prev:
                rec = todo.meta["rec"]
                is_flexible = rec.startswith("+")
                base_date = (
                    todo.meta.get("done") if is_flexible
                    else todo.meta.get("due")
                )
                new_due = _add_recurrence(base_date, rec)
                new_meta = {"rec": rec, "_prev": todo_hash}
                if new_due:
                    new_meta["due"] = new_due
                new_todo = Todo(
                    title=todo.title,
                    done=False,
                    tags=list(todo.tags),
                    description=todo.description,
                    meta=new_meta,
                )
                new_todos.append(new_todo)

    return todos + new_todos


def write_todotxt(file, todos):
    """Write a list of Todo objects to a file."""
    for todo in todos:
        line = ""
        if todo.done:
            line += "x "
        line += todo.title
        if todo.tags:
            line += " " + " ".join(todo.tags)
        for key, value in todo.meta.items():
            line += f" {key}:{value}"
        file.write(line + "\n")
        if todo.description:
            for desc_line in todo.description.split("\n"):
                file.write(f"  {desc_line}\n")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", action="version", version=__version__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    # do-rec command
    do_rec = subparsers.add_parser("do-rec", help="Process recurring tasks")
    do_rec.add_argument("file", type=argparse.FileType("r"), help="todo.txt file")
    do_rec.add_argument(
        "-o", "--output", type=argparse.FileType("w"), help="output file"
    )

    args = parser.parse_args()

    if args.command == "do-rec":
        todos = read_todotxt(args.file)
        todos = process_recurring(todos)
        output = args.output if args.output else sys.stdout
        write_todotxt(output, todos)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
