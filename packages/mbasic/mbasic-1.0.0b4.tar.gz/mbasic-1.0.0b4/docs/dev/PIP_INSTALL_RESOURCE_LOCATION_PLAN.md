# Pip Install Resource Location Plan

## Problem
Current code uses hardcoded relative paths like `Path(__file__).parent.parent.parent / "docs" / "help"` which only work in development (running from source directory). After `pip install`, docs will be in site-packages and these paths break.

## Solution Implemented

### 1. Created `src/resource_locator.py`
New module that finds resources in both dev and installed environments:
- `find_docs_dir()` - Finds docs/ directory
- `find_help_dir()` - Finds docs/help/ directory
- `find_library_dir()` - Finds docs/library/ directory
- `find_basic_dir()` - Finds basic/ directory (dev only)

**Strategy (tries in order):**
1. Development mode: Look relative to `__file__` (../../docs from src/)
2. Python 3.9+: Use `importlib.resources.files('mbasic').joinpath('docs')`
3. Fallback: Use `pkg_resources.resource_filename('mbasic', 'docs')`
4. System locations: Check /usr/share/mbasic/docs, /usr/local/share/mbasic/docs, etc.

### 2. Updated `pyproject.toml`
Added package_data configuration to include docs in distribution:
```toml
[tool.setuptools.package-data]
"mbasic" = [
    "docs/**/*.md",
    "docs/**/*.json",
    "basic/**/*.bas",
    "basic/**/*.BAS",
    "basic/**/*.txt",
]
```

### 3. Updated `MANIFEST.in`
Already includes:
```
recursive-include docs *.md
recursive-include basic *.bas *.BAS *.txt
```

### 4. Updated UI Code
**Curses UI** (`src/ui/curses_ui.py`):
- Changed `_show_help()` to use `find_help_dir()` instead of hardcoded path
- Added error handling if docs not found

## Files Modified
- ✅ `src/resource_locator.py` - NEW: Resource finder module
- ✅ `pyproject.toml` - Updated package_data configuration
- ✅ `src/ui/curses_ui.py` - Use find_help_dir()

## Files Still TODO
- `src/ui/web_help_launcher.py` - Update if needed (currently uses web server)
- `src/ui/tk_ui.py` - Uses web_help_launcher, may need updating
- `src/ui/web/nicegui_backend.py` - Check if it loads docs directly

## Testing Plan

### Test in Development (Current)
```bash
python3 mbasic  # Launch curses UI
# Press ^F for help - should work as before
```

### Test After Pip Install
```bash
# Create virtual environment
python3 -m venv /tmp/test-mbasic-venv
source /tmp/test-mbasic-venv/bin/activate

# Build and install
python3 -m build
pip install dist/mbasic-*.whl

# Test
mbasic  # Should launch and ^F help should work

# Check where docs landed
python3 -c "from src.resource_locator import find_help_dir; print(find_help_dir())"
```

### Test System Install
```bash
sudo pip install dist/mbasic-*.whl
mbasic  # Should find docs in /usr/local or /usr/share
```

## Where Docs Will Install

**Typical pip install locations:**
- User install: `~/.local/lib/python3.x/site-packages/mbasic/docs/`
- Venv install: `venv/lib/python3.x/site-packages/mbasic/docs/`
- System install: `/usr/local/lib/python3.x/site-packages/mbasic/docs/`

**Alternative (if we use data_files in setup.py):**
- System: `/usr/share/mbasic/docs/`
- Local: `/usr/local/share/mbasic/docs/`

Current approach uses package_data (keeps docs with Python package), which is simpler and more portable.

## Next Steps
1. Test current changes work in dev (^F help still works)
2. Run `python3 -m build` to create wheel
3. Test install in venv
4. Update remaining UI backends if needed
5. Document for users

## Notes
- `basic/` directory is development-only, not distributed (test programs)
- `docs/help/` is the in-app help system (distributed)
- `docs/library/` is the games/demos catalog (distributed)
- `docs/dev/` and `docs/history/` are developer docs (could exclude from distribution)

## Library Browser Addition (Future)
User wants to add library browser to curses help menu (like tk has). Plan:
- Add menu option in curses UI
- Could open lynx browser pointed at docs/library/index.md
- Or create native urwid library browser widget
