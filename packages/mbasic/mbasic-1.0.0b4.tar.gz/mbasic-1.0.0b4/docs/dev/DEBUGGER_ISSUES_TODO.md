# Debugger Issues TODO

## Fixed Issues

### 1. STEP command jumps to wrong line after breakpoint ✅
**Status**: FIXED in src/interpreter.py:317-321
**Fix**: Auto-resume PC when in step mode if stopped at BREAK/USER
- When stepping after a breakpoint, PC is now automatically resumed
- Works in both web UI and curses UI

### 2. INPUT statements not highlighted/indicated ✅
**Status**: FIXED in src/ui/web/nicegui_backend.py
**Fix**: Added highlighting and status display at three locations (lines 2090, 2135, 2365)
- INPUT statements now highlighted in CodeMirror editor
- Status shows: "at line 2065: COMMAND?" (line number + prompt)
- Current line label shows: ">>> INPUT at line 2065"

### 3. Breakpoints detected but program ends instead of pausing ✅
**Status**: FIXED in src/pc.py:102-117 (v873)
**Root Cause**: PC is frozen dataclass with default __eq__ that compared all fields
- When breakpoint hits, `pc.stop("BREAK")` creates new PC with stop_reason="BREAK"
- `statement_table.get(stopped_pc)` failed because default equality includes stop_reason
- `__hash__` included stop_reason, violating hash/equality contract when comparing by position only
**Fix**: Added custom `__eq__` and `__hash__` methods to PC class
- Both now only compare/hash position (line, statement), not state (stop_reason, error)
- This allows PC lookups in statement_table and breakpoints to work correctly regardless of PC state
- Line-level breakpoint detection also fixed in interpreter.py:352-355 (v871)
- Changed from `pc.line_num in self.runtime.breakpoints` to loop checking `bp.line == pc.line_num`

### 4. Curses UI breakpoint crash: 'int' object has no attribute 'line' ✅
**Status**: FIXED in src/runtime.py:1442,1466 (v875)
**Root Cause**: Curses UI passed line numbers as integers to set_breakpoint(), but breakpoint checking code expected PC objects
- Curses UI: `set_breakpoint(line_num)` added raw integer to breakpoints set
- interpreter.py:353 tried to access `bp.line` on all breakpoints, failed on integers
**Fix**: Modified set_breakpoint and clear_breakpoint to always create PC objects
- Line-level breakpoints now stored as `PC(line_num, 0)` instead of raw integers
- Ensures all breakpoints are PC objects with .line attribute

### 5. Curses UI: STEP shows "Paused at None" after breakpoint ✅
**Status**: FIXED in src/ui/curses_ui.py:3612-3616 (v876)
**Root Cause**: Used `state.current_line` which is None at breakpoints
**Fix**: Changed to use `runtime.pc.line` instead (same as web UI fix in v874)
- Added comment explaining state.current_line may be None at breakpoint
- Status bar and output now show correct line number when paused

### 6. Curses UI: ^U menu scrolls program to top ✅
**Status**: FIXED in src/ui/interactive_menu.py:160-167 (v877)
**Root Cause**: Wrapping base widget in new AttrMap on every menu open caused urwid to lose editor scroll position
- `_show_dropdown()` created `urwid.AttrMap(base_widget, 'body')` every time
- New widget wrapper caused urwid to re-render from scratch, resetting scroll
**Fix**: Pass base_widget directly to Overlay without wrapping
- Removed `base_with_bg = urwid.AttrMap(base_widget, 'body')` line
- Pass base_widget directly to preserve widget state
- Dropdown still wrapped in AttrMap for correct colors

## Outstanding Issues

None - all debugger issues resolved!

## Investigation Notes

- Line 30 in Super Star Trek is just a REM statement
- Line 2060 has: `INPUT"COMMAND";A$`
- Line 2065 has: `ZZ$=A$:gosub 9450:a$=zz$`
- Breakpoint/step issue suggests PC is being reset incorrectly when stepping

## Files to Check

- `src/interpreter.py` - Step command implementation
- `src/ui/web/nicegui_backend.py` - Web UI debugger
- `src/ui/curses_ui.py` - Curses UI debugger
- `src/pc.py` - Program Counter logic
