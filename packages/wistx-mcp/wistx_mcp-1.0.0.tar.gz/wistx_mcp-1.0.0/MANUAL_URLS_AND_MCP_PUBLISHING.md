# Manual URLs & MCP Publishing Guide

## Question 1: What About the Manual URLs I Added?

### ✅ **YES - Your Manual URLs Are Actively Used!**

Your manual URLs in `data_pipelines/config/source_registry.py` are **actively used** in the pipeline. Here's how:

---

### How Manual URLs Work

**Location**: `data_pipelines/config/source_registry.py:231-732`

**Process**:
1. **TRUSTED_DOMAINS** runs first (automated sitemap discovery)
2. **MANUAL_URLS** are then **added** to discovered URLs (doesn't replace)
3. Both sources are **combined** and **deduplicated**
4. Final URLs are used for collection

**Code**: `data_pipelines/collectors/discovery_helper.py:68-88`

```python
# Gets MANUAL_URLS for domain
domain_manual_urls = MANUAL_URLS.get(domain, {})

# Filters by subdomain if specified
if subdomain:
    manual_urls = domain_manual_urls.get(subdomain, [])
else:
    manual_urls = []
    for urls in domain_manual_urls.values():
        manual_urls.extend(urls)

# Separates PDFs from web URLs
if manual_urls:
    manual_pdf_urls = [url for url in manual_urls if url.endswith(".pdf")]
    manual_web_urls = [url for url in manual_urls if not url.endswith(".pdf")]
    all_web_urls.extend(manual_web_urls)  # ← Added to discovered URLs
    all_pdf_urls.extend(manual_pdf_urls)  # ← Added to discovered URLs
```

---

### Your Manual URLs Count

**Compliance Domain**:
- **PCI-DSS**: 13 URLs
- **CIS-AWS**: 8 URLs
- **CIS-GCP**: 6 URLs
- **CIS-Azure**: 5 URLs
- **HIPAA**: 13 URLs
- **SOC2**: 11 URLs
- **NIST-800-53**: 18 URLs
- **ISO-27001**: 11 URLs
- **GDPR**: 10 URLs
- **FedRAMP**: 12 URLs
- **CCPA**: 15 URLs
- **SOX**: 12 URLs
- **GLBA**: 12 URLs
- **GENERAL_DATA_PROTECTION_REGULATION**: 20+ URLs

**Total Compliance Manual URLs**: ~150+ URLs

**Other Domains**:
- **FinOps**: ~50+ URLs (AWS/GCP/Azure cost management)
- **Architecture**: ~30+ URLs (cloud docs, design principles)
- **Security**: ~40+ URLs (cloud security, Wiz.io academy)
- **DevOps**: ~50+ URLs (Kubernetes, Terraform, CI/CD tools)

**Total Manual URLs**: **~320+ URLs** across all domains

---

### Why Manual URLs Are Important

**1. Coverage**:
- ✅ URLs not in sitemaps (third-party sites, GitHub repos)
- ✅ Specific high-quality sources (official docs, authoritative blogs)
- ✅ PDF documents (often not in sitemaps)

**2. Quality**:
- ✅ Curated sources (you've vetted them)
- ✅ Official documentation (AWS, GCP, Azure)
- ✅ Authoritative blogs (CrowdStrike, Vanta, Drata)

**3. Fallback**:
- ✅ If auto-discovery fails, manual URLs still work
- ✅ Ensures pipeline always has URLs to process
- ✅ Provides baseline coverage

**4. Specificity**:
- ✅ Direct links to specific pages/PDFs
- ✅ Not dependent on sitemap structure
- ✅ Can target exact content you want

---

### How They're Used in Pipeline

**Step 1**: Discovery (`get_discovered_urls()`)
```
TRUSTED_DOMAINS → Discovers URLs from sitemaps
     +
MANUAL_URLS → Adds your manual URLs
     =
Combined URL list (deduplicated)
```

**Step 2**: Collection
```
Combined URLs → Collected via Crawl4AI/Docling
     ↓
Raw articles extracted
```

**Step 3**: Processing
```
Raw articles → Processed → Embedded → Stored
```

---

### Example: PCI-DSS Processing

**Input**:
- `domain = "compliance"`
- `subdomain = "PCI-DSS"`

**Process**:
1. **TRUSTED_DOMAINS**:
   - Discovers URLs from `pcisecuritystandards.org` sitemap
   - Filters by `/document_library/` pattern
   - Returns: `{"web_urls": [...], "pdf_urls": [...]}`

2. **MANUAL_URLS**:
   - Gets `MANUAL_URLS["compliance"]["PCI-DSS"]` (13 URLs)
   - Adds to discovered URLs:
     - `https://help.drata.com/en/articles/6038558-required-documentation-for-pci-dss`
     - `https://sprinto.com/blog/pci-dss-controls/`
     - `https://www.crowdstrike.com/en-us/cybersecurity-101/data-protection/pci-dss-requirements/`
     - `https://documentation.suse.com/compliance/all/pdf/article-security-pcidss_en.pdf`
     - ... (9 more URLs)

3. **Result**:
   - Combined list: Discovered URLs + 13 manual URLs
   - Deduplicated
   - Ready for collection

---

### Summary: Manual URLs

✅ **Status**: **Actively Used**
✅ **Purpose**: Supplement auto-discovery with curated high-quality sources
✅ **Count**: ~320+ URLs across all domains
✅ **Value**: Ensures comprehensive coverage and quality
✅ **Location**: `data_pipelines/config/source_registry.py:MANUAL_URLS`

**Your manual URLs are a critical part of the pipeline!** They ensure you have:
- ✅ High-quality sources
- ✅ Comprehensive coverage
- ✅ Fallback when auto-discovery fails
- ✅ Specific URLs you've vetted

---

## Question 2: For MCP, Does It Mean Publishing It Like a Package?

### ✅ **YES - MCP Servers Are Published as Packages!**

MCP servers can be published in multiple ways:

---

### Publishing Options

#### Option 1: **npm Package** (MCP Registry - Recommended)

**For**: Anthropic's official MCP registry (Claude Desktop)

**How**:
1. Create npm package wrapper
2. Publish to npm registry
3. Submit to MCP registry
4. Users install via `npm install -g @wistx/mcp-server`

**Example Structure**:
```
wistx-mcp-server/
├── package.json          # npm package config
├── index.js              # Wrapper that calls Python
├── bin/
│   └── wistx-mcp        # Executable
└── README.md
```

**package.json**:
```json
{
  "name": "@wistx/mcp-server",
  "version": "1.0.0",
  "description": "WISTX MCP Server for DevOps compliance and pricing context",
  "bin": {
    "wistx-mcp": "./bin/wistx-mcp"
  },
  "scripts": {
    "postinstall": "pip install wistx-mcp"
  },
  "dependencies": {
    "wistx-mcp": "^1.0.0"
  }
}
```

**Benefits**:
- ✅ Official MCP registry listing
- ✅ One-click installation in Claude Desktop
- ✅ Discoverable by users
- ✅ Version management via npm

---

#### Option 2: **Python Package** (PyPI)

**For**: Direct Python installation

**How**:
1. Update `pyproject.toml` (already configured!)
2. Build package: `uv build`
3. Publish to PyPI: `uv publish`

**Current Setup** (`pyproject.toml`):
```toml
[project]
name = "wistx-api"  # ← Change to "wistx-mcp" for MCP server
version = "0.1.0"
description = "WISTX API - MCP context server for DevOps compliance, pricing, and best practices"
keywords = ["mcp", "devops", "compliance", "pricing", "infrastructure", "api"]

[project.scripts]
wistx-mcp = "wistx_mcp.server:main"  # ← Add entry point
```

**Installation**:
```bash
pip install wistx-mcp
# Or
uv pip install wistx-mcp
```

**Benefits**:
- ✅ Direct Python installation
- ✅ Works with existing Python tooling
- ✅ Version management via PyPI

---

#### Option 3: **Both** (Recommended)

**Strategy**: Publish both npm and Python packages

**npm Package**:
- Wrapper that calls Python package
- For MCP registry (Claude Desktop)
- One-click installation

**Python Package**:
- Core MCP server code
- For direct Python installation
- For CI/CD, scripts, integrations

**Architecture**:
```
npm package (@wistx/mcp-server)
    ↓
calls Python package (wistx-mcp)
    ↓
runs MCP server (wistx_mcp/server.py)
```

---

### MCP Server Publishing Process

#### Step 1: Prepare Python Package

**Update `pyproject.toml`**:
```toml
[project]
name = "wistx-mcp"  # ← Change from "wistx-api"
version = "1.0.0"
description = "WISTX MCP Server - DevOps compliance and pricing context"
keywords = ["mcp", "devops", "compliance", "pricing"]

[project.scripts]
wistx-mcp = "wistx_mcp.server:main"  # ← Entry point

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["wistx_mcp"]  # ← Only MCP server code
```

**Build**:
```bash
uv build
# Creates: dist/wistx_mcp-1.0.0-py3-none-any.whl
```

**Publish to PyPI**:
```bash
uv publish
# Or: twine upload dist/*
```

---

#### Step 2: Create npm Package Wrapper

**Create `wistx-mcp-server/package.json`**:
```json
{
  "name": "@wistx/mcp-server",
  "version": "1.0.0",
  "description": "WISTX MCP Server for DevOps compliance and pricing context",
  "main": "index.js",
  "bin": {
    "wistx-mcp": "./bin/wistx-mcp"
  },
  "scripts": {
    "postinstall": "pip install --quiet wistx-mcp || uv pip install wistx-mcp"
  },
  "keywords": ["mcp", "devops", "compliance", "pricing"],
  "author": "WISTX Team",
  "license": "MIT"
}
```

**Create `wistx-mcp-server/bin/wistx-mcp`**:
```bash
#!/bin/bash
# Wrapper script that calls Python MCP server
exec python -m wistx_mcp.server "$@"
```

**Create `wistx-mcp-server/index.js`**:
```javascript
// npm package entry point
module.exports = require('./bin/wistx-mcp');
```

**Publish to npm**:
```bash
cd wistx-mcp-server
npm publish --access public
```

---

#### Step 3: Submit to MCP Registry

**MCP Registry** (Anthropic's official registry):
1. Go to: https://modelcontextprotocol.io/registry
2. Submit your npm package
3. Provide:
   - Package name: `@wistx/mcp-server`
   - Description
   - Documentation URL
   - GitHub repository

**Benefits**:
- ✅ Listed in official MCP registry
- ✅ Discoverable in Claude Desktop
- ✅ One-click installation
- ✅ Version management

---

### Installation Methods

#### Method 1: **npm (MCP Registry)**

**Users install via npm**:
```bash
npm install -g @wistx/mcp-server
```

**Configure in Claude Desktop** (`~/.config/claude-desktop/claude_desktop_config.json`):
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

---

#### Method 2: **Python (PyPI)**

**Users install via pip**:
```bash
pip install wistx-mcp
# Or
uv pip install wistx-mcp
```

**Configure in Claude Desktop**:
```json
{
  "mcpServers": {
    "wistx": {
      "command": "python",
      "args": ["-m", "wistx_mcp.server"],
      "env": {
        "MONGODB_URL": "mongodb://...",
        "PINECONE_API_KEY": "..."
      }
    }
  }
}
```

---

#### Method 3: **Local Development** (Current Setup)

**For development/testing**:
```json
{
  "mcpServers": {
    "wistx": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/wistx-model", "python", "-m", "wistx_mcp.server"],
      "env": {
        "WISTX_API_URL": "http://localhost:8000"
      }
    }
  }
}
```

---

### Publishing Checklist

#### Python Package (PyPI)
- [ ] Update `pyproject.toml`:
  - [ ] Change `name` to `wistx-mcp`
  - [ ] Add `[project.scripts]` entry point
  - [ ] Update `[tool.hatch.build.targets.wheel]` packages
- [ ] Build package: `uv build`
- [ ] Test installation: `pip install dist/wistx_mcp-*.whl`
- [ ] Publish to PyPI: `uv publish`
- [ ] Verify: `pip install wistx-mcp`

#### npm Package (MCP Registry)
- [ ] Create `wistx-mcp-server/` directory
- [ ] Create `package.json` with bin entry
- [ ] Create `bin/wistx-mcp` wrapper script
- [ ] Test locally: `npm link`
- [ ] Publish to npm: `npm publish --access public`
- [ ] Submit to MCP registry

#### Documentation
- [ ] Create installation guide
- [ ] Document configuration
- [ ] Provide examples
- [ ] Update README.md

---

### Recommended Publishing Strategy

**Phase 1: Python Package** (Start Here)
1. ✅ Update `pyproject.toml`
2. ✅ Build and publish to PyPI
3. ✅ Test installation
4. ✅ Document usage

**Phase 2: npm Package** (For MCP Registry)
1. ✅ Create npm wrapper
2. ✅ Publish to npm
3. ✅ Submit to MCP registry
4. ✅ Test in Claude Desktop

**Phase 3: Documentation**
1. ✅ Installation guide
2. ✅ Configuration examples
3. ✅ Troubleshooting guide
4. ✅ API documentation

---

### Summary: MCP Publishing

✅ **Yes, MCP servers are published as packages!**

**Options**:
1. **npm Package** → MCP registry (Claude Desktop) ← **Recommended**
2. **Python Package** → PyPI (direct installation)
3. **Both** → Maximum reach

**Current Status**:
- ✅ `pyproject.toml` configured (ready for PyPI)
- ✅ MCP server code ready (`wistx_mcp/server.py`)
- ⚠️ Need to create npm wrapper for MCP registry
- ⚠️ Need to submit to MCP registry

**Next Steps**:
1. Update `pyproject.toml` for MCP server package
2. Publish Python package to PyPI
3. Create npm wrapper package
4. Publish npm package
5. Submit to MCP registry

---

## Combined Summary

### Manual URLs
✅ **Status**: Actively used (~320+ URLs)
✅ **Purpose**: Supplement auto-discovery with curated sources
✅ **Value**: Ensures comprehensive coverage and quality

### MCP Publishing
✅ **Yes**: Published as packages (npm + Python)
✅ **Strategy**: Publish both for maximum reach
✅ **Next**: Update `pyproject.toml` and create npm wrapper

**Both are production-ready and important!** 🚀

