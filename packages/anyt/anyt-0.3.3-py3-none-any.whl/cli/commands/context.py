"""Command context manager for CLI commands.

Provides centralized authentication and workspace checking with
consistent error handling and debug mode support.
"""

from typing import Optional

import typer
from rich.console import Console

from cli.config import WorkspaceConfig, get_effective_api_config
from cli.utils.errors import is_debug_mode

console = Console()


class CommandContext:
    """Shared context for CLI commands with auth and workspace validation.

    This context manager eliminates duplicated authentication and workspace
    checking code across commands. It provides:
    - Centralized authentication validation
    - Centralized workspace config validation
    - Debug mode error handling
    - Consistent, user-friendly error messages

    Example:
        @app.command()
        def create_label(name: str):
            '''Create a label.'''
            with CommandContext(require_auth=True, require_workspace=True) as ctx:
                service = LabelService.from_config()
                result = asyncio.run(
                    service.create_label(
                        workspace_id=ctx.workspace_config.workspace_id,
                        label=LabelCreate(name=name)
                    )
                )
                console.print(f"[green]✓[/green] Created label: {result.name}")
    """

    def __init__(
        self,
        require_auth: bool = True,
        require_workspace: bool = False,
    ):
        """Initialize command context.

        Args:
            require_auth: Whether to require authentication (ANYT_API_KEY)
            require_workspace: Whether to require workspace config (.anyt/anyt.json)
        """
        self.require_auth = require_auth
        self.require_workspace = require_workspace
        self.api_config: dict[str, str] | None = None
        self.workspace_config: WorkspaceConfig | None = None

    def __enter__(self) -> "CommandContext":
        """Validate context requirements on entry.

        Returns:
            Self for context manager protocol

        Raises:
            typer.Exit: If validation fails (in production mode)
            RuntimeError: If validation fails (in debug mode)
        """
        # Check authentication
        if self.require_auth:
            try:
                self.api_config = get_effective_api_config()
            except RuntimeError as e:
                if is_debug_mode():
                    raise
                console.print("[red]Error:[/red] Not authenticated")
                console.print("\nSet the ANYT_API_KEY environment variable:")
                console.print("  [cyan]export ANYT_API_KEY=anyt_agent_...[/cyan]")
                raise typer.Exit(1) from e

        # Check workspace config
        if self.require_workspace:
            self.workspace_config = WorkspaceConfig.load()

            if not self.workspace_config:
                if is_debug_mode():
                    raise RuntimeError("Not in a workspace directory")
                console.print("[red]Error:[/red] Not in a workspace directory")
                console.print("Run [cyan]anyt workspace init[/cyan] first")
                raise typer.Exit(1)

        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[object],
    ) -> bool:
        """Handle cleanup and error formatting.

        Args:
            exc_type: Exception type if an error occurred
            exc_val: Exception value if an error occurred
            exc_tb: Exception traceback if an error occurred

        Returns:
            True to suppress exception (production mode), False to propagate (debug mode)
        """
        if exc_type and not isinstance(exc_val, typer.Exit):
            if is_debug_mode():
                return False  # Let exception propagate with full traceback
            # Production mode: friendly error message
            console.print(f"[red]Error:[/red] {exc_val}")
            return True  # Suppress traceback

        return False  # No exception or typer.Exit, proceed normally
