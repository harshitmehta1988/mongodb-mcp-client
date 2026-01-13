#!/usr/bin/env python3
"""
Interactive Shell - Chat with your MongoDB database.

This example provides an interactive REPL for querying MongoDB
using natural language.
"""

import asyncio
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from src import MongoDBMCPClient, MCPConnectionError, MCPQueryError

# Load environment variables
load_dotenv()

console = Console()


async def interactive_shell():
    """Run an interactive query shell."""
    
    console.print(
        Panel(
            "[bold cyan]MongoDB Natural Language Query Shell[/bold cyan]\n\n"
            "Ask questions about your MongoDB data in plain English.\n"
            "Type [bold]'quit'[/bold] or [bold]'exit'[/bold] to leave.\n"
            "Type [bold]'help'[/bold] for example queries.",
            title="Welcome",
            border_style="cyan",
        )
    )
    
    try:
        async with MongoDBMCPClient(verbose=True) as client:
            
            while True:
                try:
                    # Get user input
                    console.print()
                    query = Prompt.ask("[bold cyan]You[/bold cyan]")
                    
                    # Handle special commands
                    if query.lower() in ("quit", "exit", "q"):
                        console.print("[yellow]Goodbye![/yellow]")
                        break
                    
                    if query.lower() == "help":
                        show_help()
                        continue
                    
                    if query.lower() == "databases":
                        result = await client.list_databases()
                        console.print(result)
                        continue
                    
                    if not query.strip():
                        continue
                    
                    # Execute the query
                    await client.query(query)
                    
                except MCPQueryError as e:
                    console.print(f"[red]Query Error:[/red] {e}")
                except KeyboardInterrupt:
                    console.print("\n[yellow]Use 'quit' to exit.[/yellow]")
                    
    except MCPConnectionError as e:
        console.print(f"[red]Connection Error:[/red] {e}")
        sys.exit(1)


def show_help():
    """Display help information."""
    console.print(
        Panel(
            "[bold]Example Queries:[/bold]\n\n"
            "• How many documents are in the movies collection?\n"
            "• What databases are available?\n"
            "• Show me the schema for sample_mflix.movies\n"
            "• What are the top 10 highest rated movies?\n"
            "• Find movies directed by Christopher Nolan\n"
            "• What's the average runtime by genre?\n"
            "• How many movies were released each year since 2000?\n\n"
            "[bold]Special Commands:[/bold]\n\n"
            "• [cyan]databases[/cyan] - List all databases\n"
            "• [cyan]help[/cyan] - Show this help\n"
            "• [cyan]quit[/cyan] - Exit the shell",
            title="Help",
            border_style="blue",
        )
    )


if __name__ == "__main__":
    asyncio.run(interactive_shell())

