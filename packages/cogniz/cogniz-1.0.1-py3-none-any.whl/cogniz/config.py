"""Configuration management for Cogniz SDK."""

import os
from typing import Optional
from cogniz.errors import ValidationError


class Config:
    """
    Cogniz SDK configuration.

    Args:
        api_key: Your Cogniz API key (starts with 'mp_')
        base_url: Platform base URL (default: https://cogniz.online)
        project_id: Default project ID
        timeout: Request timeout in seconds (default: 30)

    Example:
        >>> config = Config(api_key="mp_...")
        >>> config = Config.from_env()  # Load from environment
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        project_id: Optional[str] = None,
        timeout: int = 30
    ):
        self.api_key = api_key or os.getenv("COGNIZ_API_KEY")
        self.base_url = (base_url or os.getenv("COGNIZ_BASE_URL", "https://cogniz.online")).rstrip("/")
        self.project_id = project_id or os.getenv("COGNIZ_PROJECT_ID")
        self.timeout = timeout

        if not self.api_key:
            raise ValidationError(
                "API key is required. Set COGNIZ_API_KEY environment variable "
                "or pass api_key parameter."
            )

    @classmethod
    def from_env(cls) -> "Config":
        """
        Create configuration from environment variables.

        Environment Variables:
            COGNIZ_API_KEY: API key (required)
            COGNIZ_BASE_URL: Base URL (optional, default: https://cogniz.online)
            COGNIZ_PROJECT_ID: Default project ID (optional)

        Returns:
            Config instance

        Example:
            >>> config = Config.from_env()
        """
        return cls()

    @property
    def api_endpoint(self) -> str:
        """Get full API endpoint URL."""
        return f"{self.base_url}/wp-json/memory/v1"

    @property
    def skills_endpoint(self) -> str:
        """Get skills API endpoint URL."""
        return f"{self.base_url}/wp-json/cogniz/v1"

    def get_headers(self) -> dict:
        """Get HTTP headers for requests."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": f"cogniz-python/{self._get_version()}",
            "X-Memory-Platform-Client": "python-sdk"
        }

    def _get_version(self) -> str:
        """Get SDK version."""
        try:
            from cogniz import __version__
            return __version__
        except:
            return "1.0.0"

    def __repr__(self) -> str:
        return f"Config(base_url='{self.base_url}', project_id={self.project_id})"
