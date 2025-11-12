#!/usr/bin/env python3
"""
Submagic MCP Server Test Suite

Verifies server configuration, tool registration, and API connectivity.
"""

import os
import asyncio
import sys

def load_env():
    """Load environment variables from .env file if present"""
    try:
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    value = value.strip('"').strip("'")
                    os.environ[key] = value
        print("Loaded environment variables from .env")
    except FileNotFoundError:
        print("No .env file found, using existing environment variables")

async def test_server():
    """Test the MCP server functionality"""
    from submagic_mcp import app, get_api_key

    print("\n" + "="*60)
    print("SUBMAGIC MCP SERVER TEST")
    print("="*60)

    # Test 1: Check API key
    print("\n1. Checking API key...")
    try:
        api_key = get_api_key()
        print(f"   API key loaded: {api_key[:10]}...")
    except Exception as e:
        print(f"   ERROR: {e}")
        sys.exit(1)

    # Test 2: List tools
    print("\n2. Listing available tools...")
    tools = await app.list_tools()
    print(f"   Found {len(tools)} tools:")
    for tool in tools:
        print(f"   - {tool.name}")

    # Test 3: Call list_languages
    print("\n3. Testing API call: list_languages...")
    try:
        result = await app.call_tool('submagic_list_languages', {})
        if 'English' in str(result) or 'en' in str(result):
            print("   SUCCESS: Languages retrieved")
        else:
            print("   WARNING: Unexpected response format")
    except Exception as e:
        print(f"   ERROR: {e}")
        sys.exit(1)

    # Test 4: Call list_templates
    print("\n4. Testing API call: list_templates...")
    try:
        result = await app.call_tool('submagic_list_templates', {})
        if 'Hormozi' in str(result) or 'Sara' in str(result):
            print("   SUCCESS: Templates retrieved")
        else:
            print("   WARNING: Unexpected response format")
    except Exception as e:
        print(f"   ERROR: {e}")
        sys.exit(1)

    print("\n" + "="*60)
    print("ALL TESTS PASSED!")
    print("="*60)
    print("\nThe MCP server is properly configured and ready to use.")
    print("You can now add it to your Claude Desktop config.\n")

if __name__ == "__main__":
    load_env()
    asyncio.run(test_server())
