"""CLI context management for dependency injection."""

from __future__ import annotations

import click

from ev.cli.config import Config
from ev.cli.credentials import AuthorizationError, Credentials, Token
from ev.cli.project_config import ProjectConfig, load_project_config
from ev.client import Client
from ev.git_utils import get_git_root


class Context:
    """Context object holding configuration and client for CLI commands."""

    def __init__(
        self,
        config: Config,
        project_config: ProjectConfig | None = None,
    ) -> None:
        """Private constructor. Use Context.load() to create instances.

        Args:
            config: Configuration instance for the active profile
            project_config: Project configuration from ev.toml
        """
        self._config = config
        self._project_config = project_config
        self._token: Token | None = None
        self._client: Client | None = None

    @classmethod
    def load(cls, profile: str | None = None) -> Context:
        """Load context with configuration for the given profile.

        Args:
            profile: Profile name to load, defaults to 'default'

        Returns:
            Context instance with loaded configuration
        """
        profile = profile or "default"
        config = Config.load(profile)

        # Try to load the project config, otherwise None
        try:
            pconf = load_project_config(get_git_root() / "ev.toml")
        except Exception:
            pconf = None

        return cls(
            config=config,
            project_config=pconf,
        )

    @property
    def config(self) -> Config:
        """Get the config object.

        Returns:
            Config instance for this context.
        """
        return self._config

    def token(self) -> Token:
        """Get the authentication token, loading and refreshing if needed.

        Returns:
            Valid authentication token.

        Raises:
            click.ClickException: If credentials are not found or refresh fails.
        """
        # Load token from cache or disk
        if self._token is None:
            self._token = Credentials.load(self._config.profile)
            if self._token is None:
                raise click.ClickException(
                    f"No credentials found for profile '{self._config.profile}'.\n"
                    f"Please run 'ev login' to authenticate."
                )

        # Check if token is expired or expiring soon
        if Credentials.is_expired(self._token):
            try:
                self._token = Credentials.refresh(self._config.endpoint_url, self._token)
                Credentials.save(self._config.profile, self._token)
                # Invalidate client so it gets recreated with new token
                self._client = None
            except AuthorizationError:
                raise click.ClickException(
                    "Credentials expired and refresh failed. Please run 'ev login' to re-authenticate."
                )

        return self._token

    @property
    def workspace_id(self) -> str:
        """Get the workspace ID from the authenticated token.

        Returns:
            Workspace ID string.

        Raises:
            click.ClickException: If credentials are not found for the profile.
        """
        return self.token().workspace_id

    @property
    def project_id(self) -> str:
        """Get the project ID from the project configuration.

        Returns:
            Project ID string.

        Raises:
            AttributeError: If project_config is not loaded or doesn't have project_id.
        """
        if self._project_config is None:
            raise click.ClickException("No project found!\nPlease run 'ev init' to initialize the project.")
        return self._project_config.project_id

    @property
    def client(self) -> Client:
        """Get or create the client instance lazily.

        Returns:
            Client instance configured with endpoint from config and access token from token.

        Raises:
            click.ClickException: If credentials are not found for the profile.
        """
        # Create a new client if needed
        if self._client is None:
            token = self.token()
            self._client = Client(
                endpoint=self._config.endpoint_url,
                access_token=token.access_token,
            )

        return self._client


# Create pass decorator for Click context
pass_context = click.make_pass_decorator(Context)
