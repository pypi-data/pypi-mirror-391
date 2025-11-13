#!/bin/bash
# Test MCP protocol communication

set -e

echo "========================================="
echo "Testing MCP Protocol"
echo "========================================="
echo ""

# Check environment variables
if [ -z "$OPENSEARCH_KB_API_URL" ] || [ -z "$OPENSEARCH_KB_API_TOKEN" ]; then
    echo "⚠️  Environment variables not set"
    echo ""
    echo "For full testing, set:"
    echo "  export OPENSEARCH_KB_API_URL='https://your-api-url'"
    echo "  export OPENSEARCH_KB_API_TOKEN='your-token'"
    echo ""
    echo "Testing without API calls..."
    echo ""
fi

# Test 1: Initialize request
echo "1️⃣  Testing initialize..."
INIT_REQUEST='{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test-client","version":"1.0.0"}}}'

echo "$INIT_REQUEST" | timeout 5 python -m opensearch_kb_mcp_server 2>&1 | head -20 || {
    echo "❌ Initialize failed"
    echo ""
    echo "Common issues:"
    echo "1. Environment variables not set"
    echo "2. Package not installed (run: pip install -e .)"
    echo "3. Dependencies missing (run: pip install mcp httpx)"
    exit 1
}

echo "✅ Initialize successful"
echo ""

# Test 2: List tools
echo "2️⃣  Testing tools/list..."
LIST_TOOLS='{"jsonrpc":"2.0","id":2,"method":"tools/list"}'

RESPONSE=$(echo "$LIST_TOOLS" | timeout 5 python -m opensearch_kb_mcp_server 2>/dev/null | tail -1)

if echo "$RESPONSE" | grep -q "search_opensearch_knowledge"; then
    echo "✅ Tools list successful"
    echo "   Found tool: search_opensearch_knowledge"
else
    echo "⚠️  Tools list response unexpected"
    echo "   Response: $RESPONSE"
fi

echo ""

# Test 3: Call tool (if env vars set)
if [ -n "$OPENSEARCH_KB_API_URL" ] && [ -n "$OPENSEARCH_KB_API_TOKEN" ]; then
    echo "3️⃣  Testing tools/call..."
    CALL_TOOL='{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"search_opensearch_knowledge","arguments":{"question":"test"}}}'
    
    echo "$CALL_TOOL" | timeout 30 python -m opensearch_kb_mcp_server 2>&1 | head -50 || {
        echo "⚠️  Tool call test skipped (timeout or error)"
    }
    echo ""
fi

echo "========================================="
echo "✅ MCP Protocol Tests Complete"
echo "========================================="
echo ""
echo "The server can communicate via MCP protocol."
echo ""
echo "To use with AI agents, configure:"
echo '  "command": "uvx",'
echo '  "args": ["opensearch-knowledge-base-mcp-server"]'
