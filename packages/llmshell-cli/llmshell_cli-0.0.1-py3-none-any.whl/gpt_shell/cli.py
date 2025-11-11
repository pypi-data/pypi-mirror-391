"""Command-line interface for llmshell."""

import argparse
import sys
from gpt_shell import GPTShell, __version__


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="GPT Shell - A tool for GPT shell interactions"
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"llmshell {__version__}"
    )
    parser.add_argument(
        "command",
        nargs="?",
        help="Command to execute"
    )
    parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="Start interactive mode"
    )

    args = parser.parse_args()

    shell = GPTShell()

    if args.interactive:
        print(f"llmshell {__version__} - Interactive Mode")
        print("Type 'exit' or 'quit' to exit\n")
        while True:
            try:
                command = input("llmshell> ")
                if command.lower() in ("exit", "quit"):
                    break
                if command.strip():
                    result = shell.execute(command)
                    print(result)
            except (KeyboardInterrupt, EOFError):
                print("\nExiting...")
                break
    elif args.command:
        result = shell.execute(args.command)
        print(result)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
