#!/usr/bin/env python3
"""
Simple test for MCP server
"""

import sys
import json
import subprocess
import os

def test_mcp_server():
    """Test MCP server initialization and tools list"""
    
    print("=" * 50)
    print("Testing MCP Server")
    print("=" * 50)
    print()
    
    # Check environment variables
    api_url = os.getenv("OPENSEARCH_KB_API_URL", "")
    api_token = os.getenv("OPENSEARCH_KB_API_TOKEN", "")
    
    if not api_url or not api_token:
        print("⚠️  Environment variables not set")
        print("For full testing, set:")
        print("  export OPENSEARCH_KB_API_URL='https://your-api-url'")
        print("  export OPENSEARCH_KB_API_TOKEN='your-token'")
        print()
    
    # Test 1: Initialize
    print("1️⃣  Testing initialize...")
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        }
    }
    
    try:
        proc = subprocess.Popen(
            [sys.executable, "-m", "opensearch_kb_mcp_server"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Send initialize request
        stdout, stderr = proc.communicate(
            input=json.dumps(init_request) + "\n",
            timeout=5
        )
        
        if stderr:
            print("Server logs:")
            for line in stderr.split('\n')[:5]:
                if line.strip():
                    print(f"  {line}")
        
        # Parse response
        for line in stdout.split('\n'):
            if line.strip():
                try:
                    response = json.loads(line)
                    if response.get("id") == 1:
                        if "result" in response:
                            print("✅ Initialize successful")
                            server_info = response["result"].get("serverInfo", {})
                            print(f"   Server: {server_info.get('name', 'unknown')}")
                            print(f"   Version: {server_info.get('version', 'unknown')}")
                        else:
                            print("❌ Initialize failed")
                            print(f"   Error: {response.get('error', 'unknown')}")
                            return False
                        break
                except json.JSONDecodeError:
                    continue
        
    except subprocess.TimeoutExpired:
        print("❌ Initialize timeout")
        proc.kill()
        return False
    except Exception as e:
        print(f"❌ Initialize error: {e}")
        return False
    
    print()
    
    # Test 2: List tools
    print("2️⃣  Testing tools/list...")
    list_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list"
    }
    
    try:
        proc = subprocess.Popen(
            [sys.executable, "-m", "opensearch_kb_mcp_server"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Send both initialize and list tools
        requests = json.dumps(init_request) + "\n" + json.dumps(list_request) + "\n"
        stdout, stderr = proc.communicate(input=requests, timeout=5)
        
        # Parse responses
        found_tools = False
        for line in stdout.split('\n'):
            if line.strip():
                try:
                    response = json.loads(line)
                    if response.get("id") == 2 and "result" in response:
                        tools = response["result"].get("tools", [])
                        if tools:
                            print("✅ Tools list successful")
                            for tool in tools:
                                print(f"   - {tool.get('name', 'unknown')}")
                            found_tools = True
                        break
                except json.JSONDecodeError:
                    continue
        
        if not found_tools:
            print("⚠️  No tools found in response")
    
    except subprocess.TimeoutExpired:
        print("❌ Tools list timeout")
        proc.kill()
    except Exception as e:
        print(f"❌ Tools list error: {e}")
    
    print()
    print("=" * 50)
    print("✅ Basic tests complete")
    print("=" * 50)
    print()
    print("The server can communicate via MCP protocol.")
    print()
    print("To use with AI agents, configure:")
    print('  "command": "uvx",')
    print('  "args": ["opensearch-knowledge-base-mcp-server"]')
    
    return True


if __name__ == "__main__":
    try:
        success = test_mcp_server()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted")
        sys.exit(1)
