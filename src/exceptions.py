"""Custom exceptions for MongoDB MCP Client."""


class MCPConnectionError(Exception):
    """Raised when connection to MCP server fails."""

    pass


class MCPQueryError(Exception):
    """Raised when a query execution fails."""

    pass

