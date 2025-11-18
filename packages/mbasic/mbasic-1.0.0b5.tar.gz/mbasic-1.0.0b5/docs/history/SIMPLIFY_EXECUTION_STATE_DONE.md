# TODO: Simplify Execution State - Remove Mode Complexity

## Problem
Currently the interpreter/runtime has too many overlapping state concepts:
- `status`: 'idle', 'running', 'paused', 'at_breakpoint', 'done', 'error', 'waiting_for_input'
- `runtime.halted`: Boolean flag
- `self.running`: UI flag
- `self.paused_at_breakpoint`: Another UI flag

This is confusing and causes bugs (e.g., stepping not working after loading a file because status is 'done').

## User's Vision: "Like a Microprocessor"
A microprocessor has:
1. **PC (Program Counter)** - where we are
2. **Halt flag** - are we stopped?

That's it. Simple.

## Proposed Simplification

### Runtime State (src/runtime.py)
Keep only:
- `self.pc` - Program counter (line, stmt_offset)
- `self.halted` - Boolean: True if stopped (for ANY reason)

Remove or collapse:
- All the 'status' values in InterpreterState
- Separate 'paused' vs 'at_breakpoint' vs 'done' states

### Why We Halted (Display Only)
The UI can determine WHY we halted by checking:
- `if runtime.halted and pc.line_num in breakpoints` → "Stopped at breakpoint"
- `if runtime.halted and pc.is_valid()` → "Paused at line X"
- `if runtime.halted and not pc.is_valid()` → "Program completed"
- Check for error_info if present → "Error at line X"

### Questions to Answer
1. **Do we need 'paused' vs 'at_breakpoint' to be different?**
   - No. Just check if current line has a breakpoint when displaying status.

2. **Do we need 'running' flag?**
   - Only for UI display (spinner/status). Not for execution logic.

3. **What about 'waiting_for_input'?**
   - This might need to stay separate since it's a blocking state. Or make it a separate flag like `waiting_for_input` boolean.

4. **What about 'error'?**
   - Set `halted = True` and populate `error_info`. UI checks for error_info to display error.

## Implementation Steps
1. Remove status mode checks from stepping logic (DONE in v1.0.451)
2. Audit all uses of `state.status` in UI code
3. Replace with checks on `runtime.halted` and other simple flags
4. Simplify interpreter's state management
5. Update tests

## Benefits
- Simpler logic, fewer bugs
- Stepping "just works" - clear halted flag and go
- More like real hardware/microprocessor
- Easier to understand and maintain

## Files to Change
- `src/interpreter.py` - Remove complex status states
- `src/runtime.py` - Already has halted flag, just use it consistently
- `src/ui/curses_ui.py` - Replace status checks with halted checks
- `src/ui/web/nicegui_backend.py` - Same for web UI
- Tests that check status values

## Notes
- 'running' flag can stay in UI for display purposes only
- Interpreter shouldn't care about "running" - it just executes when told to tick()
- PC and halted flag is all the core needs
