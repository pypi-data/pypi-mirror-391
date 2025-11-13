"""Project commands for AnyTask CLI."""

from __future__ import annotations

from pathlib import Path
from typing import List

import typer
from rich.console import Console
from typing_extensions import Annotated

from cli.commands.context import CommandContext
from cli.commands.decorators import async_command
from cli.commands.formatters import TableFormatter
from cli.commands.services import ServiceRegistry as services
from cli.models.project import Project, ProjectCreate
from cli.services.context import resolve_workspace

app = typer.Typer(help="Manage projects")
console = Console()


@app.command()
@async_command()
async def create(
    name: Annotated[str, typer.Option("--name", "-n", help="Project name")],
    description: Annotated[
        str | None,
        typer.Option("--description", "-d", help="Project description"),
    ] = None,
    workspace: Annotated[
        str | None,
        typer.Option(
            "--workspace",
            "-w",
            help="Workspace ID or identifier (default: current workspace)",
        ),
    ] = None,
    directory: Annotated[
        Path | None,
        typer.Option(
            "--dir", help="Directory with workspace config (default: current)"
        ),
    ] = None,
) -> None:
    """Create a new project in a workspace.

    Creates a project with the given name.
    By default, uses the workspace from the current directory's anyt.json.
    """
    with CommandContext(require_auth=True) as _:
        # Get services from registry
        project_service = services.get_project_service()

        # Resolve workspace (from flag or local config)
        target_workspace, _ = await resolve_workspace(workspace, directory)

        # Create project
        console.print(
            f"Creating project: [cyan]{name}[/cyan] in workspace [yellow]{target_workspace.name}[/yellow]..."
        )

        project = await project_service.create_project(
            workspace_id=target_workspace.id,
            project=ProjectCreate(
                name=name,
                description=description,
            ),
        )

        console.print(f"[green]✓[/green] Created project: {project.name}")
        console.print(f"Project ID: {project.id}")

        if description:
            console.print(f"Description: {description}")


@app.command()
@async_command()
async def list(
    workspace: Annotated[
        str | None,
        typer.Option(
            "--workspace",
            "-w",
            help="Workspace ID or identifier (default: current workspace)",
        ),
    ] = None,
    directory: Annotated[
        Path | None,
        typer.Option(
            "--dir", help="Directory with workspace config (default: current)"
        ),
    ] = None,
) -> None:
    """List all projects in a workspace.

    By default, lists projects in the workspace from the current directory's anyt.json.
    """
    with CommandContext(require_auth=True) as _:
        # Get services from registry
        project_service = services.get_project_service()

        # Resolve workspace (from flag or local config)
        target_workspace, _ = await resolve_workspace(workspace, directory)

        # Fetch projects
        console.print(
            f"Fetching projects in [yellow]{target_workspace.name}[/yellow]..."
        )
        projects = await project_service.list_projects(target_workspace.id)

        def format_project_row(proj: Project) -> List[str]:
            """Format a project row for table display."""
            return [proj.name, str(proj.id)]

        TableFormatter().format_list(
            items=projects,
            columns=[
                ("Name", "green"),
                ("ID", "dim"),
            ],
            title=f"Projects in {target_workspace.name}",
            row_formatter=format_project_row,
            empty_message="No projects found\n\nCreate one with: anyt project create --name 'Project Name'",
        )
