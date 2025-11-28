# I Have Learned a Basic MCP Tool

*Published: November 28, 2025*

**Slug:** `i-have-learned-a-basic-mcp-tool`

---

I just built my first MCP server — and it feels like unlocking a superpower.

Imagine giving your AI assistant the ability to do *anything* you can code: calculate complex math, generate UUIDs, hash passwords, transform text, even remember things between conversations. That's exactly what the Model Context Protocol lets you do.

In this post, I'll walk you through how I built KensMCP, a custom tool server with 11 utilities that now live inside my Cursor editor. No more copy-pasting to external tools. No more context switching. Just ask, and it's done.

---

## What I Built: KensMCP

KensMCP is my custom MCP server — a Python-based toolkit that gives Cursor's AI assistant superpowers it doesn't have out of the box.

### The Tools

I started with the utilities I actually use every day:

| Tool | What It Does |
|------|--------------|
| **calculate** | Math with `sqrt`, `sin`, `cos`, `log`, and more |
| **text_transform** | Uppercase, lowercase, title case, slugify, reverse, word/char count |
| **system_info** | Current time, platform details, environment variables |
| **generate_uuid** | Create 1-10 random UUIDs instantly |
| **generate_hash** | MD5, SHA1, SHA256, SHA512 hashing |
| **json_format** | Pretty-print, minify, or validate JSON |
| **base64_convert** | Encode and decode Base64 strings |
| **note_create/read/list/delete** | Persistent notes that survive restarts |

### Why These Tools?

I used to bounce between terminals, websites, and scripts for these tasks:
- Stack Overflow for "python uuid generate"
- Random websites for Base64 encoding
- Opening a Python REPL just to test some math

Now? I just ask. "Generate 5 UUIDs." Done. "Slugify this title." Done. "Hash this string with SHA256." Done.

### The Architecture

The server is surprisingly simple:
- **~600 lines of Python** — that's it
- **MCP SDK** handles the protocol
- **stdio transport** connects to Cursor
- **JSON file** persists notes to disk

Each tool is defined with a JSON schema (so the AI knows what parameters to pass) and an async handler (that does the actual work).

### The Magic Moment

The first time I asked Cursor to "calculate pi times 5 squared" and watched it call MY server, return 78.54, and display it — that's when it clicked. I wasn't just using AI. I was *extending* it.

---

## Conclusion: Your AI, Your Rules

Building KensMCP taught me something important: **AI assistants aren't fixed products — they're platforms.**

The Model Context Protocol is like an API for your AI. Instead of waiting for OpenAI or Anthropic to add the feature you need, you build it yourself. In an afternoon. With Python you already know.

### What I Learned

1. **Start small.** My first tool was just a calculator. Then I kept adding.
2. **Build what you use.** Every tool in KensMCP solves a real annoyance I had.
3. **It's easier than it looks.** The MCP SDK handles the hard parts. You just write the logic.
4. **The compound effect is real.** 11 tools × every chat session = massive time saved.

### What's Next for Me

- Adding a `password_generate` tool for secure random passwords
- A `regex_test` tool to validate patterns without leaving Cursor
- Maybe packaging it up and sharing on GitHub

### Your Turn

If you're using Cursor (or Claude Desktop), you can build your own MCP server today. Start with one tool. Something simple. Something you actually need.

Then watch your AI do things it couldn't do yesterday.

---

**The code is ~600 lines of Python. The possibilities are infinite.**

🚀 Happy hacking.

---

*Want to see the full code? Check out [KensMCP on GitHub](#) (coming soon).*

*Have questions? Find me on Twitter/X: [@yourhandle](#)*

---

**Tags:** #mcp #cursor #ai #python #tools #tutorial

