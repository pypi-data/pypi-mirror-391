# TRUSTED_DOMAINS and MANUAL_URLS Explained

## ✅ Summary

**TRUSTED_DOMAINS**: ✅ **USED** - For automated sitemap-based URL discovery  
**MANUAL_URLS**: ✅ **USED** - As fallback/supplement to discovered URLs

Both are actively used in the knowledge pipeline orchestrator.

---

## 1. What TRUSTED_DOMAINS Does

### 1.1 Purpose

`TRUSTED_DOMAINS` enables **automated URL discovery** from trusted domains using sitemap discovery.

### 1.2 How It Works

**Location**: `data_pipelines/config/source_registry.py:8-229`

**Process**:
1. ✅ Takes domain configurations (e.g., `pcisecuritystandards.org`)
2. ✅ Converts domain to sitemap URLs automatically:
   - `https://{domain}/sitemap.xml`
   - `https://{domain}/sitemap_index.xml`
   - `https://www.{domain}/sitemap.xml`
   - `https://www.{domain}/sitemap_index.xml`
3. ✅ Fetches sitemap XML files
4. ✅ Extracts all URLs from sitemaps
5. ✅ Filters URLs by `path_patterns` (e.g., `/document_library/`)
6. ✅ Filters by `content_types` (e.g., `["pdf", "html"]`)
7. ✅ Separates PDFs from web URLs
8. ✅ Returns discovered URLs

### 1.3 Example Configuration

```python
TRUSTED_DOMAINS = {
    "compliance": {
        "tier_1": [
            {
                "domain": "pcisecuritystandards.org",
                "discovery_mode": "sitemap",  # Uses sitemap discovery
                "path_patterns": ["/document_library/", "/requirements/"],
                "content_types": ["pdf", "html"],
            },
        ],
    },
}
```

**What Happens**:
- Domain: `pcisecuritystandards.org`
- Tries sitemap URLs: `https://pcisecuritystandards.org/sitemap.xml`, etc.
- Extracts URLs matching `/document_library/` or `/requirements/`
- Filters to PDFs and HTML pages
- Returns: `{"web_urls": [...], "pdf_urls": [...]}`

### 1.4 Where It's Used

**File**: `data_pipelines/collectors/discovery_helper.py:24-41`

```python
async def get_discovered_urls(domain: str, subdomain: str | None = None):
    # Gets TRUSTED_DOMAINS config
    domain_configs = TRUSTED_DOMAINS.get(domain, {}).get("tier_1", [])
    
    # Uses SourceDiscovery to discover URLs from sitemaps
    if domain_configs:
        async with SourceDiscovery() as discovery:
            for domain_config in domain_configs:
                discovered = await discovery.discover_all_for_domain(domain_config)
                all_web_urls.extend(discovered["web_urls"])
                all_pdf_urls.extend(discovered["pdf_urls"])
```

**Called From**: `data_pipelines/processors/knowledge_pipeline_orchestrator.py:98`

```python
discovered = await get_discovered_urls(domain, subdomain)
web_urls = discovered.get("web_urls", [])
pdf_urls = discovered.get("pdf_urls", [])
```

---

## 2. What MANUAL_URLS Does

### 2.1 Purpose

`MANUAL_URLS` provides **manual URL fallback/supplement** when automated discovery:
- Fails to find URLs
- Needs additional URLs not in sitemaps
- Requires specific URLs that may not be in sitemaps

### 2.2 How It Works

**Location**: `data_pipelines/config/source_registry.py:231-732`

**Process**:
1. ✅ Gets manual URLs for domain/subdomain
2. ✅ Separates PDFs from web URLs
3. ✅ **Adds to discovered URLs** (doesn't replace)
4. ✅ Combines with TRUSTED_DOMAINS results

### 2.3 Example Configuration

```python
MANUAL_URLS = {
    "compliance": {
        "PCI-DSS": [
            "https://www.pcisecuritystandards.org/document_library/",
            "https://help.drata.com/en/articles/6038558-required-documentation-for-pci-dss",
            "https://documentation.suse.com/compliance/all/pdf/article-security-pcidss_en.pdf",
        ],
    },
}
```

### 2.4 Where It's Used

**File**: `data_pipelines/collectors/discovery_helper.py:43-63`

```python
# Gets MANUAL_URLS for domain
domain_manual_urls = MANUAL_URLS.get(domain, {})

# Filters by subdomain if specified
if subdomain:
    manual_urls = domain_manual_urls.get(subdomain, [])
else:
    # Gets all manual URLs for domain
    manual_urls = []
    for urls in domain_manual_urls.values():
        manual_urls.extend(urls)

# Separates PDFs from web URLs
if manual_urls:
    manual_pdf_urls = [url for url in manual_urls if url.endswith(".pdf")]
    manual_web_urls = [url for url in manual_urls if not url.endswith(".pdf")]
    
    # ADDS to discovered URLs (doesn't replace)
    all_web_urls.extend(manual_web_urls)
    all_pdf_urls.extend(manual_pdf_urls)
```

---

## 3. How They Work Together

### 3.1 Complete Flow

```
┌─────────────────────────────────────────────────────────────┐
│              get_discovered_urls(domain, subdomain)         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  STEP 1: TRUSTED_DOMAINS Discovery                         │
│                                                             │
│  1. Get domain configs from TRUSTED_DOMAINS[domain]["tier_1"] │
│  2. For each domain config:                                 │
│     - Convert domain → sitemap URLs                         │
│     - Fetch sitemap XML                                     │
│     - Extract URLs                                          │
│     - Filter by path_patterns                               │
│     - Filter by content_types                               │
│     - Separate PDFs from web URLs                           │
│  3. Add to all_web_urls and all_pdf_urls                   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  STEP 2: MANUAL_URLS Addition                              │
│                                                             │
│  1. Get manual URLs from MANUAL_URLS[domain]               │
│  2. Filter by subdomain if specified                        │
│  3. Separate PDFs from web URLs                             │
│  4. EXTEND (add to) discovered URLs                        │
│     - all_web_urls.extend(manual_web_urls)                  │
│     - all_pdf_urls.extend(manual_pdf_urls)                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  STEP 3: Return Combined Results                           │
│                                                             │
│  return {                                                    │
│      "web_urls": list(set(all_web_urls)),  # Deduplicated  │
│      "pdf_urls": list(set(all_pdf_urls)),  # Deduplicated  │
│  }                                                          │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Key Points

1. **TRUSTED_DOMAINS runs first**: Automated discovery from sitemaps
2. **MANUAL_URLS adds to results**: Doesn't replace, extends
3. **Deduplication**: Final URLs are deduplicated using `set()`
4. **Fallback**: If TRUSTED_DOMAINS fails, MANUAL_URLS still provides URLs
5. **Combined**: Both sources are combined for comprehensive coverage

---

## 4. Usage in Knowledge Pipeline

### 4.1 Where It's Called

**File**: `data_pipelines/processors/knowledge_pipeline_orchestrator.py:98`

```python
async def run_knowledge_pipeline(self, domain: str, subdomain: str | None = None):
    # ...
    if run_collection:
        # Calls get_discovered_urls which uses BOTH TRUSTED_DOMAINS and MANUAL_URLS
        discovered = await get_discovered_urls(domain, subdomain)
        
        web_urls = discovered.get("web_urls", [])
        pdf_urls = discovered.get("pdf_urls", [])
        
        # Collects from discovered URLs
        raw_articles = await self._collect_from_urls(web_urls, pdf_urls, domain, subdomain)
```

### 4.2 Example: Compliance Domain

**Input**:
- `domain = "compliance"`
- `subdomain = "PCI-DSS"`

**Process**:
1. **TRUSTED_DOMAINS**:
   - Gets `TRUSTED_DOMAINS["compliance"]["tier_1"]`
   - Discovers URLs from `pcisecuritystandards.org` sitemap
   - Filters by `/document_library/` pattern
   - Returns: `{"web_urls": [...], "pdf_urls": [...]}`

2. **MANUAL_URLS**:
   - Gets `MANUAL_URLS["compliance"]["PCI-DSS"]`
   - Adds manual URLs (e.g., third-party sites, specific PDFs)
   - Extends discovered URLs

3. **Result**:
   - Combined list of URLs from both sources
   - Deduplicated
   - Ready for collection

---

## 5. Comparison: TRUSTED_DOMAINS vs MANUAL_URLS

| Aspect | TRUSTED_DOMAINS | MANUAL_URLS |
|--------|----------------|-------------|
| **Purpose** | Automated discovery | Manual fallback/supplement |
| **Source** | Sitemap XML files | Hardcoded URLs |
| **Discovery Mode** | Sitemap, search, crawl | N/A (direct URLs) |
| **Filtering** | Path patterns, content types | None (all URLs included) |
| **When Used** | First (primary discovery) | Second (extends results) |
| **Updates** | Automatic (from sitemaps) | Manual (code changes) |
| **Coverage** | All URLs in sitemap | Specific URLs only |

---

## 6. When to Use Each

### Use TRUSTED_DOMAINS When:
- ✅ Domain has sitemap.xml
- ✅ Want automatic discovery of all URLs
- ✅ URLs follow predictable patterns
- ✅ Want to discover new URLs automatically

### Use MANUAL_URLS When:
- ✅ Domain doesn't have sitemap.xml
- ✅ Need specific URLs not in sitemap
- ✅ Want to include third-party sources
- ✅ Need fallback if sitemap discovery fails
- ✅ Want to supplement discovered URLs

---

## 7. Current Status

### ✅ TRUSTED_DOMAINS: **ACTIVELY USED**

**Evidence**:
- ✅ Imported in `discovery_helper.py:3`
- ✅ Used in `get_discovered_urls()` function (line 24)
- ✅ Called from `knowledge_pipeline_orchestrator.py:98`
- ✅ Processes sitemap discovery for all configured domains

**Domains Configured**:
- Compliance: `pcisecuritystandards.org`, `hhs.gov`, `csrc.nist.gov`, etc.
- FinOps: `aws.amazon.com`, `cloud.google.com`, `azure.microsoft.com`
- Architecture: Cloud provider architecture docs
- Security: `owasp.org`, `cisecurity.org`
- DevOps: `kubernetes.io`, `terraform.io`, `cncf.io`
- Platform: `backstage.io`, `platformengineering.org`
- SRE: `sre.google`, `landing.google.com`

### ✅ MANUAL_URLS: **ACTIVELY USED**

**Evidence**:
- ✅ Imported in `discovery_helper.py:3`
- ✅ Used in `get_discovered_urls()` function (line 43-63)
- ✅ Extends discovered URLs (doesn't replace)
- ✅ Provides fallback if discovery fails

**URLs Configured**:
- Compliance: PCI-DSS, CIS-AWS/GCP/Azure, HIPAA, SOC2, NIST-800-53, ISO-27001, GDPR, FedRAMP, CCPA, SOX, GLBA
- FinOps: AWS/GCP/Azure cost management, optimization guides
- Architecture: Infrastructure design principles, cloud docs
- Security: Cloud security guides
- DevOps: Tool documentation URLs

---

## 8. Example: Complete Flow

### Scenario: Collect PCI-DSS Compliance Data

**Step 1: TRUSTED_DOMAINS Discovery**
```python
# Gets config from TRUSTED_DOMAINS["compliance"]["tier_1"]
domain_config = {
    "domain": "pcisecuritystandards.org",
    "discovery_mode": "sitemap",
    "path_patterns": ["/document_library/"],
    "content_types": ["pdf", "html"],
}

# Discovers URLs from sitemap
discovered = await SourceDiscovery().discover_all_for_domain(domain_config)
# Result: {"web_urls": [100 URLs], "pdf_urls": [20 PDFs]}
```

**Step 2: MANUAL_URLS Addition**
```python
# Gets manual URLs from MANUAL_URLS["compliance"]["PCI-DSS"]
manual_urls = [
    "https://www.pcisecuritystandards.org/document_library/",
    "https://help.drata.com/en/articles/6038558-required-documentation-for-pci-dss",
    "https://documentation.suse.com/compliance/all/pdf/article-security-pcidss_en.pdf",
    # ... more URLs
]

# Separates PDFs from web URLs
manual_pdf_urls = [url for url in manual_urls if url.endswith(".pdf")]
manual_web_urls = [url for url in manual_urls if not url.endswith(".pdf")]

# EXTENDS discovered URLs
all_web_urls.extend(manual_web_urls)  # Adds to discovered web URLs
all_pdf_urls.extend(manual_pdf_urls)  # Adds to discovered PDF URLs
```

**Step 3: Deduplication**
```python
# Removes duplicates
return {
    "web_urls": list(set(all_web_urls)),  # Deduplicated
    "pdf_urls": list(set(all_pdf_urls)),  # Deduplicated
}
```

**Step 4: Collection**
```python
# Knowledge pipeline collects from combined URLs
raw_articles = await self._collect_from_urls(web_urls, pdf_urls, domain, subdomain)
```

---

## 9. Summary

### TRUSTED_DOMAINS
- ✅ **USED**: Yes, actively used for automated sitemap discovery
- ✅ **Purpose**: Discover URLs automatically from sitemaps
- ✅ **Location**: `discovery_helper.py:24-41`
- ✅ **Result**: Provides initial set of URLs

### MANUAL_URLS
- ✅ **USED**: Yes, actively used as fallback/supplement
- ✅ **Purpose**: Add manual URLs to discovered URLs
- ✅ **Location**: `discovery_helper.py:43-63`
- ✅ **Result**: Extends discovered URLs with manual URLs

### How They Work Together
1. **TRUSTED_DOMAINS** discovers URLs from sitemaps
2. **MANUAL_URLS** adds manual URLs to the results
3. **Combined** URLs are deduplicated
4. **Result** is used for collection

**Both are production-ready and actively used!** ✅

