"""todotxt"""

import argparse
import re
from dataclasses import dataclass, field

__version__ = "0.1.0"

DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TAG_PATTERN = re.compile(r"[@+]\S+")
REC_PATTERN = re.compile(r"rec:(\d+[dwmy])")


class TodotxtError(Exception):
    """Error parsing todotxt file."""


@dataclass
class Todo:
    title: str
    completed: bool = False
    date: str | None = None
    tags: list[str] = field(default_factory=list)
    description: str = ""
    rec: str | None = None


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
    rec_match = REC_PATTERN.search(line)
    rec = rec_match.group(1) if rec_match else None
    title = TAG_PATTERN.sub("", line)
    title = REC_PATTERN.sub("", title).strip()

    return Todo(title=title, completed=completed, date=date, tags=tags, rec=rec)


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
        if todo.rec:
            line += f" rec:{todo.rec}"
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
