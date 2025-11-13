"""Tests for Client pagination behavior."""

from __future__ import annotations

from unittest.mock import Mock

import pytest
from ev.client import Client
from ev.models import (
    Project,
    ProjectSource,
    ProjectSourceGithub,
)


@pytest.fixture
def mock_session() -> Mock:
    """Create a mock requests session."""
    return Mock()


@pytest.fixture
def client(mock_session: Mock) -> Client:
    """Create a client with mocked session."""
    client = Client(endpoint="http://test.example.com", access_token="test-token")
    client.session = mock_session
    return client


def test_list_all_projects_with_pagination(client: Client, mock_session: Mock) -> None:
    """Test that limit=None fetches all projects across multiple pages."""
    # Create mock projects
    projects_page1 = [
        Project(
            id=f"proj-{i}",
            name=f"Project {i}",
            source=ProjectSource(github=ProjectSourceGithub(remote="https://github.com/test/repo", branch="main")),
        )
        for i in range(50)
    ]
    projects_page2 = [
        Project(
            id=f"proj-{i}",
            name=f"Project {i}",
            source=ProjectSource(github=ProjectSourceGithub(remote="https://github.com/test/repo", branch="main")),
        )
        for i in range(50, 80)
    ]

    # Mock responses
    mock_response1 = Mock()
    mock_response1.json.return_value = {
        "projects": [p.model_dump() for p in projects_page1],
        "page": 0,
        "page_size": 50,
    }

    mock_response2 = Mock()
    mock_response2.json.return_value = {
        "projects": [p.model_dump() for p in projects_page2],
        "page": 1,
        "page_size": 50,
    }

    mock_session.get.side_effect = [mock_response1, mock_response2]

    # Call method with limit=None
    result = client.list_projects("workspace-123", limit=None)

    # Verify all projects were returned
    assert len(result) == 80
    assert result[0].id == "proj-0"
    assert result[49].id == "proj-49"
    assert result[50].id == "proj-50"
    assert result[79].id == "proj-79"

    # Verify two API calls were made
    assert mock_session.get.call_count == 2


def test_list_projects_with_limit(client: Client, mock_session: Mock) -> None:
    """Test that specifying a limit returns a single page."""
    projects = [
        Project(
            id=f"proj-{i}",
            name=f"Project {i}",
            source=ProjectSource(github=ProjectSourceGithub(remote="https://github.com/test/repo", branch="main")),
        )
        for i in range(10)
    ]

    mock_response = Mock()
    mock_response.json.return_value = {
        "projects": [p.model_dump() for p in projects],
        "page": 0,
        "page_size": 10,
    }
    mock_session.get.return_value = mock_response

    # Call method with limit=10
    result = client.list_projects("workspace-123", limit=10)

    # Verify correct number returned
    assert len(result) == 10
    assert result[0].id == "proj-0"

    # Verify only one API call was made
    assert mock_session.get.call_count == 1


def test_list_projects_empty(client: Client, mock_session: Mock) -> None:
    """Test listing projects when none exist."""
    mock_response = Mock()
    mock_response.json.return_value = {"projects": [], "page": 0, "page_size": 50}
    mock_session.get.return_value = mock_response

    result = client.list_projects("workspace-123", limit=None)

    assert len(result) == 0
    assert mock_session.get.call_count == 1
