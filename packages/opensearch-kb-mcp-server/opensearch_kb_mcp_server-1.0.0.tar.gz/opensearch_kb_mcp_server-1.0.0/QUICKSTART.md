# MCP Server Quick Start

## For End Users

### Step 1: Get Your API Credentials

Contact your OpenSearch KB administrator to get:
- API URL (e.g., `https://xxx.execute-api.us-east-1.amazonaws.com`)
- API Token

### Step 2: Configure Your AI Agent

#### Claude Desktop

1. Open Claude Desktop settings
2. Find the MCP configuration file:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

3. Add this configuration:

```json
{
  "mcpServers": {
    "opensearch-kb": {
      "command": "uvx",
      "args": ["opensearch-knowledge-base-mcp-server"],
      "env": {
        "OPENSEARCH_KB_API_URL": "https://your-api-url",
        "OPENSEARCH_KB_API_TOKEN": "your-token"
      }
    }
  }
}
```

4. Restart Claude Desktop

#### Cline (VS Code)

1. Open VS Code
2. Go to Cline settings
3. Add the same MCP configuration as above
4. Restart VS Code

#### Kiro IDE

1. Create `.kiro/settings/mcp.json` in your workspace
2. Add the configuration
3. Restart Kiro

### Step 3: Use It!

That's it! The AI agent will automatically:
- Download the MCP server (first time only)
- Start it when needed
- Use it to search OpenSearch knowledge

**Example conversation:**

```
You: Can you search the OpenSearch knowledge base for indexing best practices?

Claude: I'll search for that information.
[Automatically uses the search_opensearch_knowledge tool]

Here are the OpenSearch indexing best practices:
1. Use bulk API for batch indexing...
2. Configure appropriate refresh intervals...
[...]
```

## For Administrators

### Step 1: Deploy the API

Follow the [Deployment Guide](../docs/DEPLOYMENT_GUIDE_AGENTCORE.md) to deploy:
1. AgentCore Runtime with Strands Agent
2. API Gateway with Lambda Authorizer
3. DynamoDB for tokens and statistics

### Step 2: Create API Tokens

```bash
# Create a token for MCP server users
curl -X POST "$API_URL/admin/tokens" \
  -H "X-Admin-API-Key: $ADMIN_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "mcp-users-token",
    "description": "Token for MCP server integration",
    "expires_days": 365
  }'
```

### Step 3: Distribute Credentials

Share with your users:
- API URL: `$API_URL`
- API Token: (from the response above)
- Configuration instructions (Step 2 above)

### Step 4: Monitor Usage

```bash
# View API statistics
curl -X GET "$API_URL/admin/statistics" \
  -H "X-Admin-API-Key: $ADMIN_API_KEY"

# View recent API calls
curl -X GET "$API_URL/admin/calls?limit=100" \
  -H "X-Admin-API-Key: $ADMIN_API_KEY"
```

## For Developers

### Local Development

```bash
# Clone repository
git clone <your-repo>
cd mcp-server

# Install in development mode
pip install -e .

# Set environment variables
export OPENSEARCH_KB_API_URL="https://your-api-url"
export OPENSEARCH_KB_API_TOKEN="your-token"

# Test the server
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | \
  opensearch-knowledge-base-mcp-server
```

### Publishing to PyPI

```bash
# Install build tools
pip install build twine

# Test the package
./test_package.sh

# Publish to PyPI
./publish.sh
```

See [PUBLISHING.md](PUBLISHING.md) for detailed instructions.

## Troubleshooting

### MCP Server Not Found

**Error**: `command not found: opensearch-knowledge-base-mcp-server`

**Solution**: 
- Make sure `uvx` is installed: `pip install uv`
- Check your AI agent configuration syntax
- Try restarting your AI agent

### Authentication Failed

**Error**: `API request failed with status 401`

**Solution**:
- Verify your API token is correct
- Check token hasn't expired
- Contact your administrator for a new token

### Connection Timeout

**Error**: `API request failed: timeout`

**Solution**:
- Check your internet connection
- Verify the API URL is correct
- Check if the API Gateway is running

### Tool Not Appearing

**Solution**:
1. Check MCP configuration syntax (valid JSON)
2. Restart your AI agent
3. Check AI agent logs for errors
4. Verify environment variables are set correctly

## FAQ

**Q: Do I need to install Python?**

A: No! `uvx` handles everything automatically. Just configure your AI agent.

**Q: Do I need to run the server manually?**

A: No! Your AI agent starts and stops the server automatically.

**Q: Can multiple AI agents use the same token?**

A: Yes, but consider creating separate tokens for better tracking.

**Q: How do I update to a new version?**

A: Just restart your AI agent. `uvx` will automatically use the latest version.

**Q: Is my API token secure?**

A: Yes, it's stored in your local AI agent configuration and never sent anywhere except your API Gateway.

**Q: Can I use this offline?**

A: No, it requires internet connection to reach your API Gateway.

## Support

- Documentation: [MCP Server Guide](../docs/MCP_SERVER_GUIDE.md)
- Issues: GitHub Issues
- API Status: Check with your administrator

## Next Steps

- [Full MCP Server Guide](../docs/MCP_SERVER_GUIDE.md)
- [Deployment Guide](../docs/DEPLOYMENT_GUIDE_AGENTCORE.md)
- [API Documentation](../docs/API_DOCUMENTATION.md)
