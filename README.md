# todotxt

![Tests](https://github.com/msornay/todotxt/actions/workflows/test.yml/badge.svg)

custom flavor of todotxt

## Syntax

```
x Title text @tag key:value
  Description line (indented 2 spaces)
```

### Done marker

Lines starting with `x ` are marked as done.

### Tags

Words starting with `@` are tags (e.g., `@home`, `@work`).

### Meta fields

Key-value pairs in `key:value` format:

| Field | Description |
|-------|-------------|
| `due:YYYY-MM-DD` | Due date |
| `done:YYYY-MM-DD` | Completion date |
| `rec:Nunit` | Strict recurrence (from due date) |
| `rec:+Nunit` | Flexible recurrence (from done date) |

Recurrence units: `d` (days), `w` (weeks), `m` (months), `y` (years).

### Description

Lines indented with 2 spaces belong to the preceding todo.

### Example

```
Call Mom @phone due:2024-01-20
  Ask about birthday plans

x Buy groceries @errands done:2024-01-15

Water plants @home rec:+1w due:2024-01-15
```

## Installation

```bash
poetry install
```

## Usage

### Show past-due tasks

```bash
todotxt due todo.txt        # single file
todotxt due ~/todos/        # scan a directory
```

### Process recurring tasks

```bash
todotxt do-rec todo.txt           # print to stdout
todotxt do-rec todo.txt -o out.txt  # write to file
```

For each completed task with a `rec:` field, appends a new occurrence with an
updated `due:` date and a `_prev:` hash linking back to the original.

## Development

### Running tests

```bash
make test
```

### Linting and formatting

```bash
make lint
```
