# PyPI Distribution - Deferred Project

**Status:** ⏸️ Deferred
**Last Updated:** 2025-10-28
**Version Ready:** 1.0.151

## Summary

Package is fully prepared and ready for PyPI publication, but deferred by user request.

## Current State

✅ **Package completely ready:**
- Version: 1.0.151
- Zero dependencies for core functionality
- Optional dependencies for curses/tk UIs
- Entry point: `mbasic` command
- Includes docs, help files, and example programs
- Build script: `./utils/build_package.sh`
- All tests passing

## Documentation Available

See `docs/future/DISTRIBUTION_TESTING.md` for:
- Complete build instructions
- Testing procedures
- Publishing workflow
- Pre-publication checklist
- Emergency procedures

## When to Resume

Resume this project when:
1. User explicitly requests PyPI publication
2. Ready to make MBASIC installable via `pip install mbasic`
3. Comfortable with public package distribution

## Build and Test

```bash
# Build package
./utils/build_package.sh

# Test locally
./utils/build_package.sh --test

# Test on TestPyPI (optional)
./utils/build_package.sh --test-pypi

# Publish to PyPI (REQUIRES APPROVAL)
python3 -m twine upload dist/*
```

## Why Deferred

User chose to defer PyPI distribution to focus on other features. Publishing to PyPI is:
- Irreversible (can't unpublish)
- Makes package public and discoverable
- Requires ongoing maintenance commitment

## Related Files

- `pyproject.toml` - Package configuration (v1.0.151)
- `MANIFEST.in` - Package file inclusion rules
- `utils/build_package.sh` - Automated build script
- `docs/future/DISTRIBUTION_TESTING.md` - Complete publishing guide
- `docs/future/SIMPLE_DISTRIBUTION_APPROACH.md` - Distribution approach notes
