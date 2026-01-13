#!/usr/bin/env python3
"""
Infrastructure Knowledge Graph Example.

This example demonstrates querying the infrastructure_kg database
to analyze server dependencies and relationships.
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
    """Analyze infrastructure dependencies."""
    
    async with MongoDBMCPClient(verbose=True) as client:
        
        # Query 1: Find all entities
        print("\n" + "=" * 60)
        print("Query 1: What entities exist in the infrastructure?")
        print("=" * 60)
        
        await client.query(
            "What types of entities exist in infrastructure_kg and how many of each?"
        )
        
        # Query 2: Server dependencies
        print("\n" + "=" * 60)
        print("Query 2: Server dependency analysis")
        print("=" * 60)
        
        await client.query(
            "Find all upstream and downstream dependencies for SRV-APP-004 "
            "in the infrastructure_kg database. Show the complete dependency chain."
        )
        
        # Query 3: Critical paths
        print("\n" + "=" * 60)
        print("Query 3: Critical application dependencies")
        print("=" * 60)
        
        await client.query(
            "Which applications have the most dependencies in infrastructure_kg? "
            "List the top 5 and their dependency counts."
        )
        
        # Query 4: Network analysis
        print("\n" + "=" * 60)
        print("Query 4: VLAN membership")
        print("=" * 60)
        
        await client.query(
            "Show which servers belong to which VLANs in infrastructure_kg."
        )


if __name__ == "__main__":
    asyncio.run(main())

