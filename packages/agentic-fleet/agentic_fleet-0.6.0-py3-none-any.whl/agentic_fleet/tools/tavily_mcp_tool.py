"""Tavily web search tool integration via MCP (Model Context Protocol).

Uses agent-framework's MCPStreamableHTTPTool to connect to Tavily's MCP server,
providing better integration with agent-framework's ChatAgent and improved
tool invocation reliability.
"""

import logging
import os
from typing import Any, Optional, TYPE_CHECKING


if TYPE_CHECKING:  # pragma: no cover - typing helper
    from agent_framework import MCPStreamableHTTPTool
else:
    try:
        from agent_framework import MCPStreamableHTTPTool
    except (ImportError, ModuleNotFoundError, AttributeError):  # pragma: no cover - optional dep

        class MCPStreamableHTTPTool:  # type: ignore[too-many-ancestors]
            """Fallback MCPStreamableHTTPTool for test environments."""

            def __init__(self, *args: Any, **kwargs: Any):
                self.name = kwargs.get("name", "tavily_search")
                self.description = kwargs.get("description", "")


logger = logging.getLogger(__name__)


class TavilyMCPTool(MCPStreamableHTTPTool):
    """
    Web search tool using Tavily API via MCP protocol.

    This tool connects to Tavily's MCP server and automatically loads
    available tools from the server. It provides better integration
    with agent-framework's ChatAgent compared to direct API integration.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Tavily MCP tool.

        Args:
            api_key: Tavily API key (defaults to TAVILY_API_KEY env var)

        Raises:
            ValueError: If API key is not provided
        """
        api_key = api_key or os.getenv("TAVILY_API_KEY")
        if not api_key:
            raise ValueError("TAVILY_API_KEY must be set in environment or passed to constructor")

        # Construct MCP URL with API key
        mcp_url = f"https://mcp.tavily.com/mcp/?tavilyApiKey={api_key}"

        # Enhanced description to emphasize mandatory usage for time-sensitive queries
        description = (
            "MANDATORY: Use this tool for ANY query about events, dates, or information from 2024 onwards. "
            "Search the web for real-time information using Tavily. Provides accurate, up-to-date results with source citations. "
            "ALWAYS use this tool when asked about recent events, current data, elections, news, or anything requiring current information. "
            "Never rely on training data for time-sensitive queries."
        )

        # Initialize MCPStreamableHTTPTool
        # The MCP server will provide the actual tool schemas, so we set load_tools=True
        # and load_prompts=False since we only need tools
        super().__init__(
            name="tavily_search",
            url=mcp_url,
            description=description,
            load_tools=True,
            load_prompts=False,
        )

        # Ensure downstream consumers can rely on explicit attributes even if the base class changes
        self.name = "tavily_search"
        self.description = description

        logger.info(f"Initialized TavilyMCPTool with MCP URL: {mcp_url[:50]}...")
