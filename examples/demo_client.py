#!/usr/bin/env python3
"""
KensMCP Demo Client

This script demonstrates how to interact with the KensMCP HTTP server.
Run the server first: python -m src.http_server --port 8080
Then run this script: python examples/demo_client.py
"""

import asyncio
import aiohttp
import json

BASE_URL = "http://localhost:8080"


async def call_tool(session: aiohttp.ClientSession, tool_name: str, arguments: dict) -> dict:
    """Call a tool on the MCP server."""
    async with session.post(
        f"{BASE_URL}/tools/{tool_name}",
        json=arguments,
        headers={"Content-Type": "application/json"}
    ) as response:
        return await response.json()


async def main():
    """Run demo interactions with the MCP server."""
    
    print("=" * 60)
    print("⚡ KensMCP Demo Client")
    print("=" * 60)
    print()
    
    async with aiohttp.ClientSession() as session:
        
        # Check health
        print("🏥 Checking server health...")
        async with session.get(f"{BASE_URL}/health") as response:
            health = await response.json()
            print(f"   Status: {health['status']}")
            print(f"   Server: {health['server']} v{health['version']}")
        print()
        
        # List available tools
        print("🔧 Available Tools:")
        async with session.get(f"{BASE_URL}/tools") as response:
            tools_data = await response.json()
            for tool in tools_data["tools"]:
                print(f"   • {tool['name']}: {tool['description'][:50]}...")
        print()
        
        # Demo: Calculator
        print("🔢 Demo: Calculator")
        expressions = ["2 + 2", "sqrt(144)", "10 ** 3", "sin(3.14159 / 2)"]
        for expr in expressions:
            result = await call_tool(session, "calculate", {"expression": expr})
            if result["success"]:
                print(f"   {result['result'][0]['text']}")
        print()
        
        # Demo: Text Transform
        print("📝 Demo: Text Transform")
        text = "hello world from kensmcp"
        operations = ["uppercase", "titlecase", "slugify", "word_count"]
        for op in operations:
            result = await call_tool(session, "text_transform", {"text": text, "operation": op})
            if result["success"]:
                print(f"   {op}: {result['result'][0]['text']}")
        print()
        
        # Demo: System Info
        print("💻 Demo: System Info")
        result = await call_tool(session, "system_info", {"info_type": "time"})
        if result["success"]:
            print(f"   {result['result'][0]['text']}")
        print()
        
        # Demo: UUID Generator
        print("🆔 Demo: UUID Generator")
        result = await call_tool(session, "generate_uuid", {"count": 3})
        if result["success"]:
            print(f"   {result['result'][0]['text']}")
        print()
        
        # Demo: Hash Generator
        print("🔐 Demo: Hash Generator")
        result = await call_tool(session, "generate_hash", {"text": "KensMCP", "algorithm": "sha256"})
        if result["success"]:
            print(f"   {result['result'][0]['text']}")
        print()
        
        # Demo: Base64
        print("🔤 Demo: Base64")
        result = await call_tool(session, "base64_convert", {"text": "Hello KensMCP!", "operation": "encode"})
        if result["success"]:
            encoded = result['result'][0]['text']
            print(f"   {encoded}")
        print()
        
        # Demo: JSON Format
        print("📋 Demo: JSON Formatter")
        ugly_json = '{"name":"Ken","server":"MCP","tools":["calc","text","notes"]}'
        result = await call_tool(session, "json_format", {"json_string": ugly_json, "operation": "format"})
        if result["success"]:
            print(f"   {result['result'][0]['text']}")
        print()
        
        # Demo: Notes
        print("📒 Demo: Notes")
        
        # Create a note
        result = await call_tool(session, "note_create", {
            "title": "Demo Note",
            "content": "This is a demo note created by the KensMCP demo client!"
        })
        if result["success"]:
            print(f"   {result['result'][0]['text']}")
        
        # List notes
        result = await call_tool(session, "note_list", {})
        if result["success"]:
            print(f"   {result['result'][0]['text']}")
        
        # Read the note
        result = await call_tool(session, "note_read", {"title": "Demo Note"})
        if result["success"]:
            print(f"   {result['result'][0]['text']}")
        print()
        
        print("=" * 60)
        print("✅ Demo complete! All tools working correctly.")
        print("=" * 60)


if __name__ == "__main__":
    print()
    print("Make sure the server is running:")
    print("  python -m src.http_server --port 8080")
    print()
    
    try:
        asyncio.run(main())
    except aiohttp.ClientConnectorError:
        print("❌ Error: Could not connect to server.")
        print("   Make sure the server is running on http://localhost:8080")

