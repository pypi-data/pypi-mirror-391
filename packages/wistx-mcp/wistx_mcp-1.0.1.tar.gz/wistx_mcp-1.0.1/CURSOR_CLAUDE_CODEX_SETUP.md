# WISTX MCP Server Setup Guide

Following the [Nia MCP pattern](https://docs.trynia.ai/integrations/nia-mcp#cursor) for seamless integration with Cursor, Claude Desktop, and Codex.

## 📦 Installation

### Prerequisites

- Python 3.11+
- `pipx` (recommended) or `uvx` or `pip`
- Your WISTX API key from [app.wistx.ai](https://app.wistx.ai)

### Install the Package

**Option A: Using pipx** (Recommended)
```bash
pipx install wistx-mcp
```

**Option B: Using uvx**
```bash
uvx wistx-mcp
```

**Option C: Using pip**
```bash
pip install wistx-mcp
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

**Option A: Using pipx** (Recommended, like [Nia](https://docs.trynia.ai/integrations/nia-mcp#cursor))
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

**Option B: Using uvx**
```json
{
  "mcpServers": {
    "wistx": {
      "command": "uvx",
      "args": ["wistx-mcp"],
      "env": {
        "WISTX_API_KEY": "YOUR_API_KEY",
        "WISTX_API_URL": "https://api.wistx.ai"
      }
    }
  }
}
```

**Option C: Using pip** (Direct command)
```json
{
  "mcpServers": {
    "wistx": {
      "command": "wistx-mcp",
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

### Claude Desktop

**1. Open MCP Configuration**

Open your Claude Desktop MCP configuration file:
- **macOS**: `~/.config/claude-desktop/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/claude-desktop/claude_desktop_config.json`

**2. Add WISTX Configuration**

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

**3. Replace API Key and Restart**

Get your API key from [app.wistx.ai](https://app.wistx.ai) and restart Claude Desktop.

---

### Windsurf / Codex

**1. Open MCP Configuration**

Open: `~/.codeium/windsurf/mcp_config.json`

**2. Add WISTX Configuration**

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

**3. Replace API Key and Restart**

---

### VS Code (Continue.dev)

**1. Open Continue Configuration**

Open: `~/.continue/config.json` (or your Continue config file)

**2. Add MCP Server Configuration**

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

**3. Replace API Key and Restart**

---

## 🚀 Try It Out!

After restarting your coding agent, you're good to go:

### 1. Get Compliance Requirements

Ask your coding agent:
- _"Get PCI-DSS compliance requirements for RDS"_
- _"What are the HIPAA requirements for S3?"_
- _"Show me NIST-800-53 controls for EC2"_
- _"What compliance standards apply to Lambda functions?"_

### 2. Research Knowledge Base

Try:
- _"Research best practices for AWS cost optimization"_
- _"Find DevOps patterns for Kubernetes deployments"_
- _"Search knowledge base for FinOps strategies"_
- _"What are the best practices for securing cloud infrastructure?"_

### 3. Check Your Usage

Visit [app.wistx.ai](https://app.wistx.ai) to:
- View API usage
- Manage API keys
- See indexed resources
- Monitor requests

---

## 🛠️ Available Tools

### Compliance Tools

- **`wistx_get_compliance_requirements`** - Get detailed compliance requirements for infrastructure resources
  - **Supports**: PCI-DSS, HIPAA, CIS, SOC2, NIST-800-53, ISO-27001, GDPR, FedRAMP, CCPA, SOX, GLBA
  - **Resources**: RDS, S3, EC2, Lambda, EKS, VPC, IAM, CloudFront, and more
  - **Returns**: Specific controls, remediation guidance, code examples, verification procedures

### Knowledge Base Tools

- **`wistx_research_knowledge_base`** - Deep research across DevOps, infrastructure, compliance, FinOps domains
  - **Domains**: compliance, finops, devops, infrastructure, security, architecture, platform, sre
  - **Semantic search** across 10,000+ articles
  - **Optional web search** integration (Tavily)
  - **Cross-domain insights** and relationships

---

## 📋 Environment Variables

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `WISTX_API_KEY` | ✅ Yes | Your API key from [app.wistx.ai](https://app.wistx.ai) | - |
| `WISTX_API_URL` | ⚠️ Optional | API base URL | `https://api.wistx.ai` |

**Note**: You can use `http://localhost:8000` for local development if you're running the backend API locally.

---

## 🔧 Troubleshooting

### MCP Server Not Found

**Error**: `command not found: wistx-mcp`

**Solution**:
```bash
# Reinstall with pipx
pipx install --force wistx-mcp

# Or verify installation
pipx list | grep wistx

# Or verify command exists
which wistx-mcp
```

### API Key Invalid

**Error**: `401 Unauthorized` or authentication errors

**Solution**:
1. Verify API key at [app.wistx.ai](https://app.wistx.ai)
2. Check API key in configuration (no extra spaces, correct format)
3. Ensure `WISTX_API_URL` is correct (`https://api.wistx.ai`)
4. Check API key hasn't expired

### Connection Error

**Error**: `Connection refused` or `Network error`

**Solution**:
1. Check `WISTX_API_URL` is correct (`https://api.wistx.ai`)
2. Verify internet connection
3. Check firewall/proxy settings
4. Verify backend API is running (if using localhost)

### Module Not Found Error

**Error**: `ModuleNotFoundError: No module named 'wistx_mcp.tools.lib'`

**Solution**:
1. Reinstall package: `pipx install --force wistx-mcp`
2. Or reinstall with pip: `pip install --force-reinstall wistx-mcp`
3. Verify package version: `pip show wistx-mcp`
4. Check package includes all files: `pip show -f wistx-mcp | grep tools/lib`

---

## 📚 Complete Configuration Examples

### Cursor (macOS)

**File**: `~/.cursor/mcp.json`

**Production** (using hosted API):
```json
{
  "mcpServers": {
    "wistx": {
      "command": "pipx",
      "args": ["run", "--no-cache", "wistx-mcp"],
      "env": {
        "WISTX_API_KEY": "wistx_xxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "WISTX_API_URL": "https://api.wistx.ai"
      }
    }
  }
}
```

**Local Development** (using localhost):
```json
{
  "mcpServers": {
    "wistx": {
      "command": "pipx",
      "args": ["run", "--no-cache", "wistx-mcp"],
      "env": {
        "WISTX_API_KEY": "YOUR_API_KEY",
        "WISTX_API_URL": "http://localhost:8000"
      }
    }
  }
}
```

**Note**: For localhost, make sure your backend API is running:
```bash
uv run uvicorn api.main:app --reload
```

### Claude Desktop (macOS)

**File**: `~/.config/claude-desktop/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "wistx": {
      "command": "pipx",
      "args": ["run", "--no-cache", "wistx-mcp"],
      "env": {
        "WISTX_API_KEY": "wistx_xxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "WISTX_API_URL": "https://api.wistx.ai"
      }
    }
  }
}
```

### Windsurf / Codex

**File**: `~/.codeium/windsurf/mcp_config.json`

```json
{
  "mcpServers": {
    "wistx": {
      "command": "pipx",
      "args": ["run", "--no-cache", "wistx-mcp"],
      "env": {
        "WISTX_API_KEY": "wistx_xxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "WISTX_API_URL": "https://api.wistx.ai"
      }
    }
  }
}
```

---

## 🎯 Quick Start Checklist

- [ ] Install Python 3.11+
- [ ] Install `pipx`: `brew install pipx` (macOS) or `pip install pipx` (Linux/Windows)
- [ ] Install WISTX MCP: `pipx install wistx-mcp`
- [ ] Get API key from [app.wistx.ai](https://app.wistx.ai)
- [ ] Open MCP configuration file for your editor
- [ ] Add WISTX configuration with your API key
- [ ] Restart your coding assistant
- [ ] Test: Ask _"Get PCI-DSS compliance requirements for RDS"_

---

## 📖 Additional Resources

- **Full Documentation**: [docs.wistx.ai](https://docs.wistx.ai)
- **API Reference**: [docs.wistx.ai/api](https://docs.wistx.ai/api)
- **Support**: [app.wistx.ai/support](https://app.wistx.ai/support)
- **GitHub**: [github.com/wistx/wistx-api](https://github.com/wistx/wistx-api)

---

**Need Help?** Join our community or reach out through [app.wistx.ai](https://app.wistx.ai) for support and updates.

