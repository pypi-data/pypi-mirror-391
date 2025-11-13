# OpenSearch Knowledge Base MCP Server

Model Context Protocol (MCP) server that exposes the OpenSearch Knowledge Base API as a tool for AI agents.

## Features

- **MCP Tool**: `search_opensearch_knowledge` - Search OpenSearch best practices and documentation
- **Session Support**: Maintain conversation context across multiple queries
- **Source Citations**: Returns relevant sources with relevance scores
- **Easy Integration**: Works with any MCP-compatible AI agent (Claude Desktop, Cline, etc.)

## Installation

**Important**: You don't need to manually run the server! The AI agent will automatically start and manage the MCP server process when needed.

### For End Users (Recommended)

Simply configure your AI agent (see [Usage](#usage-with-claude-desktop) below). The agent will automatically:
1. Download and install the package via `uvx`
2. Start the server when needed
3. Stop the server when done

No manual installation or server management required!

### For Development

```bash
# Clone the repository
git clone <your-repo>
cd mcp-server

# Install in development mode
pip install -e .

# Test the server
python test_simple.py

# The package is now available as a command
# (But you still don't need to run it manually - let your AI agent do it!)
```

## Configuration

The server requires two environment variables:

- `OPENSEARCH_KB_API_URL`: Your API Gateway URL (e.g., `https://xxx.execute-api.us-east-1.amazonaws.com`)
- `OPENSEARCH_KB_API_TOKEN`: Your API token (obtained from the Admin UI or API)

## Usage with Claude Desktop

Add to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "opensearch-knowledge-base": {
      "command": "uvx",
      "args": ["opensearch-knowledge-base-mcp-server"],
      "env": {
        "OPENSEARCH_KB_API_URL": "https://your-api-gateway-url",
        "OPENSEARCH_KB_API_TOKEN": "your-api-token"
      }
    }
  }
}
```

Or if installed locally:

```json
{
  "mcpServers": {
    "opensearch-knowledge-base": {
      "command": "python",
      "args": ["/path/to/mcp-server/server.py"],
      "env": {
        "OPENSEARCH_KB_API_URL": "https://your-api-gateway-url",
        "OPENSEARCH_KB_API_TOKEN": "your-api-token"
      }
    }
  }
}
```

## Usage with Cline (VS Code)

Add to your Cline MCP settings:

```json
{
  "mcpServers": {
    "opensearch-knowledge-base": {
      "command": "uvx",
      "args": ["opensearch-knowledge-base-mcp-server"],
      "env": {
        "OPENSEARCH_KB_API_URL": "https://your-api-gateway-url",
        "OPENSEARCH_KB_API_TOKEN": "your-api-token"
      }
    }
  }
}
```

## Usage with Kiro IDE

Add to your Kiro MCP configuration (`.kiro/settings/mcp.json`):

```json
{
  "mcpServers": {
    "opensearch-knowledge-base": {
      "command": "uvx",
      "args": ["opensearch-knowledge-base-mcp-server"],
      "env": {
        "OPENSEARCH_KB_API_URL": "https://your-api-gateway-url",
        "OPENSEARCH_KB_API_TOKEN": "your-api-token"
      },
      "disabled": false,
      "autoApprove": ["search_opensearch_knowledge"]
    }
  }
}
```

## Tool: search_opensearch_knowledge

Search the OpenSearch Knowledge Base for best practices, configuration guides, and troubleshooting information.

### Parameters

- `question` (required): Your question about OpenSearch
  - Example: "How to optimize OpenSearch indexing performance?"
  - Example: "What are the best practices for cluster sizing?"
  - Example: "How to troubleshoot slow queries?"

- `session_id` (optional): Session ID for conversation continuity
  - Use the same session_id across queries to maintain context
  - If not provided, each query is independent

### Example Usage

In Claude Desktop or any MCP-compatible client:

```
User: Use the search_opensearch_knowledge tool to find information about 
      optimizing OpenSearch indexing performance