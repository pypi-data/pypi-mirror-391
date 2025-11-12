import os
import logging

from dotenv import load_dotenv
from typing import Optional


class Config:
    """Configuration management class for XGA Tools."""

    def __init__(self, env_file: str = ".env"):
        load_dotenv(env_file)

        self.TAVILY_API_KEY     = self._get_env_var("TAVILY_API_KEY")

        self.FIRECRAWL_API_KEY  = self._get_env_var("FIRECRAWL_API_KEY")
        self.FIRECRAWL_URL      = self._get_env_var("FIRECRAWL_URL", "https://api.firecrawl.dev")

        self.DAYTONA_API_KEY            = self._get_env_var("DAYTONA_API_KEY")
        self.DAYTONA_SERVER_URL         = self._get_env_var("DAYTONA_SERVER_URL", "https://app.daytona.io/api")
        self.DAYTONA_TARGET             = self._get_env_var("DAYTONA_TARGET", "us")
        self.DAYTONA_IMAGE_NAME         = self._get_env_var("DAYTONA_IMAGE_NAME", "kortix/suna:0.1.3")

        self.SANDBOX_TIMEOUT_MINUTE     = int(self._get_env_var("SANDBOX_TIMEOUT_MINUTE", "6"))

        self._validate_config()


    def _get_env_var(self, key: str, default: Optional[str] = None) -> Optional[str]:
        value = os.getenv(key, default)
        if value is None:
            logging.warning(f"Environment variable {key} not found and no default provided")
        return value


    def _validate_config(self):
        """Validate that required configuration values are present."""
        required_vars = {
            'TAVILY_API_KEY'    : self.TAVILY_API_KEY,
            'FIRECRAWL_API_KEY' : self.FIRECRAWL_API_KEY,
            'DAYTONA_API_KEY'   : self.DAYTONA_API_KEY,
        }

        missing_vars = [key for key, value in required_vars.items() if not value]

        if missing_vars:
            error_msg = f"Missing required configuration variables: {', '.join(missing_vars)}"
            logging.error(error_msg)
            raise ValueError(error_msg)


    def get_tavily_config(self) -> dict:
        return {
            'api_key': self.TAVILY_API_KEY
        }


    def get_firecrawl_config(self) -> dict:
        return {
            'api_key'   : self.FIRECRAWL_API_KEY,
            'url'       : self.FIRECRAWL_URL
        }


    def get_daytona_config(self) -> dict:
        return {
            'api_key'           : self.DAYTONA_API_KEY,
            'server_url'        : self.DAYTONA_SERVER_URL,
            'target'            : self.DAYTONA_TARGET,
            'image_name'        : self.DAYTONA_IMAGE_NAME,
            'timeout'           : self.SANDBOX_TIMEOUT_MINUTE,
        }


# Global configuration instance
config = Config()

