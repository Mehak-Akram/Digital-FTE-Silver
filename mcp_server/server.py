"""
MCP Server for Silver Tier AI Employee.

Provides external integration functions (email, Facebook) with rate limiting and logging.
"""
import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Import MCP SDK
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
except ImportError:
    print("Warning: MCP SDK not available. Install with: pip install mcp")
    Server = None

# Import local modules
import sys
sys.path.append(str(Path(__file__).parent.parent))

from shared.logging_config import get_logger
from mcp_server.rate_limiter import RateLimiter

# Load environment variables
load_dotenv()

# Initialize logger
logger = get_logger(__name__, "mcp-server.log")

# Load configuration
CONFIG_PATH = Path(__file__).parent / "config.json"


def load_config() -> Dict[str, Any]:
    """Load MCP server configuration from config.json."""
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Configuration file not found: {CONFIG_PATH}")

    with open(CONFIG_PATH, 'r') as f:
        config = json.load(f)

    # Substitute environment variables
    config_str = json.dumps(config)
    for key, value in os.environ.items():
        config_str = config_str.replace(f"${{{key}}}", value)

    return json.loads(config_str)


class SilverTierMCPServer:
    """
    MCP Server for Silver Tier external integrations.

    Provides send_email and post_facebook_page functions with rate limiting.
    """

    def __init__(self):
        """Initialize MCP server with configuration."""
        self.config = load_config()
        self.server_name = self.config["server_name"]
        self.version = self.config["version"]

        # Initialize rate limiter
        rate_limits = {
            "send_email": self.config["rate_limits"]["email_per_hour"],
            "post_facebook_page": self.config["rate_limits"]["facebook_per_hour"]
        }
        self.rate_limiter = RateLimiter(rate_limits)

        # Initialize MCP server
        if Server is None:
            logger.error("MCP SDK not available. Server cannot start.")
            self.server = None
        else:
            self.server = Server(self.server_name)
            self._register_handlers()
            self._register_tools()

        logger.info(f"MCP Server initialized: {self.server_name} v{self.version}")

    def _register_handlers(self):
        """Register MCP protocol handlers."""
        if self.server is None:
            return

        # Register list_tools handler
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available tools."""
            return [
                Tool(
                    name="send_email",
                    description="Send an email via SMTP",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "to": {"type": "string", "description": "Recipient email address"},
                            "subject": {"type": "string", "description": "Email subject"},
                            "body": {"type": "string", "description": "Email body"},
                            "cc": {"type": "string", "description": "CC recipients (optional)"},
                            "bcc": {"type": "string", "description": "BCC recipients (optional)"},
                            "content_type": {"type": "string", "description": "Content type (default: text/plain)"}
                        },
                        "required": ["to", "subject", "body"]
                    }
                ),
                Tool(
                    name="post_facebook_page",
                    description="Post to a Facebook Page",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "message": {"type": "string", "description": "Post message"},
                            "link": {"type": "string", "description": "Optional link to include"},
                            "published": {"type": "boolean", "description": "Whether to publish immediately (default: true)"}
                        },
                        "required": ["message"]
                    }
                )
            ]

    def _register_tools(self):
        """Register MCP tools (functions)."""
        if self.server is None:
            return

        # Register unified tool handler that routes based on tool name
        @self.server.call_tool()
        async def handle_tool_call(name: str, arguments: dict) -> list[TextContent]:
            """
            Handle tool calls and route to appropriate handler.

            Args:
                name: Tool name ("send_email" or "post_facebook_page")
                arguments: Tool-specific arguments

            Returns:
                List of TextContent with result
            """
            logger.info(f"Tool call received: {name}")

            if name == "send_email":
                return await self._handle_send_email(arguments)
            elif name == "post_facebook_page":
                return await self._handle_post_facebook_page(arguments)
            else:
                logger.error(f"Unknown tool: {name}")
                return [TextContent(type="text", text=json.dumps({
                    "success": False,
                    "error": "UNKNOWN_TOOL",
                    "message": f"Tool '{name}' not found",
                    "timestamp": datetime.now().isoformat()
                }))]

        logger.info("MCP tools registered: send_email, post_facebook_page")

    async def _handle_send_email(self, arguments: dict) -> list[TextContent]:
        """
        Handle send_email function call.

        Args:
            arguments: Email parameters

        Returns:
            Result as TextContent list
        """
        function_name = "send_email"

        logger.info(f"_handle_send_email called with arguments: {arguments}")

        # Check rate limit
        if not self.rate_limiter.check_limit(function_name):
            remaining = self.rate_limiter.get_remaining_calls(function_name)
            reset_time = self.rate_limiter.get_reset_time(function_name)
            error_msg = f"Rate limit exceeded. Remaining: {remaining}. Reset at: {reset_time}"
            logger.warning(f"{function_name} rate limit exceeded")
            return [TextContent(type="text", text=json.dumps({
                "success": False,
                "error": "RATE_LIMIT_EXCEEDED",
                "message": error_msg,
                "timestamp": datetime.now().isoformat()
            }))]

        # Record call
        self.rate_limiter.record_call(function_name)

        # Log request
        logger.info(f"{function_name} called with to={arguments.get('to')}, subject={arguments.get('subject')}")

        # Import email handler
        try:
            from mcp_server.email_handler import EmailHandler
            email_handler = EmailHandler()
        except Exception as e:
            logger.error(f"Failed to initialize email handler: {e}", exc_info=True)
            return [TextContent(type="text", text=json.dumps({
                "success": False,
                "error": "HANDLER_INITIALIZATION_ERROR",
                "message": f"Failed to initialize email handler: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }))]

        # Send email
        try:
            result = email_handler.send_email(
                to=arguments.get('to'),
                subject=arguments.get('subject'),
                body=arguments.get('body'),
                cc=arguments.get('cc'),
                bcc=arguments.get('bcc'),
                content_type=arguments.get('content_type', 'text/plain')
            )
            return [TextContent(type="text", text=json.dumps(result))]
        except Exception as e:
            logger.error(f"Email sending failed: {e}", exc_info=True)
            return [TextContent(type="text", text=json.dumps({
                "success": False,
                "error": "EMAIL_SEND_ERROR",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }))]

    async def _handle_post_facebook_page(self, arguments: dict) -> list[TextContent]:
        """
        Handle post_facebook_page function call.

        Args:
            arguments: Facebook post parameters

        Returns:
            Result as TextContent list
        """
        function_name = "post_facebook_page"

        logger.info(f"_handle_post_facebook_page called with arguments: {arguments}")

        # Check rate limit
        if not self.rate_limiter.check_limit(function_name):
            remaining = self.rate_limiter.get_remaining_calls(function_name)
            reset_time = self.rate_limiter.get_reset_time(function_name)
            error_msg = f"Rate limit exceeded. Remaining: {remaining}. Reset at: {reset_time}"
            logger.warning(f"{function_name} rate limit exceeded")
            return [TextContent(type="text", text=json.dumps({
                "success": False,
                "error": "RATE_LIMIT_EXCEEDED",
                "message": error_msg,
                "timestamp": datetime.now().isoformat()
            }))]

        # Record call
        self.rate_limiter.record_call(function_name)

        # Log request
        message_preview = arguments.get('message', '')[:50]
        logger.info(f"{function_name} called with message={message_preview}...")

        # Import Facebook handler
        try:
            from mcp_server.facebook_handler import FacebookHandler
            facebook_handler = FacebookHandler()
        except Exception as e:
            logger.error(f"Failed to initialize Facebook handler: {e}", exc_info=True)
            return [TextContent(type="text", text=json.dumps({
                "success": False,
                "error": "HANDLER_INITIALIZATION_ERROR",
                "message": f"Failed to initialize Facebook handler: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }))]

        # Post to Facebook
        try:
            result = facebook_handler.post_facebook_page(
                message=arguments.get('message'),
                link=arguments.get('link'),
                published=arguments.get('published', True)
            )
            return [TextContent(type="text", text=json.dumps(result))]
        except Exception as e:
            logger.error(f"Facebook posting failed: {e}", exc_info=True)
            return [TextContent(type="text", text=json.dumps({
                "success": False,
                "error": "FACEBOOK_POST_ERROR",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }))]

    async def run(self):
        """Run the MCP server."""
        if self.server is None:
            logger.error("Cannot run server: MCP SDK not available")
            return

        logger.info(f"Starting MCP server: {self.server_name}")
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


def main():
    """Main entry point for MCP server."""
    import asyncio

    try:
        server = SilverTierMCPServer()
        asyncio.run(server.run())
    except Exception as e:
        logger.error(f"MCP server error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
