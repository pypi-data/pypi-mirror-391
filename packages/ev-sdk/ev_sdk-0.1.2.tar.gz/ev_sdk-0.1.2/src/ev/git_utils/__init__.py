import re
import subprocess
from pathlib import Path
from urllib.parse import urlparse

__all__: tuple[str, ...] = (
    "IsNotGitRepoError",
    "clone_repo",
    "extract_repo_name_from_url",
    "get_commit_hash",
    "get_current_branch",
    "get_git_root",
    "get_remote_url",
    "has_remote",
    "is_commit_on_remote",
    "is_dirty",
    "is_git_repo",
)


class IsNotGitRepoError(Exception):
    """Raised when a directory is not a git repository."""


def clone_repo(repo_full_name: str, target: Path, token: str | None = None, branch: str | None = None) -> None:
    """Clone a git repository, with optional GitHub access token for private repos.

    Args:
        repo_full_name: Repository name in format 'https://github.com/owner/repo'
        target: Local path where repository will be cloned
        token: Optional GitHub access token for private repos
        branch: Optional specific branch to clone
    """
    cmd = _make_clone_repo_command(repo_full_name, target, token, branch)
    target.parent.mkdir(exist_ok=True, parents=True)
    subprocess.check_call(cmd)


def _make_clone_repo_command(
    repo_full_name: str, target: Path, token: str | None = None, branch: str | None = None
) -> list[str]:
    """Makes the command that :func:`clone_repo` uses."""
    repo_name = extract_repo_name_from_url(repo_full_name)
    if token is None:
        clone_url = f"https://github.com/{repo_name}.git"
    else:
        clone_url = f"https://x-access-token:{token}@github.com/{repo_name}.git"

    cmd = ["git", "clone"]
    if branch:
        cmd.extend(["--branch", branch])
    cmd.extend([clone_url, str(target)])

    return cmd


def get_commit_hash(git_root: Path | None = None) -> str:
    """Get the commit hash of the current repository.

    If git_root is None, the current working directory is used.
    """
    result = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=git_root)
    output = result.decode("utf-8").strip()
    return output


def get_remote_url(git_root: Path | None = None) -> str:
    """Get the remote URL of the repository.

    If git_root is None, the current working directory is used.
    """
    result = subprocess.check_output(["git", "config", "--get", "remote.origin.url"], cwd=git_root)
    output = result.decode("utf-8").strip()
    return output


def get_git_root(location: Path | None = None) -> Path:
    """Get the absolute path to the git repository root.

    Args:
        location (Path | None): The location to check for a git repository. Defaults to the current working directory.

    Returns:
        Absolute path to the git repository root

    Raises:
        IsNotGitRepo: If the directory is not a git repository.
    """
    try:
        result = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], cwd=location)
    except subprocess.CalledProcessError as e:
        if location is None:
            location = Path.cwd()
        raise IsNotGitRepoError(f"Directory {location} is not a git repository") from e

    output = result.decode("utf-8").strip()
    return Path(output).absolute()


PATTERNS: dict[str, str] = {
    "ssh": r"ssh://git@(?P<domain>[^/]+)/(?P<repo>.+?)(\.git)?$",
    "ssh_scp": r"git@(?P<domain>[^:]+):(?P<repo>.+?)(\.git)?$",  # For git@host:path format
    "http": r"http://(?P<domain>[^/]+)/(?P<repo>.+?)(\.git)?$",
    "https": r"https://(?P<domain>[^/]+)/(?P<repo>.+?)(\.git)?$",
    "git": r"git://(?P<domain>[^/]+)/(?P<repo>.+?)(\.git)?$",
}

COMPILED_PATTERNS: dict[str, re.Pattern[str]] = {proto: re.compile(regex) for proto, regex in PATTERNS.items()}


def extract_repo_name_from_url(repo_url: str) -> str:
    """Extract the repository name from git URL.

    Common formats from git remote -v are:
    - ssh://git@github.com/ohbh/test-daft-workflow.git
    - git@github.com:ohbh/test-daft-workflow.git
    - https://github.com/ohbh/test-daft-workflow.git

    We want to return "ohbh/test-daft-workflow"

    Args:
        repo_url: Git URL in various formats

    Returns:
        Repository name in format 'owner/repo'
    """
    for regex in COMPILED_PATTERNS.values():
        match = regex.match(repo_url)
        if not match:
            continue
        if match.group("domain") != "github.com":
            raise ValueError(f"Unexpected GitHub domain: {match.group('domain')} from {repo_url}")
        return match.group("repo")
    raise ValueError(f"Unable to parse GitHub repository url from {repo_url}")


def get_git_repo_name(repo_url: str) -> str:
    """Extract repository name from git URL."""
    parsed_url = urlparse(repo_url)
    path_parts = parsed_url.path.strip("/").split("/")
    if len(path_parts) >= 2:
        repo_name = path_parts[-1]
        return repo_name.removesuffix(".git")
    else:
        return Path(Path.cwd()).name


def is_git_repo() -> bool:
    """Check if current directory is inside a git repository."""
    result = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        capture_output=True,  # so we don't print to STDOUT
        check=False,  # Don't raise an exception if the process exits with a non-zero status code
    )
    return result.returncode == 0


def has_remote(remote_name: str = "origin", git_root: Path | None = None) -> bool:
    """Check if git repository has a specific remote configured.

    If git_root is None, the current working directory is used.
    """
    result = subprocess.check_output(["git", "remote", "-v"], cwd=git_root)
    output = result.decode("utf-8").strip()
    return remote_name in output


def get_current_branch(git_root: Path | None = None) -> str | None:
    """Get the current branch name.

    Args:
        git_root: The root directory of the git repository.
                  Defaults to the current working directory if None.

    Returns:
        Current branch name or None if repo is empty and has no commits

    Raises:
        subprocess.CalledProcessError: If not in a git repository
    """
    try:
        result = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=git_root,
            stderr=subprocess.PIPE,
        )
        output = result.decode("utf-8").strip()
        return output
    except subprocess.CalledProcessError as e:
        # git returns an error if there are no commits in the repository
        stderr = ""
        if hasattr(e, "stderr") and e.stderr:
            stderr = e.stderr.decode("utf-8")
        elif hasattr(e, "output") and e.output:
            stderr = e.output.decode("utf-8")
        # fatal: ambiguous argument 'HEAD': unknown revision or path not in the working tree.
        if "unknown revision or path not in the working tree" in stderr or "HEAD" in stderr:
            return None
        raise


def is_dirty(git_root: Path) -> bool:
    """Check if git repository has uncommitted changes."""
    result = subprocess.check_output(["git", "status", "--porcelain"], cwd=git_root)
    output = result.decode("utf-8").strip()
    return len(output) > 0


def is_commit_on_remote(git_root: Path, git_remote: str, git_commit: str) -> bool:
    """
    Check if a git commit exists on the remote without changing the checked-out state.

    Args:
        git_root: The root directory of the git repository
        git_remote: The remote URL to check against
        git_commit: The commit hash to check

    Returns:
        True if the commit exists on the remote, False otherwise.

    Raises:
        IsNotGitRepo: If the directory is not a git repository.
    """

    # check that `git_root` is a valid git repository
    get_git_root(git_root)  # raises exception if not a git repo

    try:
        # Fetch from remote to ensure we have the latest refs
        subprocess.run(
            ["git", "fetch", git_remote],
            cwd=git_root,
            capture_output=True,  # so we don't print to STDOUT
            check=True,
        )

        # Check if the commit exists in any remote branch
        # This uses 'git branch -r --contains' which checks remote branches
        result = subprocess.run(
            ["git", "branch", "-r", "--contains", git_commit], cwd=git_root, capture_output=True, check=True
        )
        output = result.stdout.decode("utf-8").strip()
        # git will say something like:
        # error: no such commit XYZ
        # if commit XYZ isn't in any of the branches, remote or local

        # If the command succeeded and returned any branches, the commit exists on remote
        return result.returncode == 0 and bool(len(output) > 0)

    except subprocess.CalledProcessError:
        # If fetch or branch command fails, assume commit is not on remote
        return False
