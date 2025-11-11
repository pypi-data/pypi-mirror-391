"""Tests for utility functions."""

import pytest
from unittest.mock import Mock, patch
from gpt_shell.utils import (
    is_dangerous_command,
    execute_command,
    check_command_exists,
    format_file_size,
)


class TestDangerousCommands:
    """Tests for dangerous command detection."""

    def test_dangerous_rm_rf(self):
        """Test detection of rm -rf /."""
        assert is_dangerous_command("rm -rf /")
        assert is_dangerous_command("sudo rm -rf /")

    def test_dangerous_mkfs(self):
        """Test detection of mkfs."""
        assert is_dangerous_command("mkfs.ext4 /dev/sda1")

    def test_dangerous_dd(self):
        """Test detection of dangerous dd."""
        assert is_dangerous_command("dd if=/dev/zero of=/dev/sda")

    def test_safe_commands(self):
        """Test that safe commands are not flagged."""
        assert not is_dangerous_command("ls -la")
        assert not is_dangerous_command("docker ps")
        assert not is_dangerous_command("grep 'pattern' file.txt")

    def test_safe_rm(self):
        """Test that safe rm commands are not flagged."""
        assert not is_dangerous_command("rm file.txt")
        assert not is_dangerous_command("rm -rf ./temp")


class TestExecuteCommand:
    """Tests for command execution."""

    def test_execute_simple_command(self):
        """Test executing a simple command."""
        returncode, stdout, stderr = execute_command("echo 'test'")
        assert returncode == 0
        assert "test" in stdout

    def test_execute_dry_run(self):
        """Test dry run mode."""
        returncode, stdout, stderr = execute_command("echo 'test'", dry_run=True)
        assert returncode == 0
        assert stdout == ""

    def test_execute_invalid_command(self):
        """Test executing invalid command."""
        returncode, stdout, stderr = execute_command("nonexistentcommand12345")
        assert returncode != 0


class TestCheckCommand:
    """Tests for command existence checking."""

    def test_existing_command(self):
        """Test checking for existing command."""
        assert check_command_exists("ls")
        assert check_command_exists("echo")

    def test_nonexistent_command(self):
        """Test checking for non-existent command."""
        assert not check_command_exists("nonexistentcommand12345")


class TestFormatFileSize:
    """Tests for file size formatting."""

    def test_bytes(self):
        """Test bytes formatting."""
        assert format_file_size(100) == "100.0 B"

    def test_kilobytes(self):
        """Test kilobytes formatting."""
        assert format_file_size(1024) == "1.0 KB"

    def test_megabytes(self):
        """Test megabytes formatting."""
        assert format_file_size(1024 * 1024) == "1.0 MB"

    def test_gigabytes(self):
        """Test gigabytes formatting."""
        assert format_file_size(1024 * 1024 * 1024) == "1.0 GB"

    def test_mixed_size(self):
        """Test mixed size formatting."""
        assert "MB" in format_file_size(1024 * 1024 * 1.5)
