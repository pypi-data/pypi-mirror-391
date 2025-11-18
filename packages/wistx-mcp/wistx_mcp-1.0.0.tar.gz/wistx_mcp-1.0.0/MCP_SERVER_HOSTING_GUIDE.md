# MCP Server Hosting Guide (Nia-Style Pattern)

## Overview

Following the [Nia MCP pattern](https://docs.trynia.ai/integrations/nia-mcp#cursor), your MCP server uses a **hybrid approach**:
- **MCP Server**: Runs locally on user's machine (via pipx/uvx/pip)
- **Backend API**: Hosted by you (like Nia's `https://apigcp.trynia.ai/`)
- **Authentication**: Users provide API key via environment variable

This is the **recommended pattern** for MCP servers! ✅

---

## Nia-Style Architecture (Recommended) ✅

### How It Works (Like Nia)

**Pattern**: Local MCP Server + Hosted API Backend

**Architecture**:
```
User's Machine
├─ Claude Desktop/Cursor/Windsurf
├─ MCP Server (local, installed via pipx/uvx/pip)
│  └─ Connects to your hosted API
│
Your Infrastructure
├─ Backend API (hosted, e.g., https://api.wistx.ai/)
│  ├─ API Key Authentication
│  ├─ Rate Limiting
│  └─ Connects to:
│     ├─ MongoDB Atlas (your shared instance)
│     ├─ Pinecone (your shared instance)
│     └─ OpenAI API (your key or user's key)
```

**Benefits**:
- ✅ Users install locally (simple, fast)
- ✅ You control backend (updates, monitoring)
- ✅ API key authentication (usage tracking, billing)
- ✅ Scales automatically (each user runs their own MCP server)
- ✅ Low latency (local MCP server, only API calls go over network)

**Pros**:
- ✅ Zero infrastructure cost for you
- ✅ Low latency (local process)
- ✅ No hosting complexity
- ✅ Users control their own environment
- ✅ Scales automatically (each user runs their own)

**Cons**:
- ❌ Users need to install Python/node
- ❌ Users need to configure environment variables
- ❌ Updates require users to update package

**When to Use**:
- ✅ Primary distribution method
- ✅ Most users (individual developers)
- ✅ Open source / community use

---

### Option 2: **Hosted Service** (For Enterprise/Managed Service)

**How It Works**:
- You host MCP server as a service
- Users connect via HTTP/SSE transport (if MCP supports) or proxy
- Requires converting stdio transport to HTTP/SSE

**Architecture**:
```
Your Infrastructure
├─ MCP Server (hosted service)
├─ HTTP/SSE endpoint
└─ Connects to:
   ├─ MongoDB Atlas
   ├─ Pinecone
   └─ OpenAI API

User's Machine
├─ Claude Desktop/Cursor/Windsurf
└─ Connects to your hosted MCP server
```

**Pros**:
- ✅ Users don't need to install anything
- ✅ You control updates
- ✅ Centralized monitoring/logging
- ✅ Better for enterprise customers

**Cons**:
- ❌ Infrastructure cost ($10-50/month)
- ❌ Requires HTTP/SSE transport support
- ❌ More complex deployment
- ❌ Latency (network calls)

**When to Use**:
- ✅ Enterprise customers
- ✅ Managed service offering
- ✅ Users who can't install locally

---

### Option 3: **Hybrid** (Best of Both Worlds) ✅

**How It Works**:
- Offer both local and hosted options
- Users choose based on their needs
- Local = default, hosted = premium/enterprise

**Architecture**:
```
Option A: Local (default)
User's Machine → Local MCP Server → Your Infrastructure

Option B: Hosted (premium)
User's Machine → Your Hosted MCP Server → Your Infrastructure
```

**Pros**:
- ✅ Maximum flexibility
- ✅ Free tier (local) + paid tier (hosted)
- ✅ Best user experience

**Cons**:
- ❌ More complex to maintain
- ❌ Need to support both modes

**When to Use**:
- ✅ Recommended approach
- ✅ Free + paid tiers
- ✅ Maximum market reach

---

## Implementation Guide

### Option 1: Local Hosting (Current Setup)

**Already Implemented!** ✅

**What Users Do**:
1. Install package:
   ```bash
   npm install -g @wistx/mcp-server
   # Or
   pip install wistx-mcp
   ```

2. Configure Claude Desktop:
   ```json
   {
     "mcpServers": {
       "wistx": {
         "command": "wistx-mcp",
         "env": {
           "MONGODB_URL": "mongodb://...",
           "PINECONE_API_KEY": "..."
         }
       }
     }
   }
   ```

3. Use it!

**What You Do**:
- ✅ Nothing! Users run it locally
- ✅ Just maintain MongoDB/Pinecone infrastructure
- ✅ Publish packages (npm + PyPI)

**Cost**: $0/month (users run locally)

---

### Option 2: Hosted Service

**Requires**: Converting stdio transport to HTTP/SSE

#### Step 1: Create HTTP/SSE Transport Wrapper

**File**: `wistx_mcp/server_http.py`

```python
"""HTTP/SSE transport for MCP server hosting."""

import asyncio
import logging
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from wistx_mcp.config import settings

logger = logging.getLogger(__name__)

app = FastAPI(title="WISTX MCP Server (HTTP)")

# Create MCP server instance
mcp_server = Server("wistx-mcp")

# Register tools (same as stdio version)
@app.on_event("startup")
async def startup():
    """Initialize MCP server."""
    # Register all tools here (same as stdio version)
    pass

@app.post("/sse")
async def sse_endpoint(request: Request):
    """SSE endpoint for MCP protocol."""
    transport = SseServerTransport("/messages")
    
    async def event_stream():
        async with transport.connect_sse(request) as streams:
            read_stream, write_stream = streams
            await mcp_server.run(
                read_stream,
                write_stream,
                mcp_server.create_initialization_options()
            )
    
    return StreamingResponse(event_stream(), media_type="text/event-stream")

@app.get("/health")
async def health():
    """Health check."""
    return {"status": "healthy", "server": "wistx-mcp"}
```

#### Step 2: Create Dockerfile

**File**: `wistx_mcp/Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen

# Copy MCP server code
COPY wistx_mcp/ ./wistx_mcp/

# Expose port
EXPOSE 8001

# Run HTTP server
CMD ["uv", "run", "uvicorn", "wistx_mcp.server_http:app", "--host", "0.0.0.0", "--port", "8001"]
```

#### Step 3: Deploy to Cloud

**Option A: AWS ECS/Fargate**

```yaml
# docker-compose.yml
version: '3.8'

services:
  mcp-server:
    build:
      context: .
      dockerfile: wistx_mcp/Dockerfile
    ports:
      - "8001:8001"
    environment:
      - MONGODB_URL=${MONGODB_URL}
      - PINECONE_API_KEY=${PINECONE_API_KEY}
      - PINECONE_INDEX_NAME=${PINECONE_INDEX_NAME}
    restart: unless-stopped
```

**Option B: GCP Cloud Run**

```bash
# Build and deploy
gcloud builds submit --tag gcr.io/PROJECT_ID/wistx-mcp-server
gcloud run deploy wistx-mcp-server \
  --image gcr.io/PROJECT_ID/wistx-mcp-server \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars MONGODB_URL=...,PINECONE_API_KEY=...
```

**Option C: Railway/Render/Fly.io**

```bash
# Railway
railway up

# Render
render.yaml:
services:
  - type: web
    name: wistx-mcp-server
    env: docker
    dockerfilePath: ./wistx_mcp/Dockerfile
    envVars:
      - key: MONGODB_URL
        value: ${MONGODB_URL}
```

#### Step 4: Configure Users

**Claude Desktop Config**:
```json
{
  "mcpServers": {
    "wistx": {
      "url": "https://mcp.wistx.ai/sse",
      "headers": {
        "Authorization": "Bearer YOUR_API_KEY"
      }
    }
  }
}
```

**Cost**: $10-50/month (small instance)

---

### Option 3: Hybrid Approach (Recommended)

**Strategy**: Offer both options

**Free Tier** (Local):
- Users install locally
- Connect to shared MongoDB/Pinecone
- Zero cost for you

**Premium Tier** (Hosted):
- Hosted MCP server
- Managed service
- $10-50/month per user

**Implementation**:
1. ✅ Keep local hosting (already done)
2. ✅ Add hosted service (Option 2)
3. ✅ Add API key authentication for hosted
4. ✅ Pricing page with both options

---

## Current Setup Analysis

### Your Current MCP Server

**Transport**: stdio (local execution)
**Location**: `wistx_mcp/server.py`
**Entry Point**: `wistx_mcp.server:main`

**How It Works**:
```python
# wistx_mcp/server.py
async def main():
    app = Server("wistx-mcp")
    # ... register tools ...
    
    # Uses stdio transport
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, init_options)
```

**This is perfect for local hosting!** ✅

---

## Implementation Guide (Nia-Style)

### Step 1: Host Backend API ✅

**Deploy your FastAPI backend** (already built!):

**Option A: Railway** (Easiest)
```bash
# Install Railway CLI
npm i -g @railway/cli

# Deploy
railway up
```

**Option B: Render**
```yaml
# render.yaml
services:
  - type: web
    name: wistx-api
    env: python
    buildCommand: uv sync
    startCommand: uv run uvicorn api.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: MONGODB_URL
        sync: false
      - key: PINECONE_API_KEY
        sync: false
```

**Option C: AWS/GCP**
```bash
# Build Docker image
docker build -t wistx-api -f api/Dockerfile .

# Deploy to Cloud Run / ECS / etc.
```

**Get your API URL**: `https://api.wistx.ai/` (or your domain)

**Cost**: $10-50/month (small instance)

---

### Step 2: Update MCP Server Config ✅

**Update default API URL** (`wistx_mcp/config.py`):
```python
api_url: str = Field(
    default="https://api.wistx.ai",  # ← Change from localhost
    validation_alias="WISTX_API_URL",
    description="WISTX API base URL",
)
```

**Already supports**:
- ✅ API key authentication (`WISTX_API_KEY`)
- ✅ Configurable API URL (`WISTX_API_URL`)
- ✅ Environment variable support

---

### Step 3: Publish MCP Server Package ✅

**Update `pyproject.toml`**:
```toml
[project]
name = "wistx-mcp-server"
version = "1.0.0"
description = "WISTX MCP Server - DevOps compliance and pricing context"

[project.scripts]
wistx-mcp-server = "wistx_mcp.server:main"

[tool.hatch.build.targets.wheel]
packages = ["wistx_mcp"]
```

**Build and Publish**:
```bash
# Build
uv build

# Publish to PyPI
uv publish
```

**Users install**:
```bash
# Option A: pipx (Recommended, like Nia)
pipx install wistx-mcp-server

# Option B: uvx
uvx wistx-mcp-server

# Option C: pip
pip install wistx-mcp-server
```

---

### Step 4: User Configuration (Like Nia) ✅

**Users configure in Cursor** (`~/.cursor/mcp.json`):

**Option A: Using pipx** (Recommended, like Nia)
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

**Users get API key from**: `app.wistx.ai` (your web app)

---

### Step 5: Documentation (Like Nia) ✅

**Create installation guide** (`docs/installation.md`):

```markdown
# WISTX MCP Server Installation

## Prerequisites
- Python 3.11+
- `pipx` (recommended) or `uvx` or `pip`
- Your WISTX API key from app.wistx.ai

## Installation

### Option A: Using pipx (Recommended)
```bash
pipx install wistx-mcp-server
```

### Option B: Using uvx
```bash
uvx wistx-mcp-server
```

### Option C: Using pip
```bash
pip install wistx-mcp-server
```

## Configuration

### Cursor
1. Open `~/.cursor/mcp.json`
2. Add configuration:
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
3. Replace `YOUR_API_KEY` with your API key from app.wistx.ai
4. Restart Cursor

## Try It Out!
Ask your coding agent: "Get PCI-DSS compliance requirements for RDS"
```

---

### Phase 2: Hosted Service (Future - Optional)

**When to Add**:
- Enterprise customers request it
- Need managed service offering
- Want premium tier

**What to Do**:
1. Create HTTP/SSE transport wrapper
2. Deploy to cloud (AWS/GCP/Railway)
3. Add API key authentication
4. Document hosted option

**Cost**: $10-50/month

---

## Quick Start (Nia-Style)

### For Users

**1. Get API Key**:
- Visit: `app.wistx.ai`
- Sign up / Login
- Get your API key

**2. Install MCP Server**:
```bash
# Recommended (like Nia)
pipx install wistx-mcp-server

# Or
uvx wistx-mcp-server

# Or
pip install wistx-mcp-server
```

**3. Configure Cursor** (`~/.cursor/mcp.json`):
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

**4. Restart Cursor** and use!

**No MongoDB/Pinecone config needed!** ✅ (handled by your backend)

---

### For You (Publishing)

**1. Update `pyproject.toml`**:
```toml
[project]
name = "wistx-mcp"
version = "1.0.0"

[project.scripts]
wistx-mcp = "wistx_mcp.server:main"

[tool.hatch.build.targets.wheel]
packages = ["wistx_mcp"]
```

**2. Build and Publish**:
```bash
# Build
uv build

# Publish to PyPI
uv publish

# Create npm wrapper (separate package)
cd wistx-mcp-server
npm publish
```

**3. Submit to MCP Registry**:
- Go to: https://modelcontextprotocol.io/registry
- Submit npm package: `@wistx/mcp-server`

---

## Cost Comparison

| Option | Your Cost | User Cost | Complexity |
|--------|-----------|-----------|------------|
| **Local** | $0/month | $0 | Low ✅ |
| **Hosted** | $10-50/month | $0-10/month | Medium |
| **Hybrid** | $10-50/month | $0-10/month | Medium |

**Recommendation**: Start with **Local** (free), add **Hosted** later if needed.

---

## Infrastructure Requirements

### What You Need to Host

**MongoDB Atlas**:
- ✅ Already set up
- ✅ Shared by all users (local + hosted)
- ✅ Cost: ~$10-50/month

**Pinecone**:
- ✅ Already set up
- ✅ Shared by all users
- ✅ Cost: ~$10-50/month

**MCP Server** (if hosting):
- ⚠️ Optional (only if offering hosted service)
- ⚠️ Small instance (t3.small or equivalent)
- ⚠️ Cost: ~$10-50/month

**Total Infrastructure Cost**:
- **Local only**: $20-100/month (MongoDB + Pinecone)
- **Local + Hosted**: $30-150/month (MongoDB + Pinecone + MCP server)

---

## Summary: Nia-Style Pattern ✅

### Architecture (Like Nia)

**What You Have**:
- ✅ MCP server (stdio transport) - runs locally
- ✅ Backend API (FastAPI) - ready to host
- ✅ API key authentication - already implemented
- ✅ Configurable API URL - already supported

**What to Do**:
1. ✅ **Host Backend API** (Railway/Render/AWS/GCP)
   - Deploy `api/main.py`
   - Get URL: `https://api.wistx.ai`
   - Cost: $10-50/month

2. ✅ **Update Default API URL**
   - Change `wistx_mcp/config.py` default to your hosted URL

3. ✅ **Publish MCP Server Package**
   - Update `pyproject.toml`
   - Build: `uv build`
   - Publish: `uv publish`

4. ✅ **Create User Portal**
   - Web app at `app.wistx.ai`
   - Users sign up / get API keys
   - Usage dashboard

5. ✅ **Document Like Nia**
   - Installation guide
   - Configuration examples
   - API key setup

### Cost Breakdown

**Infrastructure**:
- Backend API: $10-50/month (Railway/Render/AWS)
- MongoDB Atlas: $10-50/month (shared)
- Pinecone: $10-50/month (shared)
- **Total**: $30-150/month

**Revenue** (if charging):
- Free tier: 100 requests/month
- Paid tier: $10-50/month per user
- Enterprise: Custom pricing

### Comparison: Your Setup vs Nia

| Aspect | Nia | WISTX (Your Setup) |
|--------|-----|-------------------|
| **MCP Server** | Local (pipx) | Local (pipx/uvx/pip) ✅ |
| **Backend API** | Hosted (`apigcp.trynia.ai`) | Hosted (`api.wistx.ai`) ✅ |
| **API Key Auth** | Yes (`NIA_API_KEY`) | Yes (`WISTX_API_KEY`) ✅ |
| **Configurable URL** | Yes (`NIA_API_URL`) | Yes (`WISTX_API_URL`) ✅ |
| **Package** | `nia-mcp-server` | `wistx-mcp-server` ✅ |

**You're already set up correctly!** Just need to:
1. Host the backend API
2. Publish the package
3. Document it

---

## Recommendation

**Start with Local Hosting** ✅

**Why**:
- ✅ Zero cost
- ✅ Already implemented
- ✅ Scales automatically
- ✅ Best user experience (low latency)

**Add Hosted Service Later** (if needed)

**Why**:
- Enterprise customers may want it
- Can charge premium for managed service
- Better for users who can't install locally

**Bottom Line**: Your current setup is perfect for local hosting. Publish packages and let users run it locally. Add hosted service later if enterprise customers need it.

---

## Next Steps

1. ✅ **Publish Python Package**:
   - Update `pyproject.toml`
   - Build: `uv build`
   - Publish: `uv publish`

2. ✅ **Create npm Package**:
   - Create wrapper package
   - Publish: `npm publish`

3. ✅ **Submit to MCP Registry**:
   - Submit npm package
   - Get listed in Claude Desktop

4. ✅ **Document Installation**:
   - Create installation guide
   - Provide examples
   - Update README

5. ⚠️ **Optional: Hosted Service** (later):
   - Create HTTP/SSE wrapper
   - Deploy to cloud
   - Add API key auth

---

**You're ready to go with local hosting!** 🚀

