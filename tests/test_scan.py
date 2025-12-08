"""Tests for scan_todotxt."""

from io import StringIO

import pytest

from todotxt import Todo, TodotxtError, scan_todotxt


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


def test_scan_todotxt_count(todo_file):
    """Test scanning returns correct number of todos."""
    todos = scan_todotxt(todo_file)
    assert len(todos) == 3


def test_scan_todotxt_titles(todo_file):
    """Test todo titles are parsed correctly."""
    todos = scan_todotxt(todo_file)
    assert todos[0].title == "Call Mom"
    assert todos[1].title == "Buy groceries"
    assert todos[2].title == "Write tests for todotxt"


def test_scan_todotxt_completed(todo_file):
    """Test completed status is parsed correctly."""
    todos = scan_todotxt(todo_file)
    assert todos[0].completed is False
    assert todos[1].completed is True
    assert todos[2].completed is False


def test_scan_todotxt_date(todo_file):
    """Test date is parsed correctly."""
    todos = scan_todotxt(todo_file)
    assert todos[0].date is None
    assert todos[1].date == "2024-01-15"
    assert todos[2].date is None


def test_scan_todotxt_tags(todo_file):
    """Test tags are parsed correctly."""
    todos = scan_todotxt(todo_file)
    assert todos[0].tags == ["@phone", "+family"]
    assert todos[1].tags == ["@errands"]
    assert todos[2].tags == ["+project"]


def test_scan_todotxt_description(todo_file):
    """Test description is parsed correctly."""
    todos = scan_todotxt(todo_file)
    assert todos[0].description == "Ask about her birthday plans"
    assert todos[1].description == ""
    assert todos[2].description == "Add fixture\nTest parsing"


def test_scan_todotxt_orphan_indented_line():
    """Test that indented line without parent todo raises error."""
    invalid_file = StringIO("  orphan indented line\n")
    with pytest.raises(TodotxtError):
        scan_todotxt(invalid_file)
