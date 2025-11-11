"""Utility functions for llmshell."""

import subprocess
import sys
from typing import Optional, Tuple
from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint


console = Console()


def print_success(message: str) -> None:
    """
    Print success message.

    Args:
        message: Message to print
    """
    console.print(f"[green]✓[/green] {message}")


def print_error(message: str) -> None:
    """
    Print error message.

    Args:
        message: Message to print
    """
    console.print(f"[red]✗[/red] {message}", style="red")


def print_warning(message: str) -> None:
    """
    Print warning message.

    Args:
        message: Message to print
    """
    console.print(f"[yellow]⚠[/yellow] {message}", style="yellow")


def print_info(message: str) -> None:
    """
    Print info message.

    Args:
        message: Message to print
    """
    console.print(f"[blue]ℹ[/blue] {message}", style="blue")


def print_command(command: str, title: str = "Generated Command") -> None:
    """
    Print command with syntax highlighting.

    Args:
        command: Command to display
        title: Panel title
    """
    syntax = Syntax(command, "bash", theme="monokai", line_numbers=False)
    panel = Panel(syntax, title=title, border_style="cyan")
    console.print(panel)


def print_config_table(config_dict: dict, title: str = "Configuration") -> None:
    """
    Print configuration as a table.

    Args:
        config_dict: Configuration dictionary
        title: Table title
    """
    table = Table(title=title, show_header=True, header_style="bold cyan")
    table.add_column("Key", style="cyan", no_wrap=True)
    table.add_column("Value", style="white")

    def flatten_dict(d: dict, parent_key: str = "") -> dict:
        """Flatten nested dictionary."""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}.{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(flatten_dict(v, new_key).items())
            else:
                items.append((new_key, v))
        return dict(items)

    flat_config = flatten_dict(config_dict)
    for key, value in flat_config.items():
        # Mask sensitive values
        if any(sensitive in key.lower() for sensitive in ["key", "token", "password"]):
            if value and value is not None:
                display_value = "****" + str(value)[-4:] if len(str(value)) > 4 else "****"
            else:
                display_value = "[dim]not set[/dim]"
        else:
            display_value = str(value) if value is not None else "[dim]not set[/dim]"
        
        table.add_row(key, display_value)

    console.print(table)


def print_backend_status(backends: list) -> None:
    """
    Print backend status table.

    Args:
        backends: List of tuples (name, available, status)
    """
    table = Table(title="Backend Status", show_header=True, header_style="bold cyan")
    table.add_column("Backend", style="cyan", no_wrap=True)
    table.add_column("Status", style="white")
    table.add_column("Details", style="dim")

    for name, available, status in backends:
        status_icon = "[green]✓ Available[/green]" if available else "[red]✗ Unavailable[/red]"
        table.add_row(name, status_icon, status)

    console.print(table)


def confirm_execution(command: str) -> bool:
    """
    Ask user to confirm command execution.

    Args:
        command: Command to execute

    Returns:
        True if user confirms, False otherwise
    """
    print_command(command, "Command to Execute")
    
    response = console.input("\n[yellow]Execute this command?[/yellow] [dim](y/n)[/dim]: ")
    return response.lower() in ["y", "yes"]


def execute_command(command: str, dry_run: bool = False) -> Tuple[int, str, str]:
    """
    Execute shell command.

    Args:
        command: Command to execute
        dry_run: If True, don't actually execute

    Returns:
        Tuple of (return_code, stdout, stderr)
    """
    if dry_run:
        print_info(f"Dry run mode - command not executed: {command}")
        return (0, "", "")

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
        )
        return (result.returncode, result.stdout, result.stderr)
    except subprocess.TimeoutExpired:
        return (1, "", "Command timed out after 30 seconds")
    except Exception as e:
        return (1, "", str(e))


def print_execution_result(returncode: int, stdout: str, stderr: str) -> None:
    """
    Print command execution result.

    Args:
        returncode: Command return code
        stdout: Standard output
        stderr: Standard error
    """
    if returncode == 0:
        print_success("Command executed successfully")
        if stdout:
            console.print("\n[bold]Output:[/bold]")
            console.print(stdout)
    else:
        print_error(f"Command failed with exit code {returncode}")
        if stderr:
            console.print("\n[bold red]Error:[/bold red]")
            console.print(stderr, style="red")
        if stdout:
            console.print("\n[bold]Output:[/bold]")
            console.print(stdout)


def check_command_exists(command: str) -> bool:
    """
    Check if a command exists in PATH.

    Args:
        command: Command name to check

    Returns:
        True if command exists, False otherwise
    """
    try:
        result = subprocess.run(
            ["which", command],
            capture_output=True,
            text=True,
        )
        return result.returncode == 0
    except Exception:
        return False


def get_shell_type() -> str:
    """
    Detect current shell type.

    Returns:
        Shell name (bash, zsh, fish, etc.)
    """
    shell = subprocess.run(
        ["echo", "$SHELL"],
        capture_output=True,
        text=True,
        shell=True,
    )
    shell_path = shell.stdout.strip()
    
    if "zsh" in shell_path:
        return "zsh"
    elif "bash" in shell_path:
        return "bash"
    elif "fish" in shell_path:
        return "fish"
    else:
        return "unknown"


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted size string
    """
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def is_dangerous_command(command: str) -> bool:
    """
    Check if command is potentially dangerous.

    Args:
        command: Command to check

    Returns:
        True if command is dangerous, False otherwise
    """
    dangerous_patterns = [
        "rm -rf /",
        "rm -rf /*",
        "mkfs",
        "dd if=/dev/zero",
        "> /dev/sda",
        ":(){ :|:& };:",  # Fork bomb
        "chmod -R 777 /",
    ]
    
    command_lower = command.lower().strip()
    
    for pattern in dangerous_patterns:
        if pattern in command_lower:
            return True
    
    return False


def print_danger_warning(command: str) -> None:
    """
    Print warning for dangerous command.

    Args:
        command: Dangerous command
    """
    console.print(
        "\n[bold red]⚠️  WARNING: POTENTIALLY DANGEROUS COMMAND ⚠️[/bold red]\n",
        style="on red"
    )
    console.print(
        "This command may cause system damage or data loss.\n"
        "Please review it carefully before execution.\n",
        style="bold yellow"
    )
    print_command(command, "⚠️  Dangerous Command")
