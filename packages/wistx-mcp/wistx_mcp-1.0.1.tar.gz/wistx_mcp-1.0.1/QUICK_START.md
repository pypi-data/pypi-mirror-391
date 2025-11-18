# WISTX MCP Server - Quick Start Guide

Get WISTX MCP server running in Cursor, Claude Desktop, or Codex in 3 minutes!

## 🚀 Quick Setup (3 Steps)

### Step 1: Install Package

```bash
pipx install wistx-mcp
```

### Step 2: Get API Key

Visit [app.wistx.ai](https://app.wistx.ai) and get your API key.

### Step 3: Configure Your Editor

#### Cursor

**File**: `~/.cursor/mcp.json`

```json
{
  "mcpServers": {
    "wistx": {
      "command": "pipx",
      "args": ["run", "--no-cache", "wistx-mcp"],
      "env": {
        "WISTX_API_KEY": "YOUR_API_KEY",
        "WISTX_API_URL": "https://api.wistx.ai"
      }
    }
  }
}
```

#### Claude Desktop

**File**: `~/.config/claude-desktop/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "wistx": {
      "command": "pipx",
      "args": ["run", "--no-cache", "wistx-mcp"],
      "env": {
        "WISTX_API_KEY": "YOUR_API_KEY",
        "WISTX_API_URL": "https://api.wistx.ai"
      }
    }
  }
}
```

#### Windsurf / Codex

**File**: `~/.codeium/windsurf/mcp_config.json`

```json
{
  "mcpServers": {
    "wistx": {
      "command": "pipx",
      "args": ["run", "--no-cache", "wistx-mcp"],
      "env": {
        "WISTX_API_KEY": "YOUR_API_KEY",
        "WISTX_API_URL": "https://api.wistx.ai"
      }
    }
  }
}
```

**Replace `YOUR_API_KEY`** with your actual API key.

**For local development**: Change `WISTX_API_URL` to `http://localhost:8000` (make sure backend API is running locally).

Then **restart your editor**.

---

## ✅ Test It Works

After restarting, ask your coding agent:

- _"Get PCI-DSS compliance requirements for RDS"_
- _"What are the HIPAA requirements for S3?"_
- _"Research best practices for AWS cost optimization"_

---

## 📚 Full Documentation

- **Complete Setup Guide**: See `CURSOR_CLAUDE_CODEX_SETUP.md`
- **Installation Guide**: See `INSTALLATION_GUIDE.md`
- **Troubleshooting**: See `INSTALLATION_GUIDE.md#troubleshooting`

---

**That's it!** You're ready to use WISTX MCP server. 🎉

