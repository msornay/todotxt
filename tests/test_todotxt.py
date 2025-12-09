"""Tests for todotxt."""

import pytest

from todotxt import TodotxtError, process_recurring_text


def test_process_recurring_strict_creates_new_todo():
    """Test strict recurrence creates new todo based on due date."""
    text = "x Water plants rec:1w due:2024-01-15 done:2024-01-20\n"
    result = process_recurring_text(text)
    assert "Water plants rec:1w" in result
    assert "due:2024-01-22" in result  # Based on old due date
    assert "_prev:" in result


def test_process_recurring_flexible_creates_new_todo():
    """Test flexible recurrence creates new todo based on done date."""
    text = "x Water plants rec:+1w due:2024-01-15 done:2024-01-20\n"
    result = process_recurring_text(text)
    assert "Water plants rec:+1w" in result
    assert "due:2024-01-27" in result  # Based on done date
    assert "_prev:" in result


def test_process_recurring_skips_existing():
    """Test that process_recurring skips if _prev already exists."""
    text = "x Water plants rec:1w due:2024-01-15 done:2024-01-15\n"
    result = process_recurring_text(text)
    # Run again - should not create duplicate
    result2 = process_recurring_text(result)
    assert result2.count("Water plants") == 2


def test_process_recurring_ignores_non_recurring():
    """Test that process_recurring ignores non-recurring done todos."""
    text = "x Buy groceries done:2024-01-15\n"
    result = process_recurring_text(text)
    assert result == text


def test_process_recurring_ignores_incomplete():
    """Test that process_recurring ignores incomplete recurring todos."""
    text = "Water plants rec:1w due:2024-01-15\n"
    result = process_recurring_text(text)
    assert result == text


def test_process_recurring_error_missing_done_date():
    """Test that done recurring without done: date raises error."""
    text = "x Water plants rec:1w due:2024-01-15\n"
    with pytest.raises(TodotxtError):
        process_recurring_text(text)


def test_process_recurring_preserves_blank_lines():
    """Test that blank lines are preserved in output."""
    text = "Task one\n\nTask two\n\nx Water plants rec:1w due:2024-01-15 done:2024-01-20\n"
    result = process_recurring_text(text)
    # Original text should be preserved as-is
    assert result.startswith("Task one\n\nTask two\n")


def test_process_recurring_preserves_formatting():
    """Test that original formatting is preserved."""
    text = "x Water plants @garden rec:1w due:2024-01-15 done:2024-01-20\n"
    result = process_recurring_text(text)
    # Original line should be unchanged
    assert text in result
    # New task should have the tag
    lines = result.strip().split('\n')
    assert len(lines) == 2
    assert "@garden" in lines[1]


def test_process_recurring_meta_order_independent():
    """Test that meta field order doesn't matter."""
    # rec before done
    text1 = "x Water plants rec:1w done:2024-01-20 due:2024-01-15\n"
    result1 = process_recurring_text(text1)

    # done before rec
    text2 = "x Water plants done:2024-01-20 rec:1w due:2024-01-15\n"
    result2 = process_recurring_text(text2)

    # Both should create new tasks with same due date
    assert "due:2024-01-22" in result1
    assert "due:2024-01-22" in result2


def test_process_recurring_daily():
    """Test daily recurrence."""
    text = "x Task rec:3d due:2024-01-15 done:2024-01-15\n"
    result = process_recurring_text(text)
    assert "due:2024-01-18" in result


def test_process_recurring_monthly():
    """Test monthly recurrence."""
    text = "x Task rec:1m due:2024-01-15 done:2024-01-15\n"
    result = process_recurring_text(text)
    assert "due:2024-02-15" in result


def test_process_recurring_yearly():
    """Test yearly recurrence."""
    text = "x Task rec:1y due:2024-01-15 done:2024-01-15\n"
    result = process_recurring_text(text)
    assert "due:2025-01-15" in result


def test_process_recurring_no_trailing_newline():
    """Test handling of input without trailing newline."""
    text = "x Water plants rec:1w due:2024-01-15 done:2024-01-20"
    result = process_recurring_text(text)
    assert "due:2024-01-22" in result
    assert result.endswith('\n')


def test_process_recurring_empty_input():
    """Test handling of empty input."""
    result = process_recurring_text("")
    assert result == ""


def test_process_recurring_no_due_date_strict():
    """Test strict recurrence without due date produces no due in new task."""
    text = "x Water plants rec:1w done:2024-01-20\n"
    result = process_recurring_text(text)
    lines = result.strip().split('\n')
    assert len(lines) == 2
    assert "due:" not in lines[1]
