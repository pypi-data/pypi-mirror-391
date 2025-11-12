from __future__ import annotations

import requests

from ev.models import (
    CreateAppRequest,
    CreateAppResponse,
    CreateProjectRequest,
    CreateRunRequest,
    CreateRunResponse,
    GetRunResultResponse,
    ListProjectsResponse,
    ListRunsResponse,
    Project,
    Run,
    RunStatus,
    UpdateAppRequest,
    UpdateAppResponse,
    UpdateProjectRequest,
    WorkspaceIntegration,
)

__all__: tuple[str, ...] = ("Client",)


class Client:
    def __init__(self, endpoint: str, access_token: str) -> None:
        self.endpoint = endpoint.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}",
            }
        )

    def get_auth_headers(self) -> dict[str, str]:
        """Get authentication headers for use with external HTTP clients.

        This is useful when making HTTP requests with httpx or other clients
        that need to authenticate with the same credentials as this Client.

        TODO: Consider making this Client class fully async with native async methods
              instead of requiring external clients to handle async operations.

        Returns:
            Dictionary of headers including Authorization token.
        """
        return dict(self.session.headers)  # type: ignore

    def create_workspace_integration(self, workspace_id: str, integration: WorkspaceIntegration) -> None:
        url = self.get_integrations_url(workspace_id)
        res = self.session.post(url, json=integration.model_dump())
        res.raise_for_status()

    def delete_workspace_integration(self, workspace_id: str, integration: WorkspaceIntegration) -> None:
        url = self.get_integrations_url(workspace_id)
        res = self.session.delete(url, json=integration.model_dump())
        res.raise_for_status()

    # Project methods
    def list_projects(self, workspace_id: str, limit: int | None = None, offset: int = 0) -> list[Project]:
        """List projects in a workspace with automatic pagination if limit=None.

        Args:
            workspace_id: ID of the workspace to list projects from.
            limit: Maximum number of projects to return. If None, fetches all projects.
            offset: Starting offset for pagination. If limit=None, this is ignored.

        Returns:
            List of projects.
        """
        url = self.get_projects_url(workspace_id)

        # If limit is None, fetch all projects with automatic pagination
        if limit is None:
            projects = []
            local_limit = 50
            local_offset = 0

            while True:
                params = {"limit": local_limit, "offset": local_offset}
                res = self.session.get(url, params=params)
                res.raise_for_status()
                response = ListProjectsResponse.model_validate(res.json())
                projects.extend(response.projects)

                if len(response.projects) < local_limit:
                    break
                local_offset += local_limit

            return projects

        # If limit is specified, return a single page
        params = {"limit": limit, "offset": offset}
        res = self.session.get(url, params=params)
        res.raise_for_status()
        response = ListProjectsResponse.model_validate(res.json())
        return response.projects

    def get_project(self, workspace_id: str, project_id: str) -> Project:
        url = self.get_project_url(workspace_id, project_id)
        res = self.session.get(url)
        res.raise_for_status()
        return Project.model_validate(res.json())

    def create_project(self, workspace_id: str, request: CreateProjectRequest) -> Project:
        url = self.get_projects_url(workspace_id)
        res = self.session.post(url, json=request.model_dump())
        res.raise_for_status()
        return Project.model_validate(res.json())

    def update_project(self, workspace_id: str, project_id: str, request: UpdateProjectRequest) -> Project:
        url = self.get_project_url(workspace_id, project_id)
        res = self.session.patch(url, json=request.model_dump())
        res.raise_for_status()
        return Project.model_validate(res.json())

    def delete_project(self, workspace_id: str, project_id: str) -> None:
        url = self.get_project_url(workspace_id, project_id)
        res = self.session.delete(url)
        res.raise_for_status()

    # App methods
    def create_app(self, workspace_id: str, project_id: str, request: CreateAppRequest) -> CreateAppResponse:
        url = self.get_apps_url(workspace_id, project_id)
        res = self.session.post(url, json=request.model_dump(exclude_none=True))
        res.raise_for_status()
        return CreateAppResponse.model_validate(res.json())

    def update_app(
        self,
        workspace_id: str,
        project_id: str,
        app_id: str,
        request: UpdateAppRequest,
    ) -> UpdateAppResponse:
        url = f"{self.get_apps_url(workspace_id, project_id)}/{app_id}"
        res = self.session.put(url, json=request.model_dump(exclude_none=True))
        res.raise_for_status()
        return UpdateAppResponse.model_validate(res.json())

    # Run methods
    def create_run(self, workspace_id: str, project_id: str, request: CreateRunRequest) -> CreateRunResponse:
        url = self.get_runs_url(workspace_id, project_id)
        res = self.session.post(url, json=request.model_dump())
        res.raise_for_status()
        return CreateRunResponse.model_validate(res.json())

    def get_run(self, workspace_id: str, project_id: str, run_id: str) -> Run:
        url = self.get_run_url(workspace_id, project_id, run_id)
        res = self.session.get(url)
        res.raise_for_status()
        return Run.model_validate(res.json())

    def get_run_status(self, workspace_id: str, project_id: str, run_id: str) -> RunStatus:
        run = self.get_run(workspace_id, project_id, run_id)
        return run.status

    def list_runs(self, workspace_id: str, project_id: str, limit: int = 50, offset: int = 0) -> ListRunsResponse:
        url = self.get_runs_url(workspace_id, project_id)
        params = {"limit": limit, "offset": offset}
        res = self.session.get(url, params=params)
        res.raise_for_status()
        return ListRunsResponse.model_validate(res.json())

    def get_run_result(self, workspace_id: str, project_id: str, run_id: str) -> GetRunResultResponse:
        url = self.run_result_url(workspace_id, project_id, run_id)
        res = self.session.get(url)
        res.raise_for_status()
        # run result can be any JSON
        return res.json()

    def cancel_run(self, workspace_id: str, project_id: str, run_id: str) -> None:
        url = self.cancel_run_url(workspace_id, project_id, run_id)
        res = self.session.post(url)
        res.raise_for_status()

    ###
    # URL HELPERS
    ###

    def get_integrations_url(self, workspace_id: str) -> str:
        return f"{self.endpoint}/v1/workspaces/{workspace_id}/integrations"

    def get_projects_url(self, workspace_id: str) -> str:
        return f"{self.endpoint}/v1/workspaces/{workspace_id}/projects"

    def get_project_url(self, workspace_id: str, project_id: str) -> str:
        return f"{self.endpoint}/v1/workspaces/{workspace_id}/projects/{project_id}"

    def get_apps_url(self, workspace_id: str, project_id: str) -> str:
        return f"{self.get_project_url(workspace_id, project_id)}/apps"

    def get_runs_url(self, workspace_id: str, project_id: str) -> str:
        return f"{self.endpoint}/v1/workspaces/{workspace_id}/projects/{project_id}/runs"

    def get_run_url(self, workspace_id: str, project_id: str, run_id: str) -> str:
        return f"{self.endpoint}/v1/workspaces/{workspace_id}/projects/{project_id}/runs/{run_id}"

    def get_run_logs_tail_url(self, workspace_id: str, project_id: str, run_id: str) -> str:
        return f"{self.endpoint}/v1/workspaces/{workspace_id}/projects/{project_id}/runs/{run_id}/logs/tail"

    def run_result_url(self, workspace_id: str, project_id: str, run_id: str) -> str:
        return f"{self.endpoint}/v1/workspaces/{workspace_id}/projects/{project_id}/runs/{run_id}/results"

    def cancel_run_url(self, workspace_id: str, project_id: str, run_id: str) -> str:
        return f"{self.endpoint}/v1/workspaces/{workspace_id}/projects/{project_id}/runs/{run_id}/cancel"

    def get_realtime_stats_url(self, workspace_id: str, project_id: str, run_id: str) -> str:
        endpoint_ws = self.endpoint.replace("http", "ws", 1)
        return f"{endpoint_ws}/v1/workspaces/{workspace_id}/projects/{project_id}/runs/{run_id}/metrics/tail"
