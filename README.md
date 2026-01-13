# MongoDB MCP Client

A Python client for querying MongoDB using natural language through Claude AI and the Model Context Protocol (MCP).

## Features

- 🗣️ **Natural Language Queries**: Ask questions about your data in plain English
- 🤖 **Claude AI Integration**: Powered by Anthropic's Claude for intelligent query generation
- 🔧 **Direct Operations**: Execute MongoDB operations programmatically
- 🎨 **Rich Terminal UI**: Beautiful output with syntax highlighting
- 📊 **Multiple Examples**: Ready-to-run example scripts

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Your App       │────▶│   Claude AI     │────▶│  MongoDB MCP    │
│  (Prompt)       │◀────│                 │◀────│  Server         │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                       │
                                                       ▼
                                                ┌─────────────────┐
                                                │  MongoDB Atlas  │
                                                └─────────────────┘
```

## Prerequisites

- Python 3.10+
- Node.js 18+ (for MCP server)
- Anthropic API key
- MongoDB Atlas cluster (or local MongoDB)

## Installation

1. **Clone the repository**:
   ```bash
   cd mongodb-mcp-client
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your Anthropic API key:
   ```env
   ANTHROPIC_API_KEY=your-api-key-here
   MDB_MCP_CONNECTION_STRING=mongodb+srv://<admin>:<password>>@clustername.mongodb.net/
   ```

## Quick Start

### Interactive Shell

Start the interactive query shell:

```bash
python main.py
```

Then ask questions in natural language:

```
You: How many movies are in sample_mflix?
You: What are the top 5 genres?
You: Find movies directed by Christopher Nolan with rating above 8
```

### Single Query

Run a single query from the command line:

```bash
python main.py "How many documents are in sample_mflix.movies?"
```

### Programmatic Usage

```python
import asyncio
from src import MongoDBMCPClient

async def main():
    async with MongoDBMCPClient() as client:
        # Natural language query
        result = await client.query(
            "What are the top 10 highest rated movies?"
        )
        print(result["response"])
        
        # Direct aggregation
        result = await client.aggregate(
            database="sample_mflix",
            collection="movies",
            pipeline=[
                {"$group": {"_id": "$year", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 5}
            ]
        )
        print(result)

asyncio.run(main())
```

## Examples

Run the included examples:

```bash
# Basic natural language queries
python main.py --example basic

# Direct MongoDB operations (no AI)
python main.py --example direct

# Infrastructure knowledge graph analysis
python main.py --example infrastructure
```

Or run them directly:

```bash
python examples/basic_query.py
python examples/interactive_shell.py
python examples/direct_operations.py
python examples/infrastructure_analysis.py
```

## API Reference

### MongoDBMCPClient

The main client class for interacting with MongoDB via MCP.

#### Constructor

```python
MongoDBMCPClient(
    connection_string: str = None,  # MongoDB URI (uses env var if not provided)
    model: str = "claude-sonnet-4-20250514",  # Claude model to use
    verbose: bool = True  # Print detailed execution info
)
```

#### Methods

| Method | Description |
|--------|-------------|
| `connect()` | Connect to the MCP server |
| `close()` | Close all connections |
| `query(prompt)` | Execute a natural language query |
| `aggregate(db, collection, pipeline)` | Run an aggregation pipeline |
| `find(db, collection, filter, ...)` | Execute a find query |
| `count(db, collection, query)` | Count documents |
| `list_databases()` | List all databases |
| `list_collections(db)` | List collections in a database |
| `get_schema(db, collection)` | Get collection schema |

### Context Manager

The client supports async context managers for automatic cleanup:

```python
async with MongoDBMCPClient() as client:
    result = await client.query("Your question here")
# Connection automatically closed
```

## Project Structure

```
mongodb-mcp-client/
├── src/
│   ├── __init__.py       # Package exports
│   ├── client.py         # Main MCP client implementation
│   └── exceptions.py     # Custom exceptions
├── examples/
│   ├── basic_query.py    # Simple query examples
│   ├── interactive_shell.py  # Interactive REPL
│   ├── direct_operations.py  # Programmatic operations
│   └── infrastructure_analysis.py  # Knowledge graph example
├── main.py               # CLI entry point
├── requirements.txt      # Python dependencies
├── .env.example          # Environment template
└── README.md            # This file
```

## Example Queries

Here are some example natural language queries you can try:

```
# Basic queries
"How many movies are in sample_mflix?"
"What databases are available?"
"Show me the schema for sample_mflix.movies"

# Analytical queries
"What are the top 10 highest rated movies of all time?"
"Find the average IMDB rating by genre"
"Which directors have the most movies?"

# Complex queries
"Find all movies from 2012 with rating above 8, show title and cast"
"What's the trend in movie releases over the decades?"
"Which actors appear in the most highly-rated movies?"

# Infrastructure queries (infrastructure_kg database)
"What are the dependencies of SRV-APP-004?"
"Show all servers in VLAN-APP"
"Which applications have hard dependencies?"
```

## Troubleshooting

### Connection Issues

1. **Verify MongoDB connection string**: Ensure your connection string is correct and the cluster is accessible.

2. **Check Anthropic API key**: Make sure `ANTHROPIC_API_KEY` is set correctly.

3. **Node.js requirement**: The MCP server requires Node.js. Install it from [nodejs.org](https://nodejs.org/).

### Common Errors

| Error | Solution |
|-------|----------|
| `MCPConnectionError` | Check MongoDB connection string and network |
| `MCPQueryError` | Verify the query makes sense for your data |
| `ANTHROPIC_API_KEY not set` | Add your API key to `.env` file |

## License

MIT License - feel free to use this in your projects!

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

