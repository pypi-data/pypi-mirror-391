"""Configuration management for ZSXQ MCP server"""

import os


class Config:
    """Configuration for ZSXQ MCP server

    Configuration is read from environment variables set in Claude Desktop config:
    - ZSXQ_COOKIE: Authentication cookie from browser
    - ZSXQ_GROUP_ID: Default group/star ID
    """

    def __init__(self):
        # Read from environment variables (set by Claude Desktop MCP config)
        self.cookie = os.getenv("ZSXQ_COOKIE", "")
        self.default_group_id = os.getenv("ZSXQ_GROUP_ID", "")

    @property
    def has_cookie(self) -> bool:
        """Check if cookie is configured"""
        return bool(self.cookie)

    @property
    def has_default_group(self) -> bool:
        """Check if default group ID is configured"""
        return bool(self.default_group_id)


# Global config instance
config = Config()
