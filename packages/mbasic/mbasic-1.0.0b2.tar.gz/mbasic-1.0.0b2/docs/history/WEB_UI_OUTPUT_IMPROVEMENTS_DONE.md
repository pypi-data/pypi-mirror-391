# Web UI Output Area Improvements

## Status: ⏳ TODO

## Issues

### 1. Output Should Auto-Scroll to Bottom
**Status:** ✅ DONE (v1.0.187)
**Priority:** HIGH

**Problem:** When program produces output, the output textarea doesn't automatically scroll to show the latest output. User has to manually scroll down.

**Solution Implemented:**
- Use `ui.run_javascript()` with setTimeout to scroll after DOM updates
- Find output textarea by checking for readonly + "MBASIC 5.21" content
- Call `self.output.update()` before scrolling to force UI update
- 50ms timeout ensures DOM is updated before scrolling

**Implementation:**
```python
def _append_output(self, text):
    """Append text to output pane and auto-scroll to bottom."""
    self.output.value += text
    # Force update and then scroll
    self.output.update()
    # Auto-scroll to bottom
    ui.run_javascript('''
        setTimeout(() => {
            const textareas = document.querySelectorAll('textarea');
            for (let ta of textareas) {
                if (ta.readOnly && ta.value.includes('MBASIC 5.21')) {
                    ta.scrollTop = ta.scrollHeight;
                    break;
                }
            }
        }, 50);
    ''')
```

**Files Modified:**
- `src/ui/web/nicegui_backend.py` - `_append_output()` method (line 488)

---

### 2. Output Buffer Limiting
**Status:** ✅ DONE (v1.0.300)
**Priority:** MEDIUM

**Problem:** Output area can grow indefinitely, causing browser memory issues and slow performance with long-running programs.

**Solution:**
- Keep only last N lines in output buffer (configurable)
- Default: 2000-3000 lines
- When buffer exceeds limit, remove oldest lines
- Store in settings/config

**Implementation:**
```python
class NiceGUIBackend:
    def __init__(self, ...):
        self.output_max_lines = 3000  # Default, should come from config

    def _append_output(self, text):
        """Append text to output pane with buffer limiting."""
        self.output.value += text

        # Limit buffer size
        lines = self.output.value.split('\n')
        if len(lines) > self.output_max_lines:
            # Keep last N lines
            lines = lines[-self.output_max_lines:]
            self.output.value = '\n'.join(lines)
            # Optionally show indicator that old output was trimmed
            if not self.output.value.startswith('[... output truncated ...]\n'):
                self.output.value = '[... output truncated ...]\n' + self.output.value

        # Auto-scroll to bottom
        # ...
```

**Configuration:**
- Add to Settings dialog (when implemented)
- Setting: "Output Buffer Lines" (default: 3000)
- Minimum: 100
- Maximum: 10000

**Implementation Complete:**
- Added `self.output_max_lines = 3000` in `__init__()` (line 152)
- Updated `_append_output()` to use line-based limiting (lines 979-988)
- Changed from character-based (10,000 chars) to line-based (3,000 lines)
- Adds "[... output truncated ...]" indicator when buffer is trimmed
- More predictable behavior for users

**Files Modified:**
- `src/ui/web/nicegui_backend.py` - Updated `__init__()` and `_append_output()`

**Future Enhancement:**
- Add to Settings dialog when implemented (configurable max_lines)

---

### 3. Log Errors to stderr
**Status:** ✅ DONE (v1.0.184)
**Priority:** HIGH

**Problem:** Errors in the web UI are only shown in the browser, not logged to terminal/stderr. Makes debugging difficult when user reports issues.

**Solution Implemented:**
- Created `log_web_error()` helper function
- Wraps all menu handlers and critical methods with try/except
- Logs exceptions to stderr with full traceback
- Still shows error in web UI via ui.notify()

**Implementation:**
```python
def log_web_error(context: str, exception: Exception):
    """Log web UI error to stderr for debugging."""
    sys.stderr.write(f"\n{'='*70}\n")
    sys.stderr.write(f"WEB UI ERROR in {context}\n")
    sys.stderr.write(f"{'='*70}\n")
    sys.stderr.write(f"Error: {exception}\n")
    sys.stderr.write(f"{'-'*70}\n")
    traceback.print_exc(file=sys.stderr)
    sys.stderr.write(f"{'='*70}\n\n")
    sys.stderr.flush()

# Used in all handlers:
try:
    # ... handler code ...
except Exception as e:
    log_web_error("_menu_run", e)
    ui.notify(f'Error: {e}', type='negative')
    self._set_status(f'Error: {e}')
```

**Files Modified:**
- `src/ui/web/nicegui_backend.py` - Added log_web_error() and wrapped all handlers

---

### 4. Better Web Browser Emulator for Testing
**Status:** ✅ DONE (v1.0.185)
**Priority:** MEDIUM

**Problem:** Current testing uses NiceGUI's `user` fixture which has limitations (async deadlock with INPUT). Need better web testing that allows full browser simulation.

**Solution Implemented:**
- Chose **Playwright** for browser automation
- Created comprehensive test suite with 9 tests
- Tests cover: UI loading, line entry, program execution, INPUT, clear output, new program, error handling
- Uses real Chromium browser for accurate testing

**Implementation:**
- Installed: `playwright>=1.40.0`, `pytest-playwright>=0.4.0`
- Created `tests/playwright/test_web_ui.py` with full test suite
- Created `tests/playwright/conftest.py` for browser configuration
- Tests start real web server on localhost:8080 with proper cleanup

**Test Coverage:**
1. `test_ui_loads` - UI initialization
2. `test_add_single_line` - Single line entry
3. `test_add_multiple_lines` - Multi-line paste
4. `test_run_simple_program` - Program execution
5. `test_input_statement` - INPUT with inline field (skips if not ready)
6. `test_clear_output` - Clear output button
7. `test_new_program` - File > New
8. `test_error_handling` - Syntax error display

**Files Created:**
- `tests/playwright/test_web_ui.py` - Full test suite
- `tests/playwright/conftest.py` - Browser config
- Updated `requirements.txt` with Playwright dependencies

**How to Run:**
```bash
source venv-nicegui/bin/activate
pytest tests/playwright/test_web_ui.py -v
```

---

## Summary

### Completed Tasks (4/4) ✅
1. ✅ **HIGH:** Auto-scroll output to bottom (v1.0.187)
2. ✅ **HIGH:** Log errors to stderr (v1.0.184)
3. ✅ **MEDIUM:** Playwright testing framework (v1.0.185)
4. ✅ **MEDIUM:** Output buffer limiting (v1.0.300)

### Overall Status
**ALL TASKS COMPLETE** ✅ - Web UI output improvements fully implemented.

---

## Related Files
- `src/ui/web/nicegui_backend.py` - Main implementation
- `tests/nicegui/test_mbasic_web_ui.py` - Current tests
- `docs/dev/WEB_UI_MISSING_FEATURES.md` - Feature parity tracking
