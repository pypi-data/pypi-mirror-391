"""FastMCP server for ZSXQ operations"""

from pathlib import Path
from typing import Optional
from fastmcp import FastMCP
from .client import ZSXQClient
from .config import config

# Initialize FastMCP server
mcp = FastMCP("zsxq-mcp")


def get_client(cookie: Optional[str] = None) -> ZSXQClient:
    """
    Get ZSXQ client with proper authentication

    Args:
        cookie: Optional cookie override, defaults to config

    Returns:
        Authenticated ZSXQClient instance

    Raises:
        ValueError: If no cookie is available
    """
    auth_cookie = cookie or config.cookie
    if not auth_cookie:
        raise ValueError(
            "No cookie provided. Please set ZSXQ_COOKIE in .env file or pass cookie parameter"
        )
    return ZSXQClient(auth_cookie)


def get_group_id(group_id: Optional[str] = None) -> str:
    """
    Get group ID from parameter or config

    Args:
        group_id: Optional group ID override

    Returns:
        Group ID to use

    Raises:
        ValueError: If no group ID is available
    """
    target_group = group_id or config.default_group_id
    if not target_group:
        raise ValueError(
            "No group_id provided. Please set ZSXQ_GROUP_ID in .env file or pass group_id parameter"
        )
    return target_group


@mcp.tool()
async def publish_topic(
    content: str,
    group_id: Optional[str] = None,
    cookie: Optional[str] = None,
) -> str:
    """
    Publish a text topic to ZSXQ group

    Args:
        content: The text content to publish
        group_id: Target group ID (optional if set in config)
        cookie: Authentication cookie (optional if set in config)

    Returns:
        Success message with topic URL
    """
    client = get_client(cookie)
    target_group = get_group_id(group_id)

    result = await client.publish_topic(group_id=target_group, content=content)

    topic_id = result.get("topic", {}).get("topic_id")
    return f"✅ Topic published successfully! Topic ID: {topic_id}"


@mcp.tool()
async def publish_topic_from_file(
    file_path: str,
    group_id: Optional[str] = None,
    cookie: Optional[str] = None,
) -> str:
    """
    Publish a topic from a text file to ZSXQ group

    Args:
        file_path: Path to the text file containing content
        group_id: Target group ID (optional if set in config)
        cookie: Authentication cookie (optional if set in config)

    Returns:
        Success message with topic URL
    """
    content_path = Path(file_path)
    if not content_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    content = content_path.read_text(encoding="utf-8")
    return await publish_topic(content=content, group_id=group_id, cookie=cookie)


@mcp.tool()
async def publish_topic_with_images(
    content: str,
    image_paths: list[str],
    group_id: Optional[str] = None,
    cookie: Optional[str] = None,
) -> str:
    """
    Publish a topic with images to ZSXQ group

    Args:
        content: The text content to publish
        image_paths: List of paths to image files to upload
        group_id: Target group ID (optional if set in config)
        cookie: Authentication cookie (optional if set in config)

    Returns:
        Success message with topic URL
    """
    client = get_client(cookie)
    target_group = get_group_id(group_id)

    # Upload all images first
    image_ids = []
    for img_path in image_paths:
        upload_result = await client.upload_image(img_path)
        image_ids.append(upload_result["image_id"])

    # Publish topic with images
    result = await client.publish_topic(
        group_id=target_group, content=content, image_ids=image_ids
    )

    topic_id = result.get("topic", {}).get("topic_id")
    return f"✅ Topic with {len(image_ids)} image(s) published successfully! Topic ID: {topic_id}"


@mcp.tool()
async def upload_image(
    image_path: str,
    cookie: Optional[str] = None,
) -> str:
    """
    Upload an image to ZSXQ (can be used later in posts)

    Args:
        image_path: Path to the image file
        cookie: Authentication cookie (optional if set in config)

    Returns:
        Image ID that can be used in publish_topic
    """
    client = get_client(cookie)
    result = await client.upload_image(image_path)
    return f"✅ Image uploaded successfully! Image ID: {result['image_id']}"


@mcp.tool()
async def get_group_info(
    group_id: Optional[str] = None,
    cookie: Optional[str] = None,
) -> str:
    """
    Get information about a ZSXQ group

    Args:
        group_id: Target group ID (optional if set in config)
        cookie: Authentication cookie (optional if set in config)

    Returns:
        Group information as formatted string
    """
    client = get_client(cookie)
    target_group = get_group_id(group_id)

    info = await client.get_group_info(target_group)

    return f"""
📊 Group Information:
- Name: {info.get('name')}
- Description: {info.get('description', 'N/A')}
- Members: {info.get('members_count', 'N/A')}
- Topics: {info.get('topics_count', 'N/A')}
"""


def main():
    """Main entry point for the package"""
    mcp.run()


if __name__ == "__main__":
    main()
