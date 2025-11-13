"""CLI commands for task comments."""

import json
from typing import Any, Optional

import typer
from rich.console import Console
from rich.table import Table
from typing_extensions import Annotated

from cli.client.comments import CommentsAPIClient
from cli.client.exceptions import APIError, NotFoundError, ValidationError
from cli.client.tasks import TasksAPIClient
from cli.commands.context import CommandContext
from cli.commands.decorators import async_command
from cli.commands.task.helpers import get_active_task_id
from cli.models.comment import CommentCreate
from cli.utils.errors import handle_api_error

app = typer.Typer(help="Manage task comments")
console = Console()


@app.command("add")
@async_command()
async def add_comment(
    message: Annotated[str, typer.Option("--message", "-m", help="Comment content")],
    identifier: Annotated[
        Optional[str],
        typer.Argument(
            help="Task identifier (e.g., DEV-42). Uses active task if not provided."
        ),
    ] = None,
    json_output: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """Add a comment to a task.

    Examples:
        # Add comment to active task
        anyt comment add -m "Completed implementation"

        # Add comment to specific task
        anyt comment add DEV-123 -m "Found edge case"
    """
    with CommandContext(require_auth=True, require_workspace=True) as ctx:
        assert ctx.workspace_config is not None  # Guaranteed by require_workspace=True

        # Resolve task identifier
        if not identifier:
            identifier = get_active_task_id()
            if not identifier:
                console.print(
                    "[red]Error:[/red] No task identifier provided and no active task set"
                )
                console.print(
                    "Use [cyan]anyt task pick <task-id>[/cyan] to set active task"
                )
                raise typer.Exit(1)

        try:
            # Create API clients
            client = CommentsAPIClient.from_config()
            tasks_client = TasksAPIClient.from_config()

            # Get task to obtain numeric ID
            task = await tasks_client.get_task_by_workspace(
                ctx.workspace_config.workspace_id, identifier
            )

            # Determine author_id and author_type
            # Agent context - use api_key from context
            assert ctx.api_config is not None  # Guaranteed by require_auth=True
            author_id = ctx.api_config["api_key"]
            author_type = "agent"

            # Create comment
            comment_data = CommentCreate(
                content=message,
                task_id=task.id,
                author_id=author_id,
                author_type=author_type,
            )
            comment = await client.create_comment(identifier, comment_data)

            if json_output:
                output: dict[str, Any] = {
                    "success": True,
                    "data": comment.model_dump(mode="json"),
                }
                print(json.dumps(output, indent=2, default=str))
            else:
                console.print(
                    f"[green]✓[/green] Comment added to task [cyan]{identifier}[/cyan]"
                )

        except NotFoundError:
            console.print(f"[red]Error:[/red] Task '{identifier}' not found")
            raise typer.Exit(1)
        except ValidationError as e:
            console.print(f"[red]Error:[/red] Invalid comment data: {e}")
            raise typer.Exit(1)
        except APIError as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)
        except Exception as e:
            # Catch any unexpected errors
            handle_api_error(e, "adding comment")


@app.command("list")
@async_command()
async def list_comments(
    identifier: Annotated[
        Optional[str],
        typer.Argument(
            help="Task identifier (e.g., DEV-42). Uses active task if not provided."
        ),
    ] = None,
    json_output: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """List all comments on a task.

    Examples:
        # List comments on active task
        anyt comment list

        # List comments on specific task
        anyt comment list DEV-123

        # JSON output
        anyt comment list DEV-123 --json
    """
    with CommandContext(require_auth=True, require_workspace=True):
        # Resolve task identifier
        if not identifier:
            identifier = get_active_task_id()
            if not identifier:
                console.print(
                    "[red]Error:[/red] No task identifier provided and no active task set"
                )
                console.print(
                    "Use [cyan]anyt task pick <task-id>[/cyan] to set active task"
                )
                raise typer.Exit(1)

        try:
            # Create API client
            client = CommentsAPIClient.from_config()

            # Fetch comments
            comments = await client.list_comments(identifier)

            if json_output:
                output: dict[str, Any] = {
                    "success": True,
                    "data": {
                        "task_identifier": identifier,
                        "comments": [c.model_dump(mode="json") for c in comments],
                    },
                }
                print(json.dumps(output, indent=2, default=str))
            else:
                if not comments:
                    console.print(f"No comments on task [cyan]{identifier}[/cyan]")
                    return

                # Display comments in a table
                table = Table(title=f"Comments on {identifier}")
                table.add_column("ID", style="dim")
                table.add_column("Content", style="white")
                table.add_column("Created", style="cyan")
                table.add_column("User ID", style="dim")

                for comment in comments:
                    # Format timestamp
                    timestamp_str = comment.created_at.strftime("%Y-%m-%d %H:%M:%S")

                    # Truncate long comments
                    content = comment.content
                    if len(content) > 80:
                        content = content[:77] + "..."

                    table.add_row(
                        str(comment.id),
                        content,
                        timestamp_str,
                        str(comment.user_id),
                    )

                console.print(table)
                console.print(f"\n[dim]Total: {len(comments)} comment(s)[/dim]")

        except NotFoundError:
            console.print(f"[red]Error:[/red] Task '{identifier}' not found")
            raise typer.Exit(1)
        except APIError as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)
        except Exception as e:
            # Catch any unexpected errors
            handle_api_error(e, "listing comments")
