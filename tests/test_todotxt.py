"""Tests for read_todotxt."""

from io import StringIO

import pytest

from todotxt import Todo, TodotxtError, read_todotxt, write_todotxt


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


def test_read_todotxt_count(todo_file):
    """Test scanning returns correct number of todos."""
    todos = read_todotxt(todo_file)
    assert len(todos) == 3


def test_read_todotxt_titles(todo_file):
    """Test todo titles are parsed correctly."""
    todos = read_todotxt(todo_file)
    assert todos[0].title == "Call Mom"
    assert todos[1].title == "Buy groceries"
    assert todos[2].title == "Write tests for todotxt"


def test_read_todotxt_completed(todo_file):
    """Test completed status is parsed correctly."""
    todos = read_todotxt(todo_file)
    assert todos[0].completed is False
    assert todos[1].completed is True
    assert todos[2].completed is False


def test_read_todotxt_date(todo_file):
    """Test date is parsed correctly."""
    todos = read_todotxt(todo_file)
    assert todos[0].date is None
    assert todos[1].date == "2024-01-15"
    assert todos[2].date is None


def test_read_todotxt_tags(todo_file):
    """Test tags are parsed correctly."""
    todos = read_todotxt(todo_file)
    assert todos[0].tags == ["@phone", "+family"]
    assert todos[1].tags == ["@errands"]
    assert todos[2].tags == ["+project"]


def test_read_todotxt_description(todo_file):
    """Test description is parsed correctly."""
    todos = read_todotxt(todo_file)
    assert todos[0].description == "Ask about her birthday plans"
    assert todos[1].description == ""
    assert todos[2].description == "Add fixture\nTest parsing"


def test_read_todotxt_orphan_indented_line():
    """Test that indented line without parent todo raises error."""
    invalid_file = StringIO("  orphan indented line\n")
    with pytest.raises(TodotxtError):
        read_todotxt(invalid_file)


def test_read_todotxt_rec_none(todo_file):
    """Test rec is None when not specified."""
    todos = read_todotxt(todo_file)
    assert all(todo.rec is None for todo in todos)


def test_read_todotxt_rec_daily():
    """Test parsing daily recurrence."""
    f = StringIO("Water plants rec:3d\n")
    todos = read_todotxt(f)
    assert todos[0].rec == "3d"
    assert todos[0].title == "Water plants"


def test_read_todotxt_rec_weekly():
    """Test parsing weekly recurrence."""
    f = StringIO("Weekly review rec:1w @work\n")
    todos = read_todotxt(f)
    assert todos[0].rec == "1w"


def test_read_todotxt_rec_monthly():
    """Test parsing monthly recurrence."""
    f = StringIO("Pay rent rec:1m\n")
    todos = read_todotxt(f)
    assert todos[0].rec == "1m"


def test_read_todotxt_rec_yearly():
    """Test parsing yearly recurrence."""
    f = StringIO("Birthday reminder rec:1y\n")
    todos = read_todotxt(f)
    assert todos[0].rec == "1y"


def test_roundtrip(todo_file):
    """Test that read followed by write produces the same todos."""
    todos = read_todotxt(todo_file)
    output = StringIO()
    write_todotxt(output, todos)
    output.seek(0)
    todos_roundtrip = read_todotxt(output)
    assert todos == todos_roundtrip
