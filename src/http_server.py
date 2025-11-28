"""
KensMCP - HTTP/SSE Server Transport

This module provides an HTTP server that exposes the MCP protocol
over Server-Sent Events (SSE) for remote access.

Usage:
    python -m src.http_server --port 8080
"""

import asyncio
import json
import logging
import argparse
from aiohttp import web
from aiohttp_sse import sse_response
from typing import Optional
import uuid

from mcp.server import Server
from mcp.types import JSONRPCMessage

# Import our server configuration
from .server import server, list_tools, call_tool, list_resources, read_resource

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("kensmcp.http")


class HTTPServerTransport:
    """HTTP/SSE Transport for MCP Server."""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8080):
        self.host = host
        self.port = port
        self.app = web.Application()
        self.sessions: dict[str, asyncio.Queue] = {}
        self._setup_routes()
    
    def _setup_routes(self):
        """Set up HTTP routes."""
        self.app.router.add_get("/", self._handle_index)
        self.app.router.add_get("/health", self._handle_health)
        self.app.router.add_get("/sse", self._handle_sse)
        self.app.router.add_post("/message", self._handle_message)
        self.app.router.add_get("/tools", self._handle_list_tools)
        self.app.router.add_post("/tools/{tool_name}", self._handle_call_tool)
        self.app.router.add_get("/resources", self._handle_list_resources)
        self.app.router.add_get("/resources/{resource_name}", self._handle_read_resource)
    
    async def _handle_index(self, request: web.Request) -> web.Response:
        """Serve a simple HTML page with API documentation."""
        html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KensMCP Server</title>
    <style>
        :root {
            --bg: #0a0a0f;
            --surface: #12121a;
            --border: #2a2a3a;
            --text: #e4e4ef;
            --text-dim: #8888a0;
            --accent: #6366f1;
            --accent-dim: #4f46e5;
            --success: #22c55e;
            --code-bg: #1a1a24;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'SF Mono', 'Fira Code', 'JetBrains Mono', monospace;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
            min-height: 100vh;
            padding: 2rem;
        }
        .container { max-width: 900px; margin: 0 auto; }
        h1 {
            font-size: 2.5rem;
            background: linear-gradient(135deg, var(--accent) 0%, #a855f7 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }
        .subtitle { color: var(--text-dim); margin-bottom: 2rem; }
        .status {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.5rem 1rem;
            background: var(--surface);
            border: 1px solid var(--success);
            border-radius: 2rem;
            margin-bottom: 2rem;
        }
        .status-dot {
            width: 8px;
            height: 8px;
            background: var(--success);
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        .section {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }
        h2 {
            font-size: 1.25rem;
            color: var(--accent);
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        .endpoint {
            background: var(--code-bg);
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 0.75rem;
            border-left: 3px solid var(--accent);
        }
        .method {
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: bold;
            margin-right: 0.5rem;
        }
        .method-get { background: #22c55e22; color: #22c55e; }
        .method-post { background: #3b82f622; color: #3b82f6; }
        .path { color: var(--text); }
        .desc { color: var(--text-dim); font-size: 0.875rem; margin-top: 0.5rem; }
        .tools-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 0.75rem;
        }
        .tool {
            background: var(--code-bg);
            padding: 0.75rem;
            border-radius: 8px;
            font-size: 0.875rem;
        }
        .tool-name { color: var(--accent); font-weight: bold; }
        code {
            background: var(--code-bg);
            padding: 0.2rem 0.4rem;
            border-radius: 4px;
            font-size: 0.875rem;
        }
        pre {
            background: var(--code-bg);
            padding: 1rem;
            border-radius: 8px;
            overflow-x: auto;
            font-size: 0.875rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>⚡ KensMCP</h1>
        <p class="subtitle">Model Context Protocol Server v0.1.0</p>
        
        <div class="status">
            <span class="status-dot"></span>
            <span>Server Running</span>
        </div>
        
        <div class="section">
            <h2>🔌 API Endpoints</h2>
            <div class="endpoint">
                <span class="method method-get">GET</span>
                <span class="path">/health</span>
                <p class="desc">Health check endpoint</p>
            </div>
            <div class="endpoint">
                <span class="method method-get">GET</span>
                <span class="path">/tools</span>
                <p class="desc">List all available tools</p>
            </div>
            <div class="endpoint">
                <span class="method method-post">POST</span>
                <span class="path">/tools/{tool_name}</span>
                <p class="desc">Execute a tool with JSON body arguments</p>
            </div>
            <div class="endpoint">
                <span class="method method-get">GET</span>
                <span class="path">/resources</span>
                <p class="desc">List all available resources</p>
            </div>
            <div class="endpoint">
                <span class="method method-get">GET</span>
                <span class="path">/sse</span>
                <p class="desc">Server-Sent Events stream for MCP protocol</p>
            </div>
        </div>
        
        <div class="section">
            <h2>🛠️ Available Tools</h2>
            <div class="tools-grid">
                <div class="tool"><span class="tool-name">calculate</span><br/>Math operations</div>
                <div class="tool"><span class="tool-name">text_transform</span><br/>Text utilities</div>
                <div class="tool"><span class="tool-name">system_info</span><br/>System details</div>
                <div class="tool"><span class="tool-name">note_create</span><br/>Create notes</div>
                <div class="tool"><span class="tool-name">note_list</span><br/>List notes</div>
                <div class="tool"><span class="tool-name">note_read</span><br/>Read notes</div>
                <div class="tool"><span class="tool-name">note_delete</span><br/>Delete notes</div>
                <div class="tool"><span class="tool-name">generate_hash</span><br/>Hash generator</div>
                <div class="tool"><span class="tool-name">generate_uuid</span><br/>UUID generator</div>
                <div class="tool"><span class="tool-name">json_format</span><br/>JSON formatter</div>
                <div class="tool"><span class="tool-name">base64_convert</span><br/>Base64 encode/decode</div>
            </div>
        </div>
        
        <div class="section">
            <h2>📖 Example Usage</h2>
            <pre>
# Calculate
curl -X POST http://localhost:8080/tools/calculate \\
  -H "Content-Type: application/json" \\
  -d '{"expression": "sqrt(144) + 10"}'

# Generate UUID
curl -X POST http://localhost:8080/tools/generate_uuid \\
  -H "Content-Type: application/json" \\
  -d '{"count": 3}'

# Create a note
curl -X POST http://localhost:8080/tools/note_create \\
  -H "Content-Type: application/json" \\
  -d '{"title": "My Note", "content": "Hello World!"}'
            </pre>
        </div>
    </div>
</body>
</html>
        """
        return web.Response(text=html, content_type="text/html")
    
    async def _handle_health(self, request: web.Request) -> web.Response:
        """Health check endpoint."""
        return web.json_response({
            "status": "healthy",
            "server": "KensMCP",
            "version": "0.1.0"
        })
    
    async def _handle_sse(self, request: web.Request) -> web.StreamResponse:
        """Handle SSE connections for MCP protocol."""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = asyncio.Queue()
        
        logger.info(f"New SSE connection: {session_id}")
        
        async with sse_response(request) as resp:
            # Send session ID
            await resp.send(json.dumps({"type": "session", "id": session_id}))
            
            try:
                while True:
                    try:
                        message = await asyncio.wait_for(
                            self.sessions[session_id].get(),
                            timeout=30.0
                        )
                        await resp.send(json.dumps(message))
                    except asyncio.TimeoutError:
                        # Send keepalive
                        await resp.send(json.dumps({"type": "ping"}))
            finally:
                del self.sessions[session_id]
                logger.info(f"SSE connection closed: {session_id}")
        
        return resp
    
    async def _handle_message(self, request: web.Request) -> web.Response:
        """Handle incoming MCP messages."""
        try:
            data = await request.json()
            session_id = request.headers.get("X-Session-ID")
            
            if session_id and session_id in self.sessions:
                await self.sessions[session_id].put(data)
            
            return web.json_response({"status": "received"})
        except Exception as e:
            return web.json_response({"error": str(e)}, status=400)
    
    async def _handle_list_tools(self, request: web.Request) -> web.Response:
        """List all available tools (REST endpoint)."""
        tools = await list_tools()
        return web.json_response({
            "tools": [
                {
                    "name": t.name,
                    "description": t.description,
                    "parameters": t.inputSchema
                }
                for t in tools
            ]
        })
    
    async def _handle_call_tool(self, request: web.Request) -> web.Response:
        """Call a specific tool (REST endpoint)."""
        tool_name = request.match_info["tool_name"]
        
        try:
            body = await request.json()
        except:
            body = {}
        
        try:
            result = await call_tool(tool_name, body)
            return web.json_response({
                "success": True,
                "result": [{"type": r.type, "text": r.text} for r in result]
            })
        except Exception as e:
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=400)
    
    async def _handle_list_resources(self, request: web.Request) -> web.Response:
        """List all available resources."""
        resources = await list_resources()
        return web.json_response({
            "resources": [
                {
                    "uri": r.uri,
                    "name": r.name,
                    "description": r.description,
                    "mimeType": r.mimeType
                }
                for r in resources
            ]
        })
    
    async def _handle_read_resource(self, request: web.Request) -> web.Response:
        """Read a specific resource."""
        resource_name = request.match_info["resource_name"]
        uri = f"kensmcp://{resource_name}"
        
        try:
            content = await read_resource(uri)
            return web.json_response({
                "uri": uri,
                "content": json.loads(content) if content else None
            })
        except Exception as e:
            return web.json_response({
                "error": str(e)
            }, status=404)
    
    async def start(self):
        """Start the HTTP server."""
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        
        logger.info(f"🚀 KensMCP HTTP Server running at http://{self.host}:{self.port}")
        logger.info(f"   📖 API Docs: http://localhost:{self.port}/")
        logger.info(f"   🔧 Tools: http://localhost:{self.port}/tools")
        logger.info(f"   💚 Health: http://localhost:{self.port}/health")
        
        # Keep running
        while True:
            await asyncio.sleep(3600)


def main():
    """Main entry point for HTTP server."""
    parser = argparse.ArgumentParser(description="KensMCP HTTP Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8080, help="Port to listen on")
    args = parser.parse_args()
    
    transport = HTTPServerTransport(host=args.host, port=args.port)
    asyncio.run(transport.start())


if __name__ == "__main__":
    main()

