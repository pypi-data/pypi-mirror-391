"""Tests for main hook logic."""

import json
from pathlib import Path

import pytest

from claude_hooks.main import (
    HOOK_CONFIG,
    create_hook_script,
    get_script_template,
    read_settings,
    update_hooks_config,
    write_settings,
)


@pytest.mark.unit
def test_get_script_template_on_edit():
    """Test script template generation for on_edit hook."""
    template = get_script_template("on_edit")
    assert "#!/bin/bash" in template
    assert "on_edit" in template
    assert "Edit tool" in template
    # PostToolUse hooks have comprehensive documentation
    assert "INPUT JSON SCHEMA:" in template
    assert "OUTPUT JSON SCHEMA:" in template
    assert "PostToolUse" in template
    assert "echo '{}'".replace("'", "") in template.replace("'", "")


@pytest.mark.unit
def test_get_script_template_on_stop():
    """Test script template generation for on_stop hook."""
    template = get_script_template("on_stop")
    assert "#!/bin/bash" in template
    assert "on_stop" in template
    assert "agent stops" in template


@pytest.mark.unit
def test_get_script_template_on_bash():
    """Test script template generation for on_bash hook."""
    template = get_script_template("on_bash")
    assert "#!/bin/bash" in template
    assert "on_bash" in template
    assert "Bash tool" in template


@pytest.mark.unit
def test_get_script_template_on_write():
    """Test script template generation for on_write hook."""
    template = get_script_template("on_write")
    assert "#!/bin/bash" in template
    assert "on_write" in template
    assert "Write tool" in template


@pytest.mark.unit
def test_get_script_template_on_multiedit():
    """Test script template generation for on_multiedit hook."""
    template = get_script_template("on_multiedit")
    assert "#!/bin/bash" in template
    assert "on_multiedit" in template
    assert "MultiEdit tool" in template


@pytest.mark.unit
def test_get_script_template_on_task_complete():
    """Test script template generation for on_task_complete hook."""
    template = get_script_template("on_task_complete")
    assert "#!/bin/bash" in template
    assert "on_task_complete" in template
    assert "Task tool" in template


@pytest.mark.unit
def test_get_script_template_on_ask_user():
    """Test script template generation for on_ask_user hook."""
    template = get_script_template("on_ask_user")
    assert "#!/bin/bash" in template
    assert "on_ask_user" in template
    assert "AskUserQuestion tool" in template


@pytest.mark.unit
def test_get_script_template_on_git_commit():
    """Test script template generation for on_git_commit hook."""
    template = get_script_template("on_git_commit")
    assert "#!/bin/bash" in template
    assert "on_git_commit" in template
    assert "Bash tool" in template


@pytest.mark.unit
def test_create_hook_script(tmp_path: Path):
    """Test hook script file creation."""
    hooks_dir = tmp_path / "hooks"
    hooks_dir.mkdir()

    script_path = create_hook_script("on_edit", hooks_dir)

    assert script_path.exists()
    assert script_path.name == "on_edit.sh"
    assert script_path.stat().st_mode & 0o111  # Check executable bit

    content = script_path.read_text()
    assert "#!/bin/bash" in content


@pytest.mark.unit
def test_read_settings_empty(tmp_path: Path):
    """Test reading non-existent settings file."""
    settings_path = tmp_path / "settings.local.json"
    settings = read_settings(settings_path)
    assert settings == {}


@pytest.mark.unit
def test_read_settings_existing(tmp_path: Path):
    """Test reading existing settings file."""
    settings_path = tmp_path / "settings.local.json"
    test_data = {"foo": "bar"}
    settings_path.write_text(json.dumps(test_data))

    settings = read_settings(settings_path)
    assert settings == test_data


@pytest.mark.unit
def test_write_settings(tmp_path: Path):
    """Test writing settings to file."""
    settings_path = tmp_path / "settings.local.json"
    test_data = {"foo": "bar", "nested": {"key": "value"}}

    write_settings(settings_path, test_data)

    assert settings_path.exists()
    saved_data = json.loads(settings_path.read_text())
    assert saved_data == test_data


@pytest.mark.unit
def test_update_hooks_config_new_hook():
    """Test adding new hook to empty settings."""
    settings = {}
    # Use relative path from cwd
    script_path = Path(".claude/hooks/on_edit.sh")

    result = update_hooks_config(settings, "on_edit", script_path)

    assert "hooks" in result
    assert "PostToolUse" in result["hooks"]
    assert len(result["hooks"]["PostToolUse"]) == 1

    hook_entry = result["hooks"]["PostToolUse"][0]
    assert hook_entry["matcher"] == "Edit"
    assert len(hook_entry["hooks"]) == 1
    assert hook_entry["hooks"][0]["type"] == "command"
    assert hook_entry["hooks"][0]["command"] == ".claude/hooks/on_edit.sh"


@pytest.mark.unit
def test_update_hooks_config_hook_without_matcher():
    """Test adding hook without matcher (Stop event)."""
    settings = {}
    # Use relative path from cwd
    script_path = Path(".claude/hooks/on_stop.sh")

    result = update_hooks_config(settings, "on_stop", script_path)

    assert "hooks" in result
    assert "Stop" in result["hooks"]
    assert len(result["hooks"]["Stop"]) == 1

    hook_entry = result["hooks"]["Stop"][0]
    assert "matcher" not in hook_entry
    assert len(hook_entry["hooks"]) == 1
    assert hook_entry["hooks"][0]["command"] == ".claude/hooks/on_stop.sh"


@pytest.mark.unit
def test_update_hooks_config_duplicate_hook(capsys):
    """Test that duplicate hooks are not added."""
    # Use relative path from cwd
    script_path = Path(".claude/hooks/on_edit.sh")
    settings = {
        "hooks": {
            "PostToolUse": [
                {
                    "matcher": "Edit",
                    "hooks": [
                        {"type": "command", "command": ".claude/hooks/on_edit.sh"}
                    ],
                }
            ]
        }
    }

    result = update_hooks_config(settings, "on_edit", script_path)

    # Should not add duplicate
    assert len(result["hooks"]["PostToolUse"]) == 1

    # Check console output
    captured = capsys.readouterr()
    assert "already exists" in captured.out


@pytest.mark.unit
def test_update_hooks_config_duplicate_hook_without_matcher(capsys):
    """Test that duplicate hooks without matcher are not added."""
    # Use relative path from cwd
    script_path = Path(".claude/hooks/on_stop.sh")
    settings = {
        "hooks": {
            "Stop": [
                {
                    "hooks": [
                        {"type": "command", "command": ".claude/hooks/on_stop.sh"}
                    ],
                }
            ]
        }
    }

    result = update_hooks_config(settings, "on_stop", script_path)

    # Should not add duplicate
    assert len(result["hooks"]["Stop"]) == 1

    # Check console output
    captured = capsys.readouterr()
    assert "already exists" in captured.out


@pytest.mark.unit
def test_hook_config_completeness():
    """Test that all hooks have required config keys."""
    for _hook_name, config in HOOK_CONFIG.items():
        assert "event" in config
        assert "matcher" in config  # Can be None
        assert "description" in config
