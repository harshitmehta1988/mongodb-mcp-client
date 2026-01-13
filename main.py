#!/usr/bin/env python3
"""
MongoDB MCP Client - Main Entry Point

Run natural language queries against MongoDB using Claude AI.

Usage:
    python main.py                    # Start interactive shell
    python main.py "your query here"  # Run a single query
    python main.py --help             # Show help
"""

import argparse
import asyncio
import sys

from dotenv import load_dotenv
from rich.console import Console

from src import MongoDBMCPClient, MCPConnectionError, MCPQueryError

# Load environment variables
load_dotenv()

console = Console()


async def run_single_query(query: str, verbose: bool = True):
    """Execute a single query and exit."""
    try:
        async with MongoDBMCPClient(verbose=verbose) as client:
            result = await client.query(query)
            if not verbose:
                print(result["response"])
            return 0
    except (MCPConnectionError, MCPQueryError) as e:
        console.print(f"[red]Error:[/red] {e}")
        return 1


async def run_interactive():
    """Run the interactive shell."""
    from examples.interactive_shell import interactive_shell
    await interactive_shell()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="MongoDB MCP Client - Natural language queries for MongoDB",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py
      Start the interactive query shell
      
  python main.py "How many movies are in sample_mflix?"
      Run a single query
      
  python main.py --quiet "Count all users"
      Run a query with minimal output
      
  python main.py --example basic
      Run the basic example
        """,
    )
    
    parser.add_argument(
        "query",
        nargs="?",
        help="Query to execute (starts interactive mode if not provided)",
    )
    
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Minimal output (only show final response)",
    )
    
    parser.add_argument(
        "--example", "-e",
        choices=["basic", "direct", "infrastructure"],
        help="Run an example script",
    )
    
    args = parser.parse_args()
    
    # Run example if specified
    if args.example:
        if args.example == "basic":
            from examples.basic_query import main as example_main
        elif args.example == "direct":
            from examples.direct_operations import main as example_main
        elif args.example == "infrastructure":
            from examples.infrastructure_analysis import main as example_main
        
        asyncio.run(example_main())
        return 0
    
    # Run single query or interactive mode
    if args.query:
        return asyncio.run(run_single_query(args.query, verbose=not args.quiet))
    else:
        asyncio.run(run_interactive())
        return 0


if __name__ == "__main__":
    sys.exit(main())

