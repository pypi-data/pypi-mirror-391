"""Tests for CLI argument parsing."""

import pytest

from claude_hooks.cli import parse_args


@pytest.mark.unit
def test_parse_args_add_hook():
    """Test parsing add command with hook name."""
    args = parse_args(["add", "on_edit"])
    assert args.command == "add"
    assert args.hook_name == "on_edit"


@pytest.mark.unit
def test_parse_args_add_on_todo_complete():
    """Test parsing add command with on_todo_complete."""
    args = parse_args(["add", "on_todo_complete"])
    assert args.command == "add"
    assert args.hook_name == "on_todo_complete"


@pytest.mark.unit
def test_parse_args_add_on_stop():
    """Test parsing add command with on_stop."""
    args = parse_args(["add", "on_stop"])
    assert args.command == "add"
    assert args.hook_name == "on_stop"


@pytest.mark.unit
def test_parse_args_add_on_start():
    """Test parsing add command with on_start."""
    args = parse_args(["add", "on_start"])
    assert args.command == "add"
    assert args.hook_name == "on_start"


@pytest.mark.unit
def test_parse_args_invalid_hook():
    """Test that invalid hook name raises error."""
    with pytest.raises(SystemExit):
        parse_args(["add", "invalid_hook"])


@pytest.mark.unit
def test_parse_args_no_command():
    """Test that no command sets command to None."""
    args = parse_args([])
    assert args.command is None
