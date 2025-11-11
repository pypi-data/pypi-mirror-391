"""Core functionality for llmshell."""


class GPTShell:
    """Main class for GPT shell interactions."""

    def __init__(self):
        """Initialize GPTShell."""
        self.history = []

    def execute(self, command: str) -> str:
        """
        Execute a command.

        Args:
            command: The command to execute

        Returns:
            The result of the command execution
        """
        self.history.append(command)
        # TODO: Implement actual command execution logic
        return f"Executed: {command}"

    def get_history(self) -> list[str]:
        """
        Get command history.

        Returns:
            List of executed commands
        """
        return self.history.copy()
