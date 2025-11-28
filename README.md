# ⚡ KensMCP

A custom **Model Context Protocol (MCP)** server with useful utilities for AI assistants.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![License](https://img.shields.io/badge/License-MIT-green)
![MCP](https://img.shields.io/badge/MCP-1.0-purple)

## 🎯 What is this?

KensMCP is an MCP server that exposes tools an AI assistant can use to perform real actions:

- 🔢 **Calculator** - Mathematical operations
- 📝 **Text Transform** - Text manipulation utilities
- 💻 **System Info** - Platform and environment details
- 📒 **Notes** - Persistent note storage
- 🔐 **Hash Generator** - MD5, SHA1, SHA256, SHA512
- 🆔 **UUID Generator** - Generate random UUIDs
- 📋 **JSON Formatter** - Format, minify, validate JSON
- 🔤 **Base64** - Encode/decode Base64

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/KensMCP.git
cd KensMCP

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Server

#### Option 1: stdio transport (for Cursor/Claude Desktop)

```bash
python -m src.server
```

#### Option 2: HTTP Server (for remote access)

```bash
python -m src.http_server --port 8080
```

Then open http://localhost:8080 to see the API documentation.

## 🔧 Configuration

### For Cursor IDE

Add to `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "kensmcp": {
      "command": "python",
      "args": ["-m", "src.server"],
      "cwd": "/path/to/KensMCP"
    }
  }
}
```

### For Claude Desktop

Add to your Claude Desktop config:

```json
{
  "mcpServers": {
    "kensmcp": {
      "command": "python",
      "args": ["-m", "src.server"],
      "cwd": "/path/to/KensMCP"
    }
  }
}
```

## 📚 Available Tools

### `calculate`
Perform mathematical calculations.

```json
{
  "expression": "sqrt(144) + 10 ** 2"
}
```

### `text_transform`
Transform text with various operations.

```json
{
  "text": "Hello World",
  "operation": "uppercase"  // lowercase, titlecase, reverse, word_count, char_count, slugify
}
```

### `system_info`
Get system information.

```json
{
  "info_type": "all"  // time, platform, env, cwd, all
}
```

### `note_create` / `note_list` / `note_read` / `note_delete`
Manage persistent notes.

```json
{
  "title": "My Note",
  "content": "This is my note content"
}
```

### `generate_hash`
Generate hash of text.

```json
{
  "text": "Hello World",
  "algorithm": "sha256"  // md5, sha1, sha256, sha512
}
```

### `generate_uuid`
Generate random UUIDs.

```json
{
  "count": 5
}
```

### `json_format`
Format, minify, or validate JSON.

```json
{
  "json_string": "{\"key\":\"value\"}",
  "operation": "format"  // format, minify, validate
}
```

### `base64_convert`
Encode or decode Base64.

```json
{
  "text": "Hello World",
  "operation": "encode"  // encode, decode
}
```

## 🌐 HTTP API

When running in HTTP mode, the following endpoints are available:

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API documentation page |
| GET | `/health` | Health check |
| GET | `/tools` | List all tools |
| POST | `/tools/{name}` | Execute a tool |
| GET | `/resources` | List resources |
| GET | `/sse` | SSE stream for MCP |

### Example HTTP Requests

```bash
# List tools
curl http://localhost:8080/tools

# Calculate
curl -X POST http://localhost:8080/tools/calculate \
  -H "Content-Type: application/json" \
  -d '{"expression": "2 + 2"}'

# Generate UUID
curl -X POST http://localhost:8080/tools/generate_uuid \
  -H "Content-Type: application/json" \
  -d '{"count": 3}'
```

## 📁 Project Structure

```
KensMCP/
├── src/
│   ├── __init__.py
│   ├── server.py          # Main MCP server (stdio)
│   └── http_server.py     # HTTP/SSE server
├── examples/
│   ├── demo_client.py     # Demo client script
│   └── test_tools.sh      # Bash test script
├── data/
│   └── notes.json         # Persistent notes storage
├── pyproject.toml
├── requirements.txt
├── README.md
└── .gitignore
```

## 🧪 Testing

```bash
# Run the HTTP server
python -m src.http_server --port 8080

# In another terminal, run tests
./examples/test_tools.sh
```

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

Built with ❤️ using the [Model Context Protocol](https://github.com/anthropics/mcp)

