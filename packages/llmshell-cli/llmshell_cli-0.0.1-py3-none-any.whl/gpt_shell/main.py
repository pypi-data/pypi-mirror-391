"""Main CLI interface for llmshell using Typer."""

import typer
from typing import Optional
from pathlib import Path

from gpt_shell import __version__
from gpt_shell.config import Config
from gpt_shell.llm_manager import LLMManager
from gpt_shell.utils import (
    print_success,
    print_error,
    print_warning,
    print_info,
    print_command,
    print_config_table,
    print_backend_status,
    confirm_execution,
    execute_command,
    print_execution_result,
    is_dangerous_command,
    print_danger_warning,
    console,
)

app = typer.Typer(
    name="llmshell",
    help="Convert natural language to shell commands using LLMs",
    add_completion=False,
)


def get_manager() -> LLMManager:
    """Get LLM manager instance."""
    config = Config()
    return LLMManager(config)


@app.command(name="run")
def run_command(
    prompt: str = typer.Argument(..., help="Natural language description of command"),
    execute: bool = typer.Option(False, "--execute", "-e", help="Execute command without confirmation"),
    dry_run: bool = typer.Option(False, "--dry-run", "-d", help="Show command but don't execute"),
    explain: bool = typer.Option(False, "--explain", "-x", help="Include explanation with command"),
    backend: Optional[str] = typer.Option(None, "--backend", "-b", help="Specific backend to use"),
):
    """Generate and optionally execute shell commands from natural language."""
    try:
        manager = get_manager()
        
        # Generate command
        with console.status("[cyan]Thinking...", spinner="dots"):
            command = manager.generate_command(prompt, explain=explain, backend=backend)
        
        # Display generated command
        if explain:
            console.print("\n[bold cyan]Response:[/bold cyan]")
            console.print(command)
        else:
            print_command(command)
        
        # Show which backend was used
        current_backend = manager.get_current_backend()
        if current_backend:
            print_info(f"Using backend: {current_backend}")
        
        # Check for dangerous commands
        is_dangerous = is_dangerous_command(command)
        if is_dangerous:
            print_danger_warning(command)
        
        # Handle execution
        if not dry_run and not explain:
            should_execute = execute
            
            # For dangerous commands, ALWAYS ask for confirmation
            if is_dangerous:
                should_execute = False  # Force confirmation for dangerous commands
                print_warning("Dangerous command detected - confirmation required regardless of --execute flag")
            
            if not should_execute:
                # Ask for confirmation
                config = Config()
                if not config.get("execution.confirmation_required", True) and not is_dangerous:
                    should_execute = True
                else:
                    should_execute = confirm_execution(command)
            
            if should_execute:
                console.print()
                returncode, stdout, stderr = execute_command(command)
                print_execution_result(returncode, stdout, stderr)
        elif dry_run:
            print_info("Dry run mode - command not executed")
    
    except RuntimeError as e:
        print_error(str(e))
        raise typer.Exit(code=1)
    except KeyboardInterrupt:
        print_warning("Interrupted by user")
        raise typer.Exit(code=130)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        raise typer.Exit(code=1)


@app.command(name="config")
def config_command(
    action: Optional[str] = typer.Argument(None, help="Action: show, set, get"),
    key: Optional[str] = typer.Argument(None, help="Configuration key"),
    value: Optional[str] = typer.Argument(None, help="Configuration value"),
):
    """Manage llmshell configuration."""
    config = Config()
    
    if action is None or action == "show":
        # Show current configuration
        print_config_table(config.to_dict())
        console.print(f"\n[dim]Config file: {config.config_path}[/dim]")
    
    elif action == "set":
        if not key or value is None:
            print_error("Usage: llmshell config set KEY VALUE")
            raise typer.Exit(code=1)
        
        # Set configuration value
        try:
            # Try to parse as boolean or number
            if value.lower() in ["true", "false"]:
                value = value.lower() == "true"
            elif value.isdigit():
                value = int(value)
            elif value.replace(".", "", 1).isdigit():
                value = float(value)
            
            config.set(key, value)
            print_success(f"Set {key} = {value}")
            print_info(f"Config saved to {config.config_path}")
        except Exception as e:
            print_error(f"Failed to set config: {e}")
            raise typer.Exit(code=1)
    
    elif action == "get":
        if not key:
            print_error("Usage: llmshell config get KEY")
            raise typer.Exit(code=1)
        
        # Get configuration value
        value = config.get(key)
        if value is not None:
            console.print(f"[cyan]{key}[/cyan] = {value}")
        else:
            print_warning(f"Key '{key}' not found")
            raise typer.Exit(code=1)
    
    else:
        print_error(f"Unknown action: {action}")
        print_info("Available actions: show, set, get")
        raise typer.Exit(code=1)


@app.command(name="model")
def model_command(
    action: str = typer.Argument(..., help="Action: install, list, show-available"),
    model_name: Optional[str] = typer.Option(None, "--name", "-n", help="Model name to install"),
):
    """Manage GPT4All models."""
    if action == "install":
        try:
            manager = get_manager()
            
            if model_name:
                print_info(f"Installing model: {model_name}")
            else:
                config = Config()
                model_name = config.get("backends.gpt4all.model", "mistral-7b-instruct-v0.2.Q4_0.gguf")
                print_info(f"Installing default model: {model_name}")
            
            model_path = manager.download_gpt4all_model(model_name)
            print_success(f"Model installed successfully: {model_path}")
            
        except Exception as e:
            print_error(f"Failed to install model: {e}")
            raise typer.Exit(code=1)
    
    elif action == "list":
        config = Config()
        models_dir = config.get_models_dir()
        
        if models_dir.exists():
            models = list(models_dir.glob("*.gguf"))
            if models:
                console.print("\n[bold cyan]Installed Models:[/bold cyan]")
                for model in models:
                    console.print(f"  • {model.name}")
            else:
                print_warning("No models installed")
                print_info("Run 'llmshell model install' to download a model")
        else:
            print_warning("Models directory not found")
            print_info("Run 'llmshell model install' to download a model")
    
    elif action == "show-available":
        # List popular available models from GPT4All
        console.print("\n[bold cyan]Popular GPT4All Models:[/bold cyan]\n")
        
        popular_models = [
            ("Meta-Llama-3-8B-Instruct.Q4_0.gguf", "4.7GB", "Meta's Llama 3 8B - Fast, accurate, recommended"),
            ("Mistral-7B-Instruct-v0.2.Q4_0.gguf", "4.1GB", "Mistral AI's 7B model - Good for code"),
            ("Phi-3-mini-4k-instruct.Q4_0.gguf", "2.3GB", "Microsoft's compact model - Very fast"),
            ("orca-mini-3b-gguf2-q4_0.gguf", "1.9GB", "Smaller model - Low resource usage"),
            ("gpt4all-falcon-newbpe-q4_0.gguf", "3.9GB", "Falcon 7B - Good general purpose"),
        ]
        
        from rich.table import Table
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Model Name", style="yellow", no_wrap=False)
        table.add_column("Size", style="green", justify="right")
        table.add_column("Description", style="white")
        
        for name, size, desc in popular_models:
            table.add_row(name, size, desc)
        
        console.print(table)
        console.print("\n[bold]To install a model:[/bold]")
        console.print("  [cyan]llmshell model install --name MODEL_NAME[/cyan]")
        console.print("\n[bold]Example:[/bold]")
        console.print("  [cyan]llmshell model install --name Meta-Llama-3-8B-Instruct.Q4_0.gguf[/cyan]")
        console.print("\n[dim]Note: Models are downloaded from GPT4All's official repository[/dim]")
    
    else:
        print_error(f"Unknown action: {action}")
        print_info("Available actions: install, list, show-available")
        raise typer.Exit(code=1)


@app.command(name="doctor")
def doctor_command():
    """Diagnose llmshell setup and check backend availability."""
    console.print("[bold cyan]Running diagnostics...[/bold cyan]\n")
    
    # Check config
    config = Config()
    console.print(f"[green]✓[/green] Config file: {config.config_path}")
    
    if not config.config_path.exists():
        print_warning("Config file does not exist (will be created on first run)")
    
    # Check models directory
    models_dir = config.get_models_dir()
    console.print(f"[green]✓[/green] Models directory: {models_dir}")
    
    # Check for GPT4All models
    if models_dir.exists():
        models = list(models_dir.glob("*.gguf"))
        if models:
            console.print(f"[green]✓[/green] Found {len(models)} GPT4All model(s)")
        else:
            print_warning("No GPT4All models found")
            print_info("Run 'llmshell model install' to download a model")
    
    console.print()
    
    # Check backends
    manager = LLMManager(config)
    backends = manager.check_backends()
    print_backend_status(backends)
    
    console.print()
    
    # Check if at least one backend is available
    available = any(available for _, available, _ in backends)
    if available:
        print_success("At least one backend is available")
    else:
        print_error("No backends are available")
        console.print("\n[bold]Recommendations:[/bold]")
        console.print("  1. Install GPT4All model: [cyan]llmshell model install[/cyan]")
        console.print("  2. Configure OpenAI: [cyan]llmshell config set backends.openai.api_key YOUR_KEY[/cyan]")
        console.print("  3. Start Ollama server: [cyan]ollama serve[/cyan]")
    
    # Show current backend
    current_backend = config.get("llm_backend")
    console.print(f"\n[bold]Current Backend:[/bold] {current_backend}")
    
    # Test current backend
    console.print("\n[bold cyan]Testing current backend...[/bold cyan]")
    try:
        with console.status("[cyan]Generating test command...", spinner="dots"):
            test_result = manager.generate_command("list files", backend=current_backend)
        print_success(f"Backend test successful")
        print_command(test_result, "Test Output")
    except Exception as e:
        print_error(f"Backend test failed: {e}")


@app.command(name="version")
def version_command():
    """Show version information."""
    console.print(f"[bold cyan]llmshell[/bold cyan] version [green]{__version__}[/green]")


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", "-v", help="Show version"),
):
    """
    llmshell - Convert natural language to shell commands using LLMs.
    
    Examples:
      llmshell run "list all docker containers"
      llmshell run "find python files" --execute
      llmshell config show
      llmshell model install
      llmshell doctor
    """
    if version:
        console.print(f"[bold cyan]llmshell[/bold cyan] version [green]{__version__}[/green]")
        raise typer.Exit()
    
    if ctx.invoked_subcommand is None:
        console.print(ctx.get_help())


if __name__ == "__main__":
    app()
