"""Tests for scan_todotxt."""

from io import StringIO

import pytest

from todotxt import scan_todotxt


@pytest.fixture
def todo_file():
    return StringIO(
        "Call Mom @phone +family\n"
        "  Ask about her birthday plans\n"
        "x 2024-01-15 Buy groceries @errands\n"
        "\n"
        "Write tests for todotxt +project\n"
        "  Add fixture\n"
        "  Test parsing\n"
    )


def test_scan_todotxt(todo_file):
    """Test scanning a todo.txt file."""
    scan_todotxt(todo_file)
