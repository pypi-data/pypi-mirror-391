# Work In Progress: CHAIN and Error Handling Fixes

**Date**: 2025-11-04
**Version**: 1.0.638 → 1.0.640

## Current Status: COMPLETE ✅

## Issues Fixed

### 1. CHAIN Acting Like GOSUB (Preserving Call Stack) ✅ FIXED!
**Status**: Complete (v1.0.640)

**Problem**: CHAIN was building up GOSUB/RETURN stack with each chain, causing "maximum recursion depth exceeded" after ~160 iterations between chain1.bas and chain2.bas.

**Root cause**: `cmd_chain()` in `src/interactive.py:726-747` was creating NEW Runtime and Interpreter objects with each CHAIN, then calling `interpreter.run()` which created nested recursion. The old call stack was preserved somewhere in this nesting.

**Solution (v1.0.640)**:
- Modified CHAIN to REUSE existing Runtime/Interpreter objects instead of creating new ones
- Calls `runtime.reset_for_run(self.line_asts, self.lines)` which properly clears execution_stack (GOSUB stack), FOR loops, DATA pointer, files, etc.
- Returns to let existing `interpreter.run()` continue instead of calling it again (prevents recursion)
- Only creates new objects on first RUN, reuses them for all subsequent CHAINs
- This preserves UI references to Runtime/Interpreter which would break if new objects were created

### 2. Errors Not Stopping Execution ✅ FIXED!
**Status**: Complete (v1.0.640)

**Problem**: Syntax errors during program parsing (like "maximum recursion depth exceeded") were printed but execution continued.

**Root cause**: The recursion depth error was caused by bug #1 (nested interpreter.run() calls). Once that's fixed, normal error handling in interpreter.py:360-384 will work properly - it sets `runtime.halted = True` and raises the exception.

**Solution (v1.0.640)**: Fixed by solving bug #1. CHAIN no longer creates nested interpreter.run() calls, so errors will properly halt execution via the existing error handling code.

## Files Modified

**src/interactive.py lines 724-778** - Modified cmd_chain():
- Added logic to reuse existing Runtime/Interpreter objects
- Calls reset_for_run() to clear stacks
- Returns instead of calling interpreter.run() again
- Falls back to creating new objects only on first run

**src/version.py** - Updated to 1.0.640
**pyproject.toml** - Updated to 1.0.640

## Testing

Test files: `basic/dev/tests/chain1.bas` and `chain2.bas`
- chain1 calls chain2 with ALL (pass variables)
- chain2 calls chain1 with ALL
- Should alternate forever without stack buildup
- Any errors should halt execution immediately

## Important Note

Creating new Runtime/Interpreter objects during CHAIN would break UI references. UIs (web, curses, tk) hold pointers to these objects and expect them to remain stable. The fix ensures object identity is preserved.

## Related TODO

Added todo: "Audit ALL Runtime/Interpreter creation across all .py files" - need to verify no other code paths create new objects that should reuse existing ones.
