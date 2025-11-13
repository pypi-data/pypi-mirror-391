#!/bin/bash
# Quick test for MCP server

echo "Testing MCP Server..."
echo ""

# Set dummy env vars if not set (for testing structure only)
export OPENSEARCH_KB_API_URL="${OPENSEARCH_KB_API_URL:-https://example.com}"
export OPENSEARCH_KB_API_TOKEN="${OPENSEARCH_KB_API_TOKEN:-dummy-token}"

# Run Python test
python3 test_simple.py
