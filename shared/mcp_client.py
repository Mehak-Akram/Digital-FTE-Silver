"""
MCP Client for communicating with the Silver Tier MCP Server.

Provides a simple interface to call MCP tools via STDIO.
"""
import asyncio
import json
from pathlib import Path
from typing import Dict, Any, Optional
import subprocess
import sys

sys.path.append(str(Path(__file__).parent.parent))
from shared.logging_config import get_logger

logger = get_logger(__name__)


class MCPClient:
    """
    Client for communicating with MCP server via STDIO.
    """

    def __init__(self, server_script_path: Optional[Path] = None):
        """
        Initialize MCP client.

        Args:
            server_script_path: Path to MCP server script (default: mcp_server/server.py)
        """
        if server_script_path is None:
            server_script_path = Path(__file__).parent.parent / "mcp_server" / "server.py"

        self.server_script_path = server_script_path
        logger.info(f"MCP Client initialized with server: {self.server_script_path}")

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call an MCP tool.

        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments

        Returns:
            Tool result as dictionary

        Raises:
            Exception: If tool call fails
        """
        logger.info(f"Calling MCP tool: {tool_name}")

        try:
            # Import MCP client SDK
            from mcp.client.stdio import stdio_client, StdioServerParameters
            from mcp.client.session import ClientSession

            # Create server parameters
            server_params = StdioServerParameters(
                command="python",
                args=[str(self.server_script_path)],
                env=None
            )

            # Connect to server and call tool
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    # Initialize session
                    await session.initialize()

                    # Call tool
                    result = await session.call_tool(tool_name, arguments)

                    # Parse result
                    logger.debug(f"MCP result: {result}")

                    if result.content and len(result.content) > 0:
                        content = result.content[0]
                        logger.debug(f"Content type: {type(content)}, has text: {hasattr(content, 'text')}")

                        if hasattr(content, 'text'):
                            text = content.text
                            logger.debug(f"Response text: {text[:200] if text else 'EMPTY'}")

                            if text:
                                try:
                                    return json.loads(text)
                                except json.JSONDecodeError as e:
                                    logger.error(f"JSON decode error: {e}, text: {text}")
                                    return {
                                        "success": False,
                                        "error": "JSON_DECODE_ERROR",
                                        "message": f"Failed to parse response: {str(e)}"
                                    }

                    logger.warning("MCP server returned empty or invalid response")
                    return {
                        "success": False,
                        "error": "EMPTY_RESPONSE",
                        "message": "MCP server returned empty response"
                    }

        except Exception as e:
            logger.error(f"MCP tool call failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": "MCP_CLIENT_ERROR",
                "message": str(e)
            }

    def call_tool_sync(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synchronous wrapper for call_tool.

        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments

        Returns:
            Tool result as dictionary
        """
        return asyncio.run(self.call_tool(tool_name, arguments))

    async def send_email(self, to: str, subject: str, body: str,
                        cc: Optional[str] = None,
                        bcc: Optional[str] = None,
                        content_type: str = "text/plain") -> Dict[str, Any]:
        """
        Send an email via MCP server.

        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body
            cc: CC recipients (optional)
            bcc: BCC recipients (optional)
            content_type: Content type (default: text/plain)

        Returns:
            Result dictionary
        """
        arguments = {
            "to": to,
            "subject": subject,
            "body": body,
            "content_type": content_type
        }

        if cc:
            arguments["cc"] = cc
        if bcc:
            arguments["bcc"] = bcc

        return await self.call_tool("send_email", arguments)

    async def post_facebook_page(self, message: str,
                                 link: Optional[str] = None,
                                 published: bool = True) -> Dict[str, Any]:
        """
        Post to Facebook page via MCP server.

        Args:
            message: Post message
            link: Optional link to include
            published: Whether to publish immediately (default: True)

        Returns:
            Result dictionary
        """
        arguments = {
            "message": message,
            "published": published
        }

        if link:
            arguments["link"] = link

        return await self.call_tool("post_facebook_page", arguments)


if __name__ == "__main__":
    # Test MCP client
    async def test():
        client = MCPClient()

        # Test email
        print("Testing send_email...")
        result = await client.send_email(
            to="test@example.com",
            subject="Test Email",
            body="This is a test email from MCP client."
        )
        print(f"Result: {json.dumps(result, indent=2)}")

        # Test Facebook
        print("\nTesting post_facebook_page...")
        result = await client.post_facebook_page(
            message="Test post from MCP client",
            link="https://example.com"
        )
        print(f"Result: {json.dumps(result, indent=2)}")

    asyncio.run(test())
