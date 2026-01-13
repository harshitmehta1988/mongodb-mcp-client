"""MongoDB MCP Client - Natural language queries for MongoDB using Claude AI."""

from .client import MongoDBMCPClient
from .exceptions import MCPConnectionError, MCPQueryError

__version__ = "1.0.0"
__all__ = ["MongoDBMCPClient", "MCPConnectionError", "MCPQueryError"]

