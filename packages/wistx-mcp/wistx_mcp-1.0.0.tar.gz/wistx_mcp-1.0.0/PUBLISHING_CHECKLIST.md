# Publishing Checklist: wistx-mcp

## ⚠️ Before Publishing

### 1. **PyPI Account Setup** (Required)

**Create PyPI account**:
1. Go to: https://pypi.org/account/register/
2. Create account
3. Verify email

**Get API token** (for `uv publish`):
1. Go to: https://pypi.org/manage/account/
2. Scroll to "API tokens"
3. Create token with scope: "Entire account" or "Project: wistx-mcp"
4. Copy token

**Configure credentials**:
```bash
# Option A: Use token directly
uv publish --token pypi-xxxxxxxxxxxxx

# Option B: Configure in ~/.pypirc
# [pypi]
# username = __token__
# password = pypi-xxxxxxxxxxxxx
```

---

### 2. **Test Build Locally** (Required)

**Build package**:
```bash
uv build
```

**Verify build**:
```bash
# Check dist/ directory
ls -la dist/

# Should see:
# - wistx_mcp-1.0.0-py3-none-any.whl
# - wistx_mcp-1.0.0.tar.gz
```

**Test installation locally**:
```bash
# Install from local wheel
pip install dist/wistx_mcp-1.0.0-py3-none-any.whl

# Or use uv
uv pip install dist/wistx_mcp-1.0.0-py3-none-any.whl

# Test command works
wistx-mcp --help
# Should show MCP server starting (or error if no API key)
```

**Uninstall test**:
```bash
pip uninstall wistx-mcp -y
```

---

### 3. **Backend API Status** (Important)

**Current default**: `http://localhost:8000`

**Options**:

**Option A: Host Backend API First** (Recommended)
- Deploy `api/main.py` to Railway/Render/AWS
- Get URL: `https://api.wistx.ai`
- Update `wistx_mcp/config.py` default to hosted URL
- Users can override with `WISTX_API_URL` env var

**Option B: Keep Localhost Default** (For Development)
- Users must set `WISTX_API_URL` env var
- Or run backend locally
- Not ideal for production

**Recommendation**: Host backend API first, then publish MCP server.

---

### 4. **Package Configuration Check** ✅

**Verify `pyproject.toml`**:
- ✅ Name: `wistx-mcp`
- ✅ Version: `1.0.0`
- ✅ Entry point: `wistx-mcp = "wistx_mcp.server:cli"`
- ✅ Packages: `["wistx_mcp"]`
- ✅ Dependencies: All listed
- ✅ README: Exists

**Verify `wistx_mcp/server.py`**:
- ✅ `cli()` function exists
- ✅ Calls `asyncio.run(main())`
- ✅ Error handling present

---

### 5. **Test MCP Server Locally** (Recommended)

**Test with local backend**:
```bash
# Terminal 1: Start backend API
cd /path/to/wistx-model
uv run uvicorn api.main:app --reload

# Terminal 2: Test MCP server
export WISTX_API_URL="http://localhost:8000"
export WISTX_API_KEY="test-key"  # Or your real API key
wistx-mcp
# Should start MCP server (stdio mode)
```

**Test with Cursor**:
```json
{
  "mcpServers": {
    "wistx": {
      "command": "wistx-mcp",
      "env": {
        "WISTX_API_URL": "http://localhost:8000",
        "WISTX_API_KEY": "YOUR_API_KEY"
      }
    }
  }
}
```

---

## 🚀 Publishing Steps

### Step 1: Build Package

```bash
uv build
```

**Verify**:
- `dist/wistx_mcp-1.0.0-py3-none-any.whl` exists
- `dist/wistx_mcp-1.0.0.tar.gz` exists

---

### Step 2: Test Installation (Optional but Recommended)

```bash
# Install from wheel
pip install dist/wistx_mcp-1.0.0-py3-none-any.whl

# Test command
wistx-mcp --help

# Uninstall
pip uninstall wistx-mcp -y
```

---

### Step 3: Publish to PyPI

**First time** (requires token):
```bash
uv publish --token pypi-xxxxxxxxxxxxx
```

**Subsequent publishes**:
```bash
# If token configured
uv publish

# Or with token
uv publish --token pypi-xxxxxxxxxxxxx
```

**What happens**:
- Uploads wheel and source distribution to PyPI
- Package becomes available at: https://pypi.org/project/wistx-mcp/
- Users can install: `pip install wistx-mcp`

---

### Step 4: Verify Publication

**Check PyPI**:
- Visit: https://pypi.org/project/wistx-mcp/
- Should show version 1.0.0
- Should show description, dependencies, etc.

**Test installation**:
```bash
# Install from PyPI
pip install wistx-mcp

# Verify command
wistx-mcp --help

# Should work!
```

---

## ⚠️ Important Notes

### Backend API Dependency

**Current State**:
- MCP server defaults to `http://localhost:8000`
- Users need to either:
  1. Run backend locally, OR
  2. Set `WISTX_API_URL` env var to hosted API

**For Production**:
- **Host backend API first** (Railway/Render/AWS)
- Update default `WISTX_API_URL` in `wistx_mcp/config.py`
- Then publish MCP server

**Users will need**:
- `WISTX_API_KEY` (from your web app)
- `WISTX_API_URL` (if not using default)

---

### Version Management

**After publishing**:
- To update: Change version in `pyproject.toml`
- Build: `uv build`
- Publish: `uv publish`

**Version format**: `MAJOR.MINOR.PATCH` (e.g., `1.0.0`)

---

## ✅ Ready to Publish?

### Checklist:

- [ ] PyPI account created
- [ ] API token obtained
- [ ] Backend API hosted (or users will set `WISTX_API_URL`)
- [ ] `pyproject.toml` configured correctly
- [ ] `cli()` function exists in `server.py`
- [ ] Tested build locally (`uv build`)
- [ ] Tested installation locally (`pip install dist/...`)
- [ ] Tested MCP server works
- [ ] README.md exists and is accurate

### If all checked ✅:

```bash
# Build
uv build

# Publish
uv publish --token pypi-xxxxxxxxxxxxx

# Verify
pip install wistx-mcp
wistx-mcp --help
```

---

## 🎯 After Publishing

### 1. Update Documentation

- Update `INSTALLATION_GUIDE.md` with PyPI installation
- Update README.md
- Create user portal at `app.wistx.ai` for API keys

### 2. Create npm Package (Optional)

- For MCP registry submission
- Wrapper around Python package
- See `MANUAL_URLS_AND_MCP_PUBLISHING.md`

### 3. Submit to MCP Registry (Optional)

- Go to: https://modelcontextprotocol.io/registry
- Submit npm package (if created)
- Or submit Python package directly

---

## 🚨 Common Issues

### Issue: "Package already exists"

**Solution**: Change version in `pyproject.toml` or use different package name

### Issue: "Authentication failed"

**Solution**: Check API token is correct, or use `--token` flag

### Issue: "Missing dependencies"

**Solution**: Ensure all dependencies are in `pyproject.toml` `[project.dependencies]`

### Issue: "Entry point not found"

**Solution**: Verify `cli()` function exists and `[project.scripts]` is correct

---

## Summary

**To publish**:
1. ✅ Set up PyPI account + token
2. ✅ Test build locally
3. ⚠️ Host backend API (recommended)
4. ✅ Run `uv build`
5. ✅ Run `uv publish --token pypi-xxx`
6. ✅ Verify on PyPI

**After publishing**:
- Users can install: `pip install wistx-mcp`
- Users configure: `WISTX_API_KEY` and `WISTX_API_URL`
- Users use: `wistx-mcp` command

**You're almost ready!** Just need PyPI account + token, and optionally host backend API first.

