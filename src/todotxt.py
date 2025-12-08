"""todotxt"""

import argparse
import re
from dataclasses import dataclass, field

__version__ = "0.1.0"

DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TAG_PATTERN = re.compile(r"[@+]\S+")


class TodotxtError(Exception):
    """Error parsing todotxt file."""


@dataclass
class Todo:
    title: str
    completed: bool = False
    date: str | None = None
    tags: list[str] = field(default_factory=list)
    description: str = ""


def scan_todotxt(file):
    """Scan a todo.txt file and return list of Todo objects."""
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
    title = TAG_PATTERN.sub("", line).strip()

    return Todo(title=title, completed=completed, date=date, tags=tags)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument("file", type=argparse.FileType("r"), help="todo.txt file")

    args = parser.parse_args()

    scan_todotxt(args.file)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
