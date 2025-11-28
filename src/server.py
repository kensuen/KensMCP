"""
KensMCP - Main MCP Server with HTTP/SSE Transport

This server exposes useful tools that an AI assistant can use:
- Calculator operations
- Text manipulation utilities
- System information
- Note taking (persistent storage)
- Web fetching capabilities
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Any

from mcp.server import Server
from mcp.types import (
    Tool,
    TextContent,
    Resource,
    ResourceTemplate,
)


# Initialize the MCP Server
server = Server("KensMCP")

# In-memory storage for notes (persisted to file)
NOTES_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "notes.json")


def load_notes() -> dict:
    """Load notes from persistent storage."""
    try:
        if os.path.exists(NOTES_FILE):
            with open(NOTES_FILE, "r") as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def save_notes(notes: dict) -> None:
    """Save notes to persistent storage."""
    os.makedirs(os.path.dirname(NOTES_FILE), exist_ok=True)
    with open(NOTES_FILE, "w") as f:
        json.dump(notes, f, indent=2)


# ============================================================================
# TOOLS - Functions the AI can call
# ============================================================================

@server.list_tools()
async def list_tools() -> list[Tool]:
    """Return the list of available tools."""
    return [
        # Calculator Tool
        Tool(
            name="calculate",
            description="Perform mathematical calculations. Supports +, -, *, /, **, sqrt, sin, cos, tan, log, abs, round, floor, ceil.",
            inputSchema={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Mathematical expression to evaluate (e.g., '2 + 2', 'sqrt(16)', '10 ** 2')"
                    }
                },
                "required": ["expression"]
            }
        ),
        
        # Text Tools
        Tool(
            name="text_transform",
            description="Transform text: uppercase, lowercase, title case, reverse, count words/chars, or slugify.",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text to transform"
                    },
                    "operation": {
                        "type": "string",
                        "enum": ["uppercase", "lowercase", "titlecase", "reverse", "word_count", "char_count", "slugify"],
                        "description": "The transformation to apply"
                    }
                },
                "required": ["text", "operation"]
            }
        ),
        
        # System Info Tool
        Tool(
            name="system_info",
            description="Get system information: current time, platform, environment variables, or working directory.",
            inputSchema={
                "type": "object",
                "properties": {
                    "info_type": {
                        "type": "string",
                        "enum": ["time", "platform", "env", "cwd", "all"],
                        "description": "Type of system information to retrieve"
                    }
                },
                "required": ["info_type"]
            }
        ),
        
        # Notes Tool - Create
        Tool(
            name="note_create",
            description="Create a new note with a title and content. Notes are persisted to disk.",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Title of the note (used as identifier)"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content of the note"
                    }
                },
                "required": ["title", "content"]
            }
        ),
        
        # Notes Tool - List
        Tool(
            name="note_list",
            description="List all saved notes with their titles and creation dates.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        
        # Notes Tool - Read
        Tool(
            name="note_read",
            description="Read the content of a specific note by title.",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Title of the note to read"
                    }
                },
                "required": ["title"]
            }
        ),
        
        # Notes Tool - Delete
        Tool(
            name="note_delete",
            description="Delete a note by title.",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Title of the note to delete"
                    }
                },
                "required": ["title"]
            }
        ),
        
        # Hash Generator Tool
        Tool(
            name="generate_hash",
            description="Generate hash of text using MD5, SHA1, SHA256, or SHA512.",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to hash"
                    },
                    "algorithm": {
                        "type": "string",
                        "enum": ["md5", "sha1", "sha256", "sha512"],
                        "description": "Hash algorithm to use"
                    }
                },
                "required": ["text", "algorithm"]
            }
        ),
        
        # UUID Generator
        Tool(
            name="generate_uuid",
            description="Generate a random UUID (v4).",
            inputSchema={
                "type": "object",
                "properties": {
                    "count": {
                        "type": "integer",
                        "description": "Number of UUIDs to generate (default: 1, max: 10)",
                        "minimum": 1,
                        "maximum": 10
                    }
                },
                "required": []
            }
        ),
        
        # JSON Formatter
        Tool(
            name="json_format",
            description="Format, validate, or minify JSON data.",
            inputSchema={
                "type": "object",
                "properties": {
                    "json_string": {
                        "type": "string",
                        "description": "JSON string to process"
                    },
                    "operation": {
                        "type": "string",
                        "enum": ["format", "minify", "validate"],
                        "description": "Operation to perform"
                    }
                },
                "required": ["json_string", "operation"]
            }
        ),
        
        # Base64 Encoder/Decoder
        Tool(
            name="base64_convert",
            description="Encode or decode Base64 strings.",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to encode or Base64 string to decode"
                    },
                    "operation": {
                        "type": "string",
                        "enum": ["encode", "decode"],
                        "description": "Whether to encode or decode"
                    }
                },
                "required": ["text", "operation"]
            }
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool execution."""
    
    try:
        if name == "calculate":
            return await _handle_calculate(arguments)
        elif name == "text_transform":
            return await _handle_text_transform(arguments)
        elif name == "system_info":
            return await _handle_system_info(arguments)
        elif name == "note_create":
            return await _handle_note_create(arguments)
        elif name == "note_list":
            return await _handle_note_list(arguments)
        elif name == "note_read":
            return await _handle_note_read(arguments)
        elif name == "note_delete":
            return await _handle_note_delete(arguments)
        elif name == "generate_hash":
            return await _handle_generate_hash(arguments)
        elif name == "generate_uuid":
            return await _handle_generate_uuid(arguments)
        elif name == "json_format":
            return await _handle_json_format(arguments)
        elif name == "base64_convert":
            return await _handle_base64_convert(arguments)
        else:
            return [TextContent(type="text", text=f"❌ Unknown tool: {name}")]
    except Exception as e:
        return [TextContent(type="text", text=f"❌ Error executing {name}: {str(e)}")]


# ============================================================================
# TOOL HANDLERS
# ============================================================================

async def _handle_calculate(args: dict) -> list[TextContent]:
    """Handle calculator operations."""
    import math
    
    expression = args.get("expression", "")
    
    # Safe evaluation context
    safe_dict = {
        "abs": abs,
        "round": round,
        "min": min,
        "max": max,
        "sum": sum,
        "pow": pow,
        "sqrt": math.sqrt,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "log": math.log,
        "log10": math.log10,
        "log2": math.log2,
        "exp": math.exp,
        "floor": math.floor,
        "ceil": math.ceil,
        "pi": math.pi,
        "e": math.e,
    }
    
    try:
        # Clean the expression
        expr = expression.replace("^", "**")
        result = eval(expr, {"__builtins__": {}}, safe_dict)
        return [TextContent(type="text", text=f"🔢 {expression} = {result}")]
    except Exception as e:
        return [TextContent(type="text", text=f"❌ Invalid expression: {str(e)}")]


async def _handle_text_transform(args: dict) -> list[TextContent]:
    """Handle text transformation operations."""
    import re
    
    text = args.get("text", "")
    operation = args.get("operation", "")
    
    results = {
        "uppercase": text.upper(),
        "lowercase": text.lower(),
        "titlecase": text.title(),
        "reverse": text[::-1],
        "word_count": str(len(text.split())),
        "char_count": str(len(text)),
        "slugify": re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-'),
    }
    
    if operation in results:
        return [TextContent(type="text", text=f"📝 Result: {results[operation]}")]
    else:
        return [TextContent(type="text", text=f"❌ Unknown operation: {operation}")]


async def _handle_system_info(args: dict) -> list[TextContent]:
    """Handle system information requests."""
    import platform
    
    info_type = args.get("info_type", "all")
    
    info = {}
    
    if info_type in ("time", "all"):
        info["current_time"] = datetime.now().isoformat()
        info["timezone"] = datetime.now().astimezone().tzname()
    
    if info_type in ("platform", "all"):
        info["system"] = platform.system()
        info["release"] = platform.release()
        info["version"] = platform.version()
        info["machine"] = platform.machine()
        info["processor"] = platform.processor()
        info["python_version"] = platform.python_version()
    
    if info_type in ("cwd", "all"):
        info["working_directory"] = os.getcwd()
    
    if info_type in ("env", "all"):
        # Only show safe environment variables
        safe_vars = ["USER", "HOME", "SHELL", "LANG", "PATH"]
        info["environment"] = {k: os.environ.get(k, "N/A") for k in safe_vars}
    
    formatted = json.dumps(info, indent=2)
    return [TextContent(type="text", text=f"💻 System Information:\n```json\n{formatted}\n```")]


async def _handle_note_create(args: dict) -> list[TextContent]:
    """Create a new note."""
    title = args.get("title", "").strip()
    content = args.get("content", "")
    
    if not title:
        return [TextContent(type="text", text="❌ Note title is required")]
    
    notes = load_notes()
    notes[title] = {
        "content": content,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    save_notes(notes)
    
    return [TextContent(type="text", text=f"✅ Note '{title}' saved successfully!")]


async def _handle_note_list(args: dict) -> list[TextContent]:
    """List all notes."""
    notes = load_notes()
    
    if not notes:
        return [TextContent(type="text", text="📭 No notes found. Create one with note_create!")]
    
    lines = ["📒 **Your Notes:**\n"]
    for title, data in notes.items():
        created = data.get("created_at", "Unknown")[:10]
        preview = data.get("content", "")[:50]
        if len(data.get("content", "")) > 50:
            preview += "..."
        lines.append(f"• **{title}** (created: {created})\n  {preview}\n")
    
    return [TextContent(type="text", text="\n".join(lines))]


async def _handle_note_read(args: dict) -> list[TextContent]:
    """Read a specific note."""
    title = args.get("title", "").strip()
    notes = load_notes()
    
    if title not in notes:
        return [TextContent(type="text", text=f"❌ Note '{title}' not found")]
    
    note = notes[title]
    return [TextContent(type="text", text=f"📖 **{title}**\n\n{note['content']}\n\n_Created: {note['created_at']}_")]


async def _handle_note_delete(args: dict) -> list[TextContent]:
    """Delete a note."""
    title = args.get("title", "").strip()
    notes = load_notes()
    
    if title not in notes:
        return [TextContent(type="text", text=f"❌ Note '{title}' not found")]
    
    del notes[title]
    save_notes(notes)
    
    return [TextContent(type="text", text=f"🗑️ Note '{title}' deleted successfully!")]


async def _handle_generate_hash(args: dict) -> list[TextContent]:
    """Generate hash of text."""
    import hashlib
    
    text = args.get("text", "")
    algorithm = args.get("algorithm", "sha256")
    
    hash_funcs = {
        "md5": hashlib.md5,
        "sha1": hashlib.sha1,
        "sha256": hashlib.sha256,
        "sha512": hashlib.sha512,
    }
    
    if algorithm not in hash_funcs:
        return [TextContent(type="text", text=f"❌ Unknown algorithm: {algorithm}")]
    
    hash_result = hash_funcs[algorithm](text.encode()).hexdigest()
    return [TextContent(type="text", text=f"🔐 {algorithm.upper()}: `{hash_result}`")]


async def _handle_generate_uuid(args: dict) -> list[TextContent]:
    """Generate UUIDs."""
    import uuid
    
    count = min(args.get("count", 1), 10)
    uuids = [str(uuid.uuid4()) for _ in range(count)]
    
    if count == 1:
        return [TextContent(type="text", text=f"🆔 UUID: `{uuids[0]}`")]
    else:
        formatted = "\n".join([f"  {i+1}. `{u}`" for i, u in enumerate(uuids)])
        return [TextContent(type="text", text=f"🆔 Generated {count} UUIDs:\n{formatted}")]


async def _handle_json_format(args: dict) -> list[TextContent]:
    """Format, minify, or validate JSON."""
    json_string = args.get("json_string", "")
    operation = args.get("operation", "format")
    
    try:
        parsed = json.loads(json_string)
        
        if operation == "validate":
            return [TextContent(type="text", text="✅ Valid JSON!")]
        elif operation == "minify":
            result = json.dumps(parsed, separators=(",", ":"))
            return [TextContent(type="text", text=f"📦 Minified:\n`{result}`")]
        else:  # format
            result = json.dumps(parsed, indent=2)
            return [TextContent(type="text", text=f"📋 Formatted:\n```json\n{result}\n```")]
    except json.JSONDecodeError as e:
        return [TextContent(type="text", text=f"❌ Invalid JSON: {str(e)}")]


async def _handle_base64_convert(args: dict) -> list[TextContent]:
    """Encode or decode Base64."""
    import base64
    
    text = args.get("text", "")
    operation = args.get("operation", "encode")
    
    try:
        if operation == "encode":
            result = base64.b64encode(text.encode()).decode()
            return [TextContent(type="text", text=f"🔤 Encoded:\n`{result}`")]
        else:  # decode
            result = base64.b64decode(text.encode()).decode()
            return [TextContent(type="text", text=f"🔤 Decoded:\n`{result}`")]
    except Exception as e:
        return [TextContent(type="text", text=f"❌ Error: {str(e)}")]


# ============================================================================
# RESOURCES - Data the AI can read
# ============================================================================

@server.list_resources()
async def list_resources() -> list[Resource]:
    """List available resources."""
    return [
        Resource(
            uri="kensmcp://notes",
            name="All Notes",
            description="Access all saved notes",
            mimeType="application/json"
        ),
        Resource(
            uri="kensmcp://server-info",
            name="Server Information",
            description="Information about this MCP server",
            mimeType="application/json"
        )
    ]


@server.read_resource()
async def read_resource(uri: str) -> str:
    """Read a resource by URI."""
    if uri == "kensmcp://notes":
        return json.dumps(load_notes(), indent=2)
    elif uri == "kensmcp://server-info":
        return json.dumps({
            "name": "KensMCP",
            "version": "0.1.0",
            "author": "Ken",
            "description": "A custom MCP server with useful utilities",
            "tools_count": 10,
            "tools": [
                "calculate", "text_transform", "system_info",
                "note_create", "note_list", "note_read", "note_delete",
                "generate_hash", "generate_uuid", "json_format", "base64_convert"
            ]
        }, indent=2)
    else:
        raise ValueError(f"Unknown resource: {uri}")


# ============================================================================
# ENTRY POINTS
# ============================================================================

async def run_stdio():
    """Run the server using stdio transport (for Cursor/Claude Desktop)."""
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


def main():
    """Main entry point."""
    asyncio.run(run_stdio())


if __name__ == "__main__":
    main()

