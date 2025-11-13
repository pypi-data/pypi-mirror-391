# Fix MkDocs Strict Mode Errors

⏳ **Status:** TODO - HIGH PRIORITY

## Problem

The MkDocs build fails in `--strict` mode with errors, causing the GitHub Actions workflow to fail and send 150+ notification emails.

**Current Status:**
- Auto-deployment disabled temporarily (commit d8388ba)
- Build runs: `mkdocs build --strict --verbose`
- Strict mode treats warnings as errors
- Unknown number of failures (log shows "31 failures" but details not captured)

## Background

The documentation deployment workflow (`.github/workflows/docs.yml`) is configured to:
1. Run on every push to `main` that touches `docs/**`, `mkdocs.yml`, or the workflow file
2. Build with `mkdocs build --strict --verbose`
3. Deploy to GitHub Pages

The `--strict` flag causes the build to fail on any warnings, which is good for quality but requires all warnings to be fixed first.

## Investigation Needed

**Step 1: Reproduce locally**
```bash
# Install dependencies
pip install mkdocs mkdocs-material mkdocs-awesome-pages-plugin python-frontmatter

# Build with strict mode to see errors
mkdocs build --strict --verbose 2>&1 | tee mkdocs_errors.txt

# Or just see warnings without failing
mkdocs build --verbose 2>&1 | tee mkdocs_warnings.txt
```

**Step 2: Identify error types**

Common MkDocs strict mode errors:
- Missing files referenced in nav or links
- Invalid markdown syntax
- Broken internal links
- Missing front matter
- Invalid YAML in front matter
- Duplicate page titles
- Files not in navigation

**Step 3: Count and categorize**

From the error log, identify:
- How many errors total?
- What types of errors?
- Which files are affected?
- Are they in help docs or dev docs?

## Likely Issues

Based on the project structure:

1. **Dev docs not in navigation** - Files like `*_TODO.md`, `*_DONE.md` may not be in `mkdocs.yml` nav
2. **Help files structure** - Large number of statement docs in `docs/help/common/language/statements/`
3. **Broken links** - Internal links that reference moved/renamed files
4. **Missing front matter** - Some markdown files may lack required YAML front matter

## Solution Options

### Option A: Fix All Errors (RECOMMENDED)

**Pros:**
- Clean, high-quality documentation
- Strict mode catches future issues
- Professional documentation site

**Cons:**
- Time-consuming to fix all errors
- May require restructuring

**Steps:**
1. Run `mkdocs build --strict --verbose` locally
2. Fix errors one by one
3. Re-test until build succeeds
4. Re-enable auto-deployment

### Option B: Remove --strict Flag

**Pros:**
- Quick fix - deployment works immediately
- Warnings don't block deployment

**Cons:**
- Lower quality - warnings ignored
- Issues accumulate over time
- Unprofessional

**Implementation:**
```yaml
# In .github/workflows/docs.yml
- name: Build documentation
  run: mkdocs build --verbose  # Remove --strict
```

### Option C: Exclude Problem Files

**Pros:**
- Deploys documentation that works
- Can fix errors incrementally

**Cons:**
- Incomplete documentation site
- Requires maintaining exclusion list

**Implementation:**
Add to `mkdocs.yml`:
```yaml
exclude_docs: |
  dev/*_TODO.md
  dev/*_DONE.md
```

## Recommended Approach

**Phase 1: Quick diagnosis**
1. Install mkdocs locally
2. Run strict build to see all errors
3. Document error types and counts

**Phase 2: Triage**
1. Separate critical errors from minor ones
2. Decide which docs should be published (help vs dev)
3. Create exclusion list if needed

**Phase 3: Fix**
1. Fix critical errors first (broken help docs)
2. Fix dev docs or exclude them
3. Re-enable auto-deployment

**Phase 4: Maintain**
1. Keep strict mode enabled
2. Fix warnings before committing doc changes
3. Add CI check for doc quality

## Files to Check

**Workflow:**
- `.github/workflows/docs.yml` - Deployment configuration

**Configuration:**
- `mkdocs.yml` - Site configuration, navigation, plugins

**Documentation:**
- `docs/help/common/language/statements/*.md` - Help documentation (100+ files)
- `docs/dev/*_TODO.md` - Development todos
- `docs/dev/*_DONE.md` - Completed work history
- `docs/user/*.md` - User documentation

## Priority

**HIGH** - Currently generating hundreds of failure emails and blocking documentation deployment.

## Dependencies

- mkdocs >= 1.5.0
- mkdocs-material >= 9.0.0
- mkdocs-awesome-pages-plugin >= 2.8.0
- python-frontmatter >= 1.0.0

## Testing

After fixes:
```bash
# Test locally
mkdocs build --strict --verbose

# Preview site
mkdocs serve

# Check specific page
# Open http://127.0.0.1:8000/ in browser
```

## Rollout

1. Fix errors locally
2. Commit fixes
3. Re-enable auto-deployment in `.github/workflows/docs.yml`
4. Push to main
5. Verify GitHub Actions succeeds
6. Check deployed site at GitHub Pages URL

## Notes

- Documentation uses Material for MkDocs theme
- Awesome Pages plugin for auto-navigation
- Front matter plugin for YAML metadata
- See `requirements.txt` for exact versions
