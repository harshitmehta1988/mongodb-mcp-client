#!/usr/bin/env python3
"""
Basic Query Example - Demonstrates simple natural language queries.

This example shows how to use the MongoDB MCP Client to ask
questions about your data using natural language.
"""

import asyncio
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

from src import MongoDBMCPClient

# Load environment variables
load_dotenv()


async def main():
    """Run basic query examples."""
    
    # Initialize client using environment variable for connection string
    async with MongoDBMCPClient(verbose=True) as client:
        
        # Example 1: Simple count query
        print("\n" + "=" * 60)
        print("Example 1: Count documents")
        print("=" * 60)
        
        result = await client.query(
            "How many movies are in the sample_mflix database?"
        )
        
        # Example 2: Aggregation query
        print("\n" + "=" * 60)
        print("Example 2: Top genres")
        print("=" * 60)
        
        result = await client.query(
            "What are the top 5 most common genres in sample_mflix movies?"
        )
        
        # Example 3: Complex analysis
        print("\n" + "=" * 60)
        print("Example 3: Complex analysis")
        print("=" * 60)
        
        result = await client.query(
            "Find the average IMDB rating by decade for movies in sample_mflix. "
            "Only include decades with at least 100 movies."
        )


if __name__ == "__main__":
    asyncio.run(main())

