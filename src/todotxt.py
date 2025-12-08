"""todotxt"""

import argparse
import hashlib
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta

__version__ = "0.1.0"

DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TAG_PATTERN = re.compile(r"[@+]\S+")
META_PATTERN = re.compile(r"(\w+):(\S+)")


class TodotxtError(Exception):
    """Error parsing todotxt file."""


@dataclass
class Todo:
    title: str
    completed: bool = False
    date: str | None = None
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
    completed = False
    date = None

    if line.startswith("x "):
        completed = True
        line = line[2:]
        parts = line.split(" ", 1)
        if parts and DATE_PATTERN.match(parts[0]):
            date = parts[0]
            line = parts[1] if len(parts) > 1 else ""

    tags = TAG_PATTERN.findall(line)
    meta = dict(META_PATTERN.findall(line))
    title = TAG_PATTERN.sub("", line)
    title = META_PATTERN.sub("", title).strip()

    return Todo(title=title, completed=completed, date=date, tags=tags, meta=meta)


def _todo_hash(todo):
    """Generate a short hash for a todo based on title."""
    return hashlib.sha1(todo.title.encode()).hexdigest()[:8]


def _add_recurrence(date_str, rec):
    """Add recurrence interval to a date string."""
    if not date_str:
        return None
    date = datetime.strptime(date_str, "%Y-%m-%d")
    amount = int(rec[:-1])
    unit = rec[-1]
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
    """Create new todos for completed recurring tasks.

    For each completed todo with a rec: meta field, creates a new uncompleted
    todo unless one already exists with a _prev: hash pointing to it.
    """
    existing_prev = {t.meta.get("_prev") for t in todos if "_prev" in t.meta}
    new_todos = []

    for todo in todos:
        if todo.completed and "rec" in todo.meta:
            todo_hash = _todo_hash(todo)
            if todo_hash not in existing_prev:
                new_date = _add_recurrence(todo.date, todo.meta["rec"])
                new_todo = Todo(
                    title=todo.title,
                    completed=False,
                    date=new_date,
                    tags=list(todo.tags),
                    description=todo.description,
                    meta={"rec": todo.meta["rec"], "_prev": todo_hash},
                )
                new_todos.append(new_todo)

    return todos + new_todos


def write_todotxt(file, todos):
    """Write a list of Todo objects to a file."""
    for todo in todos:
        line = ""
        if todo.completed:
            line += "x "
            if todo.date:
                line += f"{todo.date} "
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
    parser.add_argument("file", type=argparse.FileType("r"), help="todo.txt file")

    args = parser.parse_args()

    read_todotxt(args.file)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
