"""Command decorators for async execution with error handling."""

import asyncio
import functools
from typing import Any, Awaitable, Callable, ParamSpec, TypeVar

import typer
from rich.console import Console

from cli.commands.formatters import output_json
from cli.utils.errors import handle_api_error, is_debug_mode

console = Console()
P = ParamSpec("P")
T = TypeVar("T")


def async_command(
    json_arg_name: str = "json_output",
    timeout: int | None = None,
) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, None]]:
    """Decorator to handle async command execution with error handling.

    This decorator provides:
    - Automatic async execution via asyncio.run()
    - Optional timeout support for long-running operations
    - Graceful CTRL+C (KeyboardInterrupt) handling with proper exit code
    - Consistent error handling in production mode
    - Debug mode support (full tracebacks)
    - Automatic JSON output formatting

    Args:
        json_arg_name: Name of the JSON output argument (default: "json_output")
        timeout: Optional timeout in seconds for the command

    Example:
        @app.command()
        @async_command(timeout=30)
        async def list_tasks(status: str, json_output: bool = False):
            service = TaskService.from_config()
            tasks = await service.list_tasks(...)

            if json_output:
                return {"items": [t.model_dump(mode="json") for t in tasks]}
            else:
                render_task_table(tasks)

    Returns:
        Decorated function that handles async execution and errors
    """

    def decorator(func: Callable[P, Awaitable[T]]) -> Callable[P, None]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> None:
            # Extract json_output flag
            json_output = kwargs.get(json_arg_name, False)

            async def _run() -> Any:
                try:
                    if timeout:
                        return await asyncio.wait_for(
                            func(*args, **kwargs), timeout=timeout
                        )
                    else:
                        return await func(*args, **kwargs)
                except asyncio.TimeoutError:
                    if json_output:
                        output_json(
                            {
                                "error": "TimeoutError",
                                "message": f"Command timed out after {timeout}s",
                            },
                            success=False,
                        )
                    else:
                        console.print(
                            f"[red]Error:[/red] Command timed out after {timeout}s"
                        )
                    raise typer.Exit(1)
                except typer.Exit:
                    # Let typer.Exit propagate unchanged
                    raise
                except Exception as e:
                    # In debug mode, propagate the exception for full traceback
                    if is_debug_mode():
                        raise

                    # Production mode - show user-friendly error
                    if json_output:
                        output_json(
                            {"error": type(e).__name__, "message": str(e)},
                            success=False,
                        )
                        raise typer.Exit(1)
                    else:
                        handle_api_error(e, context="")

            try:
                result = asyncio.run(_run())

                # Auto-format result if provided
                if result is not None and json_output:
                    if isinstance(result, dict):
                        output_json(result)
                    else:
                        output_json({"data": result})

            except KeyboardInterrupt:
                # Handle CTRL+C gracefully
                console.print("\n[yellow]Cancelled[/yellow]")
                raise typer.Exit(130)  # Standard SIGINT exit code

        return wrapper

    return decorator
