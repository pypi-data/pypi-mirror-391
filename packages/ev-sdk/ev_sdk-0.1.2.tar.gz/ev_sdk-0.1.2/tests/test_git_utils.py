"""Tests for git_utils module."""

import pytest
from ev.git_utils import extract_repo_name_from_url


@pytest.mark.parametrize(
    ("url", "expected", "message"),
    [
        (
            "ssh://git@github.com/ohbh/test-daft-workflow.git",
            "ohbh/test-daft-workflow",
            "Test SSH URL with .git extension.",
        ),
        (
            "ssh://git@github.com/ohbh/test-daft-workflow",
            "ohbh/test-daft-workflow",
            "Test SSH URL without .git extension.",
        ),
        (
            "git@github.com:ohbh/test-daft-workflow.git",
            "ohbh/test-daft-workflow",
            "Test SSH SCP format with .git extension.",
        ),
        (
            "git@github.com:ohbh/test-daft-workflow",
            "ohbh/test-daft-workflow",
            "Test SSH SCP format without .git extension.",
        ),
        (
            "https://github.com/ohbh/test-daft-workflow.git",
            "ohbh/test-daft-workflow",
            "Test HTTPS URL with .git extension.",
        ),
        (
            "https://github.com/ohbh/test-daft-workflow",
            "ohbh/test-daft-workflow",
            "Test HTTPS URL without .git extension.",
        ),
        (
            "http://github.com/ohbh/test-daft-workflow.git",
            "ohbh/test-daft-workflow",
            "Test HTTP URL with .git extension.",
        ),
        (
            "http://github.com/ohbh/test-daft-workflow",
            "ohbh/test-daft-workflow",
            "Test HTTP URL without .git extension.",
        ),
        (
            "git://github.com/ohbh/test-daft-workflow.git",
            "ohbh/test-daft-workflow",
            "Test git:// protocol with .git extension.",
        ),
        (
            "git://github.com/ohbh/test-daft-workflow",
            "ohbh/test-daft-workflow",
            "Test git:// protocol without .git extension.",
        ),
        (
            "https://github.com/org/suborg/repo-name.git",
            "org/suborg/repo-name",
            "Test repository with nested path structure: https & .git extension.",
        ),
        (
            "https://github.com/org/suborg/repo-name",
            "org/suborg/repo-name",
            "Test repository with nested path structure: https & without .git extension.",
        ),
        (
            "http://github.com/org/suborg/repo-name.git",
            "org/suborg/repo-name",
            "Test repository with nested path structure: http & .git extension.",
        ),
        (
            "http://github.com/org/suborg/repo-name",
            "org/suborg/repo-name",
            "Test repository with nested path structure: http & without .git extension.",
        ),
    ],
)
def test_extract_repo_name_from_url(url: str, expected: str, message: str) -> None:
    actual = extract_repo_name_from_url(url)
    assert actual == expected, f"{actual=} {expected=} | {message}"


@pytest.mark.parametrize(
    ("url", "expected_error_message"),
    [
        ("https://gitlab.com/user/repo", "Unexpected GitHub domain"),  # Test that non-GitHub domains raise ValueError.
        ("not-a-git-url", "Unable to parse GitHub repository url"),  # Test that invalid URLs raise ValueError.
        ("", "Unable to parse GitHub repository url"),  # Test that empty URLs raise ValueError.
    ],
)
def test_invalid_repo_name(url: str, expected_error_message: str) -> None:
    with pytest.raises(ValueError, match=expected_error_message):
        extract_repo_name_from_url(url)
