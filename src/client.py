"""
MongoDB MCP Client - Core client implementation.

This module provides a client for interacting with MongoDB through the
Model Context Protocol (MCP) using Claude AI for natural language processing.
"""

import json
import os
from typing import Any, Optional

from anthropic import Anthropic
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from .exceptions import MCPConnectionError, MCPQueryError

console = Console()


class MongoDBMCPClient:
    """
    A client for querying MongoDB using natural language through Claude AI and MCP.

    This client connects to a MongoDB MCP server and uses Claude AI to translate
    natural language queries into MongoDB operations, execute them, and return
    human-readable results.

    Attributes:
        connection_string: MongoDB connection URI
        model: Claude model to use (default: claude-sonnet-4-20250514)
        verbose: Whether to print detailed execution info

    Example:
        >>> async with MongoDBMCPClient("mongodb+srv://...") as client:
        ...     result = await client.query("How many documents are in my_collection?")
        ...     print(result["response"])
    """

    def __init__(
        self,
        connection_string: Optional[str] = None,
        model: str = "claude-sonnet-4-20250514",
        verbose: bool = True,
    ):
        """
        Initialize the MongoDB MCP Client.

        Args:
            connection_string: MongoDB connection URI. If not provided,
                              uses MDB_MCP_CONNECTION_STRING env variable.
            model: Claude model identifier to use for queries.
            verbose: If True, prints detailed execution information.
        """
        self.connection_string = connection_string or os.getenv(
            "MDB_MCP_CONNECTION_STRING"
        )
        if not self.connection_string:
            raise ValueError(
                "MongoDB connection string is required. "
                "Provide it directly or set MDB_MCP_CONNECTION_STRING environment variable."
            )

        self.model = model
        self.verbose = verbose
        self.anthropic_client = Anthropic()
        self.session: Optional[ClientSession] = None
        self.tools: list[dict[str, Any]] = []
        self._stdio_transport = None
        self._read_stream = None
        self._write_stream = None

    async def __aenter__(self) -> "MongoDBMCPClient":
        """Async context manager entry - connects to MCP server."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit - closes connections."""
        await self.close()

    async def connect(self) -> None:
        """
        Connect to the MongoDB MCP server.

        Raises:
            MCPConnectionError: If connection to MCP server fails.
        """
        try:
            server_params = StdioServerParameters(
                command="npx",
                args=["-y", "mongodb-mcp-server"],
                env={
                    "MDB_MCP_CONNECTION_STRING": self.connection_string,
                    "PATH": os.environ.get("PATH", ""),
                },
            )

            # Create stdio transport and session
            self._stdio_transport = stdio_client(server_params)
            transport_context = await self._stdio_transport.__aenter__()
            self._read_stream, self._write_stream = transport_context

            self.session = ClientSession(self._read_stream, self._write_stream)
            await self.session.__aenter__()
            await self.session.initialize()

            # Get available tools from MCP server
            tools_response = await self.session.list_tools()
            self.tools = [
                {
                    "name": tool.name,
                    "description": tool.description or "",
                    "input_schema": tool.inputSchema,
                }
                for tool in tools_response.tools
            ]

            if self.verbose:
                console.print(
                    Panel(
                        f"[green]✓ Connected to MongoDB MCP Server[/green]\n"
                        f"[dim]Available tools: {len(self.tools)}[/dim]",
                        title="Connection Status",
                        border_style="green",
                    )
                )

        except Exception as e:
            raise MCPConnectionError(f"Failed to connect to MCP server: {e}") from e

    async def close(self) -> None:
        """Close all connections gracefully."""
        if self.session:
            await self.session.__aexit__(None, None, None)
            self.session = None
        if self._stdio_transport:
            await self._stdio_transport.__aexit__(None, None, None)
            self._stdio_transport = None

        if self.verbose:
            console.print("[dim]Connection closed.[/dim]")

    async def query(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Execute a natural language query against MongoDB.

        Args:
            prompt: Natural language query describing what you want to know.
            system_prompt: Optional custom system prompt for Claude.

        Returns:
            Dictionary containing:
                - response: Human-readable response from Claude
                - tool_calls: List of MongoDB operations executed
                - raw_results: Raw results from MongoDB (if any)

        Raises:
            MCPQueryError: If query execution fails.
            MCPConnectionError: If not connected to MCP server.
        """
        if not self.session:
            raise MCPConnectionError("Not connected. Call connect() first.")

        default_system = """You are a MongoDB expert assistant. When users ask questions about their data:
1. Use the available MongoDB tools to query the database
2. Analyze the results and provide clear, helpful responses
3. If you need to run multiple queries, do so to get complete answers
4. Format numbers and data in a readable way
5. If an error occurs, explain what went wrong and suggest fixes"""

        messages = [{"role": "user", "content": prompt}]
        tool_calls_made = []
        raw_results = []

        try:
            if self.verbose:
                console.print(
                    Panel(prompt, title="[bold blue]Query[/bold blue]", border_style="blue")
                )

            # Initial Claude API call
            response = self.anthropic_client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=system_prompt or default_system,
                tools=self.tools,
                messages=messages,
            )

            # Process tool calls iteratively
            while response.stop_reason == "tool_use":
                # Find tool use blocks
                tool_use_blocks = [
                    block for block in response.content if block.type == "tool_use"
                ]

                # Build message with assistant's response
                messages.append({"role": "assistant", "content": response.content})

                # Process each tool call
                tool_results = []
                for tool_use_block in tool_use_blocks:
                    tool_name = tool_use_block.name
                    tool_input = tool_use_block.input

                    tool_calls_made.append(
                        {"tool": tool_name, "input": tool_input}
                    )

                    if self.verbose:
                        console.print(
                            f"\n[yellow]⚡ Executing:[/yellow] [bold]{tool_name}[/bold]"
                        )
                        console.print(
                            Syntax(
                                json.dumps(tool_input, indent=2),
                                "json",
                                theme="monokai",
                                line_numbers=False,
                            )
                        )

                    # Execute the tool via MCP
                    result = await self.session.call_tool(tool_name, tool_input)
                    tool_result_text = (
                        result.content[0].text if result.content else ""
                    )
                    raw_results.append(tool_result_text)

                    if self.verbose and tool_result_text:
                        # Truncate long results for display
                        display_result = tool_result_text[:500]
                        if len(tool_result_text) > 500:
                            display_result += "..."
                        console.print(f"[green]Result:[/green] {display_result}\n")

                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": tool_use_block.id,
                            "content": tool_result_text,
                        }
                    )

                # Add all tool results
                messages.append({"role": "user", "content": tool_results})

                # Continue the conversation
                response = self.anthropic_client.messages.create(
                    model=self.model,
                    max_tokens=4096,
                    system=system_prompt or default_system,
                    tools=self.tools,
                    messages=messages,
                )

            # Extract final text response
            final_response = ""
            for block in response.content:
                if hasattr(block, "text"):
                    final_response += block.text

            if self.verbose:
                console.print(
                    Panel(
                        final_response,
                        title="[bold green]Response[/bold green]",
                        border_style="green",
                    )
                )

            return {
                "response": final_response,
                "tool_calls": tool_calls_made,
                "raw_results": raw_results,
            }

        except Exception as e:
            raise MCPQueryError(f"Query execution failed: {e}") from e

    async def aggregate(
        self,
        database: str,
        collection: str,
        pipeline: list[dict[str, Any]],
    ) -> str:
        """
        Execute a MongoDB aggregation pipeline directly.

        Args:
            database: Database name
            collection: Collection name
            pipeline: Aggregation pipeline stages

        Returns:
            Raw result string from MongoDB
        """
        if not self.session:
            raise MCPConnectionError("Not connected. Call connect() first.")

        result = await self.session.call_tool(
            "aggregate",
            {
                "database": database,
                "collection": collection,
                "pipeline": pipeline,
            },
        )
        return result.content[0].text if result.content else ""

    async def find(
        self,
        database: str,
        collection: str,
        filter: Optional[dict[str, Any]] = None,
        projection: Optional[dict[str, Any]] = None,
        sort: Optional[dict[str, int]] = None,
        limit: int = 10,
    ) -> str:
        """
        Execute a MongoDB find query directly.

        Args:
            database: Database name
            collection: Collection name
            filter: Query filter
            projection: Fields to include/exclude
            sort: Sort specification
            limit: Maximum documents to return

        Returns:
            Raw result string from MongoDB
        """
        if not self.session:
            raise MCPConnectionError("Not connected. Call connect() first.")

        query_params: dict[str, Any] = {
            "database": database,
            "collection": collection,
            "limit": limit,
        }
        if filter:
            query_params["filter"] = filter
        if projection:
            query_params["projection"] = projection
        if sort:
            query_params["sort"] = sort

        result = await self.session.call_tool("find", query_params)
        return result.content[0].text if result.content else ""

    async def count(
        self,
        database: str,
        collection: str,
        query: Optional[dict[str, Any]] = None,
    ) -> str:
        """
        Count documents in a collection.

        Args:
            database: Database name
            collection: Collection name
            query: Optional filter query

        Returns:
            Count result string
        """
        if not self.session:
            raise MCPConnectionError("Not connected. Call connect() first.")

        params: dict[str, Any] = {
            "database": database,
            "collection": collection,
        }
        if query:
            params["query"] = query

        result = await self.session.call_tool("count", params)
        return result.content[0].text if result.content else ""

    async def list_databases(self) -> str:
        """List all databases in the MongoDB cluster."""
        if not self.session:
            raise MCPConnectionError("Not connected. Call connect() first.")

        result = await self.session.call_tool("list-databases", {})
        return result.content[0].text if result.content else ""

    async def list_collections(self, database: str) -> str:
        """List all collections in a database."""
        if not self.session:
            raise MCPConnectionError("Not connected. Call connect() first.")

        result = await self.session.call_tool(
            "list-collections", {"database": database}
        )
        return result.content[0].text if result.content else ""

    async def get_schema(self, database: str, collection: str) -> str:
        """Get the inferred schema for a collection."""
        if not self.session:
            raise MCPConnectionError("Not connected. Call connect() first.")

        result = await self.session.call_tool(
            "collection-schema",
            {"database": database, "collection": collection},
        )
        return result.content[0].text if result.content else ""

