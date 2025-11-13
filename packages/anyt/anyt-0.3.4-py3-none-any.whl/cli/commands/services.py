"""Service registry for centralized service management."""

from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    from cli.client.workspaces import WorkspacesAPIClient
    from cli.services.project_service import ProjectService
    from cli.services.task_service import TaskService
    from cli.services.user_service import UserService
    from cli.services.view_service import ViewService
    from cli.services.workspace_service import WorkspaceService


class ServiceRegistry:
    """Centralized service registry with lazy initialization and caching.

    Provides a singleton-like pattern for service instances, ensuring they are
    created only when needed and reused across commands. This improves performance
    and reduces boilerplate code.

    Example:
        from cli.commands.services import ServiceRegistry as services

        # Get service (lazy-created and cached)
        task_service = services.get_task_service()

        # Clear cache (useful for testing)
        services.clear()
    """

    _instances: dict[type, Any] = {}

    @classmethod
    def get_task_service(cls) -> "TaskService":
        """Get or create TaskService instance.

        Returns:
            Cached TaskService instance
        """
        from cli.services.task_service import TaskService

        if TaskService not in cls._instances:
            cls._instances[TaskService] = TaskService.from_config()
        return cast("TaskService", cls._instances[TaskService])

    @classmethod
    def get_workspace_service(cls) -> "WorkspaceService":
        """Get or create WorkspaceService instance.

        Returns:
            Cached WorkspaceService instance
        """
        from cli.services.workspace_service import WorkspaceService

        if WorkspaceService not in cls._instances:
            cls._instances[WorkspaceService] = WorkspaceService.from_config()
        return cast("WorkspaceService", cls._instances[WorkspaceService])

    @classmethod
    def get_project_service(cls) -> "ProjectService":
        """Get or create ProjectService instance.

        Returns:
            Cached ProjectService instance
        """
        from cli.services.project_service import ProjectService

        if ProjectService not in cls._instances:
            cls._instances[ProjectService] = ProjectService.from_config()
        return cast("ProjectService", cls._instances[ProjectService])

    @classmethod
    def get_view_service(cls) -> "ViewService":
        """Get or create ViewService instance.

        Returns:
            Cached ViewService instance
        """
        from cli.services.view_service import ViewService

        if ViewService not in cls._instances:
            cls._instances[ViewService] = ViewService.from_config()
        return cast("ViewService", cls._instances[ViewService])

    @classmethod
    def get_user_service(cls) -> "UserService":
        """Get or create UserService instance.

        Returns:
            Cached UserService instance
        """
        from cli.services.user_service import UserService

        if UserService not in cls._instances:
            cls._instances[UserService] = UserService.from_config()
        return cast("UserService", cls._instances[UserService])

    @classmethod
    def get_workspaces_client(cls) -> "WorkspacesAPIClient":
        """Get or create WorkspacesAPIClient instance.

        Returns:
            Cached WorkspacesAPIClient instance
        """
        from cli.client.workspaces import WorkspacesAPIClient

        if WorkspacesAPIClient not in cls._instances:
            cls._instances[WorkspacesAPIClient] = WorkspacesAPIClient.from_config()
        return cast("WorkspacesAPIClient", cls._instances[WorkspacesAPIClient])

    @classmethod
    def clear(cls) -> None:
        """Clear all cached service instances.

        Useful for testing to ensure fresh service instances between tests.
        Should be called in test teardown or setup.
        """
        cls._instances.clear()
