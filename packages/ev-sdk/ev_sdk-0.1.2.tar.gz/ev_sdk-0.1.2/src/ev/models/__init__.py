from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, RootModel

__all__ = [
    "CreateAppRequest",
    "CreateAppResponse",
    "CreateProjectRequest",
    "CreateRunRequest",
    "CreateRunResponse",
    "CronTrigger",
    "EndpointTrigger",
    "EventTrigger",
    "GetRunResultResponse",
    "ListProjectsResponse",
    "ListRunsResponse",
    "Project",
    "ProjectSource",
    "ProjectSourceGithub",
    "Run",
    "RunEntrypoint",
    "RunEnvironment",
    "RunSource",
    "RunStatus",
    "Trigger",
    "UpdateAppRequest",
    "UpdateAppResponse",
    "UpdateProjectRequest",
    "Workspace",
    "WorkspaceIntegration",
    "WorkspaceIntegrationGithub",
]

###
# Projects
###


class ProjectSourceGithub(BaseModel):
    remote: str
    branch: str


class ProjectSource(BaseModel):
    github: ProjectSourceGithub


class Project(BaseModel):
    id: str
    name: str
    source: ProjectSource


class CreateProjectRequest(BaseModel):
    name: str
    source: ProjectSource


class UpdateProjectRequest(BaseModel):
    name: str | None = None


class ListProjectsResponse(BaseModel):
    projects: list[Project]
    page: int
    page_size: int


###
# Runs
###


class RunStatus(str, Enum):
    UNKNOWN = "unknown"
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"

    def is_complete(self) -> bool:
        return self in [RunStatus.SUCCEEDED, RunStatus.FAILED, RunStatus.CANCELLED]


class RunEnvironment(BaseModel):
    python_version: str
    dependencies: list[str] = []
    environment_variables: dict[str, str] | None = None


class FileEntrypoint(BaseModel):
    file_path: str
    argv: list[str] | None = None


class ModuleEntrypoint(BaseModel):
    module: str
    argv: list[str] | None = None


class FunctionEntrypoint(BaseModel):
    module: str
    symbol: str
    args: list[Any] | None = None
    kwargs: dict[str, Any] | None = None


class GitSource(BaseModel):
    remote: str
    hash: str
    bundle: str | None = None
    patch: str | None = None


class AppGitSource(BaseModel):
    remote: str


class DirectorySource(BaseModel):
    path: str


class RunEntrypoint(
    RootModel[
        dict[Literal["file"], FileEntrypoint]
        | dict[Literal["module"], ModuleEntrypoint]
        | dict[Literal["function"], FunctionEntrypoint]
    ]
):
    def __init__(self, root: Any = None, **data: Any) -> None:
        if root is None and data:
            root = data
        super().__init__(root)

    @classmethod
    def file(cls, file_path: str, argv: list[str] | None = None) -> RunEntrypoint:
        return cls({"file": FileEntrypoint(file_path=file_path, argv=argv or [])})

    @classmethod
    def module(cls, module: str, argv: list[str] | None = None) -> RunEntrypoint:
        return cls({"module": ModuleEntrypoint(module=module, argv=argv or [])})

    @classmethod
    def function(
        cls,
        module: str,
        symbol: str,
        args: list[Any] | None = None,
        kwargs: dict[str, Any] | None = None,
    ) -> RunEntrypoint:
        return cls(
            {
                "function": FunctionEntrypoint(
                    module=module,
                    symbol=symbol,
                    args=args,
                    kwargs=kwargs,
                )
            }
        )

    def get_function(self) -> FunctionEntrypoint | None:
        """Get the function entrypoint if this is a function entrypoint."""
        return self.root.get("function")  # type: ignore

    def get_file(self) -> FileEntrypoint | None:
        """Get the file entrypoint if this is a file entrypoint."""
        return self.root.get("file")  # type: ignore

    def get_module(self) -> ModuleEntrypoint | None:
        """Get the module entrypoint if this is a module entrypoint."""
        return self.root.get("module")  # type: ignore


class RunSource(RootModel[dict[Literal["git"], GitSource] | dict[Literal["directory"], DirectorySource]]):
    def __init__(self, root: Any = None, **data: Any) -> None:
        if root is None and data:
            root = data
        super().__init__(root)

    @classmethod
    def git(cls, remote: str, hash: str, bundle: str | None = None, patch: str | None = None) -> RunSource:
        return cls({"git": GitSource(remote=remote, hash=hash, bundle=bundle, patch=patch)})

    @classmethod
    def directory(cls, path: str) -> RunSource:
        return cls({"directory": DirectorySource(path=path)})

    def get_git(self) -> GitSource | None:
        """Get the git source if this is a git source."""
        return self.root.get("git")  # type: ignore

    def get_directory(self) -> DirectorySource | None:
        """Get the directory source if this is a directory source."""
        return self.root.get("directory")  # type: ignore


class Run(BaseModel):
    id: str
    status: RunStatus
    entrypoint: RunEntrypoint
    source: RunSource
    environment: RunEnvironment


class CreateRunRequest(BaseModel):
    entrypoint: RunEntrypoint
    source: RunSource
    environment: RunEnvironment
    secrets: dict[str, str] | None = None


class CreateRunResponse(BaseModel):
    run: Run


class ListRunsResponse(BaseModel):
    runs: list[Run]
    page: int
    page_size: int


GetRunResultResponse = Any
"""A result can be any valid JSON."""

###
# Apps
###


class AppSource(RootModel[dict[Literal["git"], AppGitSource] | dict[Literal["directory"], DirectorySource]]):
    def __init__(self, root: Any = None, **data: Any) -> None:
        if root is None and data:
            root = data
        super().__init__(root)

    @classmethod
    def git(cls, remote: str) -> AppSource:
        return cls({"git": AppGitSource(remote=remote)})

    @classmethod
    def directory(cls, path: str) -> AppSource:
        return cls({"directory": DirectorySource(path=path)})

    def get_git(self) -> AppGitSource | None:
        """Get the git source if this is a git source."""
        return self.root.get("git")  # type: ignore

    def get_directory(self) -> DirectorySource | None:
        """Get the directory source if this is a directory source."""
        return self.root.get("directory")  # type: ignore


class App(BaseModel):
    id: str
    name: str
    entrypoint: RunEntrypoint
    source: AppSource
    environment: RunEnvironment


class CreateAppRequest(BaseModel):
    name: str
    entrypoint: RunEntrypoint
    source: AppSource
    environment: RunEnvironment
    triggers: list[Trigger]


class CreateAppResponse(BaseModel):
    app: App


class UpdateAppRequest(BaseModel):
    name: str
    entrypoint: RunEntrypoint
    source: AppSource
    environment: RunEnvironment
    triggers: list[Trigger]


class UpdateAppResponse(BaseModel):
    app: App


###
# Workspaces
###


class WorkspaceIntegrationGithub(BaseModel):
    installation_id: int


class WorkspaceIntegration(BaseModel):
    github: WorkspaceIntegrationGithub


class Workspace(BaseModel):
    id: str
    name: str
    integrations: list[WorkspaceIntegration]


###
# Triggers
###


class CronTrigger(BaseModel):
    schedule: str


class EventTrigger(BaseModel):
    # TODO(desmond): Add event-specific fields when implemented
    pass


class EndpointTrigger(BaseModel):
    # TODO(desmond): Add endpoint-specific fields when implemented
    pass


class Trigger(
    RootModel[
        dict[Literal["cron"], CronTrigger]
        | dict[Literal["event"], EventTrigger]
        | dict[Literal["endpoint"], EndpointTrigger]
    ]
):
    """A trigger configuration for pipelines."""

    def __init__(self, root: Any = None, **data: Any) -> None:
        if root is None and data:
            root = data
        super().__init__(root)

    @classmethod
    def create_cron(cls, schedule: str) -> Trigger:
        """Create a cron trigger with the given schedule."""
        return cls({"cron": CronTrigger(schedule=schedule)})

    def get_cron(self) -> CronTrigger | None:
        """Get the cron trigger if this is a cron trigger."""
        return self.root.get("cron")  # type: ignore

    def get_event(self) -> EventTrigger | None:
        """Get the event trigger if this is an event trigger."""
        return self.root.get("event")  # type: ignore

    def get_endpoint(self) -> EndpointTrigger | None:
        """Get the endpoint trigger if this is an endpoint trigger."""
        return self.root.get("endpoint")  # type: ignore
