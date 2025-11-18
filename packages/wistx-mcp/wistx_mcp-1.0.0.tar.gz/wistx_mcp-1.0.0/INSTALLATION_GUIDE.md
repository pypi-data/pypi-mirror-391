# WISTX MCP Server Installation Guide

Following the [Nia MCP pattern](https://docs.trynia.ai/integrations/nia-mcp#cursor) for seamless integration.

## 📦 Installation

### Prerequisites

- Python 3.11+
- `pipx` (recommended) or `uvx` or `pip`
- Your WISTX API key from [app.wistx.ai](https://app.wistx.ai)

### Install the Package

**Option A: Using pipx** (Recommended)
```bash
pipx install wistx-mcp-server
```

**Option B: Using uvx**
```bash
uvx wistx-mcp-server
```

**Option C: Using pip**
```bash
pip install wistx-mcp-server
```

---

## ⚙️ Configuration for Your Coding Assistant

### Cursor

**1. Open MCP Configuration**

Open your Cursor MCP configuration file:
- **macOS**: `~/.cursor/mcp.json`
- **Windows**: `%APPDATA%\Cursor\mcp.json`
- **Linux**: `~/.config/cursor/mcp.json`

**2. Add WISTX Configuration**

**Option A: Using pipx** (Recommended)
```json
{
  "mcpServers": {
    "wistx": {
      "command": "pipx",
      "args": ["run", "--no-cache", "wistx-mcp-server"],
      "env": {
        "WISTX_API_KEY": "YOUR_API_KEY",
        "WISTX_API_URL": "https://api.wistx.ai"
      }
    }
  }
}
```

**Option B: Using uvx**
```json
{
  "mcpServers": {
    "wistx": {
      "command": "uvx",
      "args": ["wistx-mcp-server"],
      "env": {
        "WISTX_API_KEY": "YOUR_API_KEY",
        "WISTX_API_URL": "https://api.wistx.ai"
      }
    }
  }
}
```

**Option C: Using pip**
```json
{
  "mcpServers": {
    "wistx": {
      "command": "python",
      "args": ["-m", "wistx_mcp.server"],
      "env": {
        "WISTX_API_KEY": "YOUR_API_KEY",
        "WISTX_API_URL": "https://api.wistx.ai"
      }
    }
  }
}
```

**3. Replace Your API Key**

Get your API key from [app.wistx.ai](https://app.wistx.ai) and replace `YOUR_API_KEY` in the configuration.

**4. Restart Cursor**

Restart Cursor completely to load the new MCP server.

---

### Windsurf

**1. Open MCP Configuration**

Open: `~/.codeium/windsurf/mcp_config.json`

**2. Add WISTX Configuration**

```json
{
  "mcpServers": {
    "wistx": {
      "command": "pipx",
      "args": ["run", "--no-cache", "wistx-mcp-server"],
      "env": {
        "WISTX_API_KEY": "YOUR_API_KEY",
        "WISTX_API_URL": "https://api.wistx.ai"
      }
    }
  }
}
```

**3. Replace API Key and Restart**

---

### Claude Desktop

**1. Open Configuration**

Open: `~/.config/claude-desktop/claude_desktop_config.json`

**2. Add WISTX Configuration**

```json
{
  "mcpServers": {
    "wistx": {
      "command": "pipx",
      "args": ["run", "--no-cache", "wistx-mcp-server"],
      "env": {
        "WISTX_API_KEY": "YOUR_API_KEY",
        "WISTX_API_URL": "https://api.wistx.ai"
      }
    }
  }
}
```

**3. Replace API Key and Restart**

---

## 🚀 Try It Out!

After restarting your coding agent, you're good to go:

### 1. Get Compliance Requirements

Ask your coding agent:
- _"Get PCI-DSS compliance requirements for RDS"_
- _"What are the HIPAA requirements for S3?"_
- _"Show me NIST-800-53 controls for EC2"_

### 2. Research Knowledge Base

Try:
- _"Research best practices for AWS cost optimization"_
- _"Find DevOps patterns for Kubernetes deployments"_
- _"Search knowledge base for FinOps strategies"_

### 3. Check Your Usage

Visit [app.wistx.ai](https://app.wistx.ai) to:
- View API usage
- Manage API keys
- See indexed resources

---

## 🛠️ Available Tools

### Compliance Tools

- **`wistx_get_compliance_requirements`** - Get detailed compliance requirements for infrastructure resources
  - Supports: PCI-DSS, HIPAA, CIS, SOC2, NIST-800-53, ISO-27001, GDPR, FedRAMP
  - Resources: RDS, S3, EC2, Lambda, EKS, and more

### Knowledge Base Tools

- **`wistx_research_knowledge_base`** - Deep research across DevOps, infrastructure, compliance, FinOps domains
  - Semantic search across 10,000+ articles
  - Optional web search integration
  - Cross-domain insights

---

## 📋 Environment Variables

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `WISTX_API_KEY` | ✅ Yes | Your API key from app.wistx.ai | - |
| `WISTX_API_URL` | ⚠️ Optional | API base URL | `https://api.wistx.ai` |

---

## 🔧 Troubleshooting

### MCP Server Not Found

**Error**: `command not found: wistx-mcp-server`

**Solution**:
```bash
# Reinstall with pipx
pipx install --force wistx-mcp-server

# Or verify installation
pipx list | grep wistx
```

### API Key Invalid

**Error**: `401 Unauthorized`

**Solution**:
1. Verify API key at [app.wistx.ai](https://app.wistx.ai)
2. Check API key in configuration (no extra spaces)
3. Ensure `WISTX_API_URL` is correct

### Connection Error

**Error**: `Connection refused` or `Network error`

**Solution**:
1. Check `WISTX_API_URL` is correct (`https://api.wistx.ai`)
2. Verify internet connection
3. Check firewall/proxy settings

---

## 📚 Documentation

- **Full Documentation**: [docs.wistx.ai](https://docs.wistx.ai)
- **API Reference**: [docs.wistx.ai/api](https://docs.wistx.ai/api)
- **Support**: [app.wistx.ai/support](https://app.wistx.ai/support)

---

## 🎯 Next Steps

1. ✅ Install MCP server
2. ✅ Configure your coding assistant
3. ✅ Get API key from app.wistx.ai
4. ✅ Restart your coding assistant
5. ✅ Start using WISTX tools!

**Need Help?** Join our community or reach out through [app.wistx.ai](https://app.wistx.ai) for support.

