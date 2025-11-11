import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from zsxq_mcp.server import mcp, get_client
from zsxq_mcp.client import ZSXQClient
from zsxq_mcp.config import Config, config


def test_server_creation():
    """Test that the server can be created successfully."""
    assert mcp is not None
    assert hasattr(mcp, 'run')


def test_config_initialization():
    """Test Config class initialization."""
    test_config = Config()
    assert hasattr(test_config, 'cookie')
    assert hasattr(test_config, 'default_group_id')


def test_get_client_with_cookie():
    """Test get_client function with provided cookie."""
    with patch('zsxq_mcp.server.config') as mock_config:
        mock_config.cookie = "test_cookie"

        client = get_client("test_cookie_override")
        assert client is not None
        assert isinstance(client, ZSXQClient)


def test_get_client_no_cookie_raises_error():
    """Test get_client raises error when no cookie available."""
    with patch('zsxq_mcp.server.config') as mock_config:
        mock_config.cookie = None

        with pytest.raises(ValueError, match="No cookie provided"):
            get_client()


@pytest.mark.asyncio
async def test_async_mock_example():
    """Example of async test with mocking."""
    mock_client = AsyncMock()
    mock_client.publish_topic.return_value = {"success": True}

    result = await mock_client.publish_topic("test content")
    assert result["success"] is True


@pytest.mark.asyncio
async def test_upload_image_mock():
    """Example of async test for image upload."""
    mock_client = AsyncMock()
    mock_client.upload_image.return_value = {"success": True, "image_id": 123}

    result = await mock_client.upload_image("/path/to/image.jpg")
    assert result["success"] is True
    assert result["image_id"] == 123


if __name__ == "__main__":
    pytest.main([__file__])