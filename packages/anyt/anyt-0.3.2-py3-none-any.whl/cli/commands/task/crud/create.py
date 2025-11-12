"""Create commands for tasks (add)."""

from typing import Optional

import typer
from typing_extensions import Annotated

from cli.client.projects import ProjectsAPIClient
from cli.commands.context import CommandContext
from cli.commands.decorators import async_command
from cli.commands.services import ServiceRegistry as services
from cli.models.common import Priority, Status
from cli.models.task import TaskCreate

from cli.commands.utils import get_project_id
from ..helpers import (
    console,
    output_json,
)


@async_command()
async def add_task(
    title: Annotated[str, typer.Argument(help="Task title")],
    description: Annotated[
        Optional[str],
        typer.Option("-d", "--description", help="Task description"),
    ] = None,
    phase: Annotated[
        Optional[str],
        typer.Option("--phase", help="Phase/milestone identifier (e.g., T3, Phase 1)"),
    ] = None,
    priority: Annotated[
        int,
        typer.Option("-p", "--priority", help="Priority (-2 to 2, default: 0)"),
    ] = 0,
    labels: Annotated[
        Optional[str],
        typer.Option("--labels", help="Comma-separated labels"),
    ] = None,
    status: Annotated[
        str,
        typer.Option("--status", help="Task status (default: backlog)"),
    ] = "backlog",
    owner: Annotated[
        Optional[str],
        typer.Option("--owner", help="Assign to user or agent ID"),
    ] = None,
    estimate: Annotated[
        Optional[int],
        typer.Option("--estimate", help="Time estimate in hours"),
    ] = None,
    project: Annotated[
        Optional[int],
        typer.Option(
            "--project",
            help="Project ID (uses current/default project if not specified)",
        ),
    ] = None,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Output in JSON format"),
    ] = False,
) -> None:
    """Create a new task."""
    with CommandContext(require_auth=True, require_workspace=True) as ctx:
        assert ctx.workspace_config is not None  # For mypy

        service = services.get_task_service()
        projects_client = ProjectsAPIClient.from_config()

        try:
            # Validate priority range
            if priority < -2 or priority > 2:
                if json_output:
                    output_json(
                        {
                            "error": "ValidationError",
                            "message": "Invalid priority value",
                            "details": "Priority must be between -2 and 2\n  -2: Lowest\n  -1: Low\n   0: Normal (default)\n   1: High\n   2: Highest",
                        },
                        success=False,
                    )
                else:
                    console.print("[red] Error:[/red] Invalid priority value")
                    console.print()
                    console.print("  Priority must be between -2 and 2")
                    console.print("    -2: Lowest")
                    console.print("    -1: Low")
                    console.print("     0: Normal (default)")
                    console.print("     1: High")
                    console.print("     2: Highest")
                raise typer.Exit(1)

            # Get project ID from argument, config, or API
            project_id = await get_project_id(
                project_arg=project,
                ws_config=ctx.workspace_config,
                projects_client=projects_client,
            )

            # Parse labels
            label_list = []
            if labels:
                label_list = [label.strip() for label in labels.split(",")]

            # Ensure project_id is set
            if project_id is None:
                raise ValueError("Project ID is required but not set")

            # Convert priority to enum
            priority_enum = Priority(priority)
            # Convert status to enum
            status_enum = Status(status)

            # Create task using typed model
            task_create = TaskCreate(
                title=title,
                description=description,
                phase=phase,
                status=status_enum,
                priority=priority_enum,
                owner_id=owner,
                project_id=project_id,
                labels=label_list,
                estimate=estimate,
            )

            # Create task via service
            task = await service.create_task_with_validation(
                project_id=project_id,
                task=task_create,
            )

            # Display success
            if json_output:
                output_json(task.model_dump(mode="json"))
            else:
                console.print(
                    f"[green]✓[/green] Created: [cyan]{task.identifier}[/cyan] ({task.title})"
                )

        except typer.Exit:
            raise
        except ValueError as e:
            # Handle enum conversion errors
            if json_output:
                output_json(
                    {"error": "ValidationError", "message": str(e)}, success=False
                )
            else:
                console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)
        except Exception as e:
            if json_output:
                output_json({"error": "CreateError", "message": str(e)}, success=False)
            else:
                console.print(f"[red]Error:[/red] Failed to create task: {e}")
            raise typer.Exit(1)
