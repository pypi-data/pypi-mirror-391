# MCP Vector Search

Cloud-based vector code search MCP server for Kiro IDE.

## Installation

```bash
uvx mcp-vector-search
```

## Configuration

Add to your `~/.kiro/settings/mcp.json`:

```json
{
  "mcpServers": {
    "vector-search": {
      "command": "uvx",
      "args": ["mcp-vector-search"],
      "env": {
        "MCP_RENDER_URL": "https://your-app.onrender.com",
        "OPENROUTER_KEY": "your-openrouter-key",
        "SUPABASE_URL": "your-supabase-url",
        "SUPABASE_KEY": "your-supabase-key"
      }
    }
  }
}
```

## Features

- **Search**: Vector-based code search
- **Index**: Index project files
- **List Projects**: View all indexed projects

## Requirements

- Python 3.8+
- Render.com deployment
- Supabase database
- OpenRouter API key

## License

MIT
