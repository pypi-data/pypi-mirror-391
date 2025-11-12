from pathlib import Path

import toml

__all__: tuple[str, ...] = ("RuntimeEnvResolver",)


class RuntimeEnvResolver:
    def __init__(self, cwd: Path, git_root: Path, env_file: Path | None = None) -> None:
        self.cwd = cwd
        self.git_root = git_root
        self.env_file = env_file

    def resolve_dependencies(self) -> list[str]:
        """Resolve dependencies by checking each directory from cwd up to git_root.

        For each directory, checks for either pyproject.toml or requirements.txt (not both).
        Returns the first set of dependencies found.
        """
        current_dir = self.cwd

        while True:
            # Error if both exist
            pyproject_exists = self._pyproject_exists(current_dir)
            requirements_exists = self._requirements_exists(current_dir)
            if pyproject_exists and requirements_exists:
                raise ValueError(
                    f"Both pyproject.toml and requirements.txt found in {current_dir}. Please use only one."
                )

            if pyproject_exists:
                return self._parse_pyproject_toml(current_dir)

            if requirements_exists:
                return self._parse_requirements_txt(current_dir)

            if current_dir == self.git_root or current_dir == current_dir.parent:
                break

            # Move up one directory
            current_dir = current_dir.parent

        return []

    def resolve_python_version(self) -> str | None:
        """Resolve Python version by checking each directory from cwd up to git_root."""
        current_dir = self.cwd

        while True:
            version = self._read_python_version_file(current_dir)
            if version:
                return version

            if current_dir == self.git_root or current_dir == current_dir.parent:
                break

            current_dir = current_dir.parent

        return None

    def resolve_environment_secrets(self) -> dict[str, str]:
        """Resolve environment variables from env file.

        Returns the parsed environment variables from the env file.
        """
        if self.env_file is None:
            return {}

        env_vars: dict[str, str] = {}

        try:
            with self.env_file.open(encoding="utf-8") as f:
                for line in f:
                    stripped_line = line.strip()
                    # Skip empty lines and comments
                    if not stripped_line or stripped_line.startswith("#"):
                        continue

                    # Parse KEY=VALUE format
                    if "=" in stripped_line:
                        key, value = stripped_line.split("=", 1)
                        key = key.strip()
                        value = value.strip()

                        # Remove quotes if present
                        if (value.startswith('"') and value.endswith('"')) or (
                            value.startswith("'") and value.endswith("'")
                        ):
                            value = value[1:-1]

                        env_vars[key] = value
        except Exception as e:
            raise ValueError(f"Failed to parse environment variables from {self.env_file}: {e}")

        return env_vars

    def _pyproject_exists(self, directory: Path) -> bool:
        """Check if pyproject.toml exists in the given directory."""
        pyproject_path = directory / "pyproject.toml"
        return pyproject_path.exists()

    def _requirements_exists(self, directory: Path) -> bool:
        """Check if requirements.txt exists in the given directory."""
        requirements_path = directory / "requirements.txt"
        return requirements_path.exists()

    def _parse_pyproject_toml(self, directory: Path) -> list[str]:
        """Parse dependencies from pyproject.toml file."""
        pyproject_path = directory / "pyproject.toml"

        try:
            pyproject_data = toml.load(pyproject_path)

            if "project" in pyproject_data and "dependencies" in pyproject_data["project"]:
                return pyproject_data["project"]["dependencies"]  # type: ignore

            return []
        except Exception:
            return []

    def _parse_requirements_txt(self, directory: Path) -> list[str]:
        """Parse dependencies from requirements.txt file."""
        req_path = directory / "requirements.txt"

        dependencies: list[str] = []
        try:
            with req_path.open() as f:
                for line in f:
                    stripped_line = line.strip()
                    if not stripped_line or stripped_line.startswith("#"):
                        continue
                    dependencies.append(stripped_line)

            return dependencies
        except Exception:
            return []

    def _read_python_version_file(self, directory: Path) -> str | None:
        """Read Python version from .python-version file."""
        python_version_path = directory / ".python-version"
        if not python_version_path.exists():
            return None

        try:
            with python_version_path.open() as f:
                version = f.read().strip()
                if version:
                    return version
        except Exception:
            pass

        return None
