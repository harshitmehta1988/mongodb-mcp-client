#!/usr/bin/env python3
"""
Direct Operations Example - Execute MongoDB operations programmatically.

This example shows how to use the client's direct methods to
execute MongoDB operations without using natural language.
"""

import asyncio
import json
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from src import MongoDBMCPClient

# Load environment variables
load_dotenv()

console = Console()


def print_result(title: str, result: str):
    """Pretty print a result."""
    console.print(Panel(title, style="bold blue"))
    try:
        # Try to parse and format as JSON
        # Extract JSON from result if it contains extra text
        if "[" in result or "{" in result:
            start = result.find("[") if "[" in result else result.find("{")
            end = result.rfind("]") + 1 if "]" in result else result.rfind("}") + 1
            json_str = result[start:end]
            data = json.loads(json_str)
            formatted = json.dumps(data, indent=2)
            console.print(Syntax(formatted, "json", theme="monokai"))
        else:
            console.print(result)
    except (json.JSONDecodeError, ValueError):
        console.print(result)
    console.print()


async def main():
    """Demonstrate direct MongoDB operations."""
    
    async with MongoDBMCPClient(verbose=False) as client:
        
        # List databases
        console.print("\n[bold cyan]Direct MongoDB Operations Demo[/bold cyan]\n")
        
        result = await client.list_databases()
        print_result("1. List Databases", result)
        
        # List collections
        result = await client.list_collections("sample_mflix")
        print_result("2. Collections in sample_mflix", result)
        
        # Count documents
        result = await client.count("sample_mflix", "movies")
        print_result("3. Movie Count", result)
        
        # Count with filter
        result = await client.count(
            "sample_mflix",
            "movies",
            query={"year": {"$gte": 2000}}
        )
        print_result("4. Movies from 2000+", result)
        
        # Find documents
        result = await client.find(
            database="sample_mflix",
            collection="movies",
            filter={"year": 2020},
            projection={"title": 1, "year": 1, "imdb.rating": 1},
            sort={"imdb.rating": -1},
            limit=5
        )
        print_result("5. Top 5 Movies from 2020", result)
        
        # Aggregation pipeline
        result = await client.aggregate(
            database="sample_mflix",
            collection="movies",
            pipeline=[
                {"$match": {"imdb.rating": {"$exists": True}}},
                {"$group": {
                    "_id": "$year",
                    "avgRating": {"$avg": "$imdb.rating"},
                    "count": {"$sum": 1}
                }},
                {"$match": {"count": {"$gte": 50}}},
                {"$sort": {"avgRating": -1}},
                {"$limit": 10}
            ]
        )
        print_result("6. Top 10 Years by Average Rating (min 50 movies)", result)
        
        # Get schema
        result = await client.get_schema("sample_mflix", "movies")
        print_result("7. Movies Collection Schema", result[:2000] + "...")


if __name__ == "__main__":
    asyncio.run(main())

