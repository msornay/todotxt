"""todotxt"""

import argparse
import calendar
import hashlib
import os
import re
import sys
from datetime import datetime, timedelta

__version__ = "0.1.0"


class TodotxtError(Exception):
    """Error parsing todotxt file."""


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
        total = date.month - 1 + amount
        year = date.year + total // 12
        month = total % 12 + 1
        day = min(date.day, calendar.monthrange(year, month)[1])
        date = date.replace(year=year, month=month, day=day)
    elif unit == "y":
        year = date.year + amount
        day = min(date.day, calendar.monthrange(year, date.month)[1])
        date = date.replace(year=year, day=day)
    return date.strftime("%Y-%m-%d")


def process_recurring_text(text):
    """Process text, appending new todos for completed recurring tasks.

    Works directly on text to preserve formatting (blank lines, etc.).

    For each completed task with rec: field, creates a new task unless
    one already exists with a _prev: hash pointing to it.

    Strict recurrence (e.g., "3w"): new due date based on old due date.
    Flexible recurrence (e.g., "+3w"): new due date based on done date.

    Raises TodotxtError if a done recurring task has no done: date.
    """
    # Find all existing _prev hashes
    existing_prev = set(re.findall(r"_prev:(\S+)", text))

    new_tasks = []

    # Match completed task lines (start with 'x ')
    for match in re.finditer(r"^x (.+)$", text, re.MULTILINE):
        line = match.group(1)

        rec_match = re.search(r"rec:(\+?\d+[dwmy])", line)
        if not rec_match:
            continue
        rec = rec_match.group(1)

        done_match = re.search(r"done:(\S+)", line)
        if not done_match:
            raise TodotxtError(
                f"Done recurring task missing done: date: {line}"
            )
        done_date = done_match.group(1)

        task_hash = hashlib.sha1(line.encode()).hexdigest()[:8]

        if task_hash in existing_prev:
            continue

        # Calculate new due date
        is_flexible = rec.startswith("+")
        if is_flexible:
            base_date = done_date
        else:
            due_match = re.search(r"due:(\S+)", line)
            base_date = due_match.group(1) if due_match else None

        new_due = _add_recurrence(base_date, rec)

        # Build new task: remove done:/due:, add _prev and new due
        new_line = re.sub(r"done:\S+", "", line).strip()
        new_line = re.sub(r"due:\S+", "", new_line).strip()
        new_line += f" _prev:{task_hash}"
        if new_due:
            new_line += f" due:{new_due}"

        new_tasks.append(new_line)

    if new_tasks:
        # Ensure text ends with newline before appending
        if text and not text.endswith("\n"):
            text += "\n"
        text += "\n".join(new_tasks) + "\n"

    return text


def find_past_due(text, today=None):
    """Find all incomplete tasks that are past due.

    Returns a list of lines that are past due.
    """
    if today is None:
        today = datetime.now().strftime("%Y-%m-%d")

    past_due = []

    for match in re.finditer(r"^(?!x )(\S.*)$", text, re.MULTILINE):
        line = match.group(1)

        due_match = re.search(r"due:(\d{4}-\d{2}-\d{2})", line)
        if not due_match:
            continue

        if due_match.group(1) <= today:
            past_due.append(line)

    return past_due


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", action="version", version=__version__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    # do-rec command
    do_rec = subparsers.add_parser("do-rec", help="Process recurring tasks")
    do_rec.add_argument("file", help="todo.txt file")
    do_rec.add_argument(
        "-o", "--output", type=argparse.FileType("w"), help="output file"
    )

    # due command
    due = subparsers.add_parser("due", help="Show tasks past due")
    due.add_argument(
        "path",
        nargs="?",
        default=".",
        help="file or folder (default: current directory)",
    )

    args = parser.parse_args()

    if args.command == "do-rec":
        with open(args.file) as f:
            text = f.read()
        text = process_recurring_text(text)
        output = args.output if args.output else sys.stdout
        output.write(text)

    elif args.command == "due":
        path = args.path
        if os.path.isfile(path):
            files = [path]
        else:
            files = []
            for root, _, filenames in os.walk(path):
                for filename in filenames:
                    files.append(os.path.join(root, filename))

        for filepath in files:
            try:
                with open(filepath) as f:
                    text = f.read()
                for line in find_past_due(text):
                    print(line)
            except (OSError, UnicodeDecodeError) as e:
                print(f"warning: {filepath}: {e}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
