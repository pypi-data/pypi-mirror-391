# Redis Storage Bug Fixes

## Bug #1: Editor/Program Manager Sync

**Reported by user**: When testing Redis storage with two browsers:
1. Browser A: Enter program and run it ✅
2. Browser B: Enter different program and run it ✅
3. Browser A: Go back - program shows on screen but RUN/LIST see empty program ❌

## Root Cause

The bug occurred because **editor content** and **program manager** were being serialized separately without synchronization:

1. User types program in editor (e.g., `10 PRINT "HELLO"`)
2. Periodic save (every 5 seconds) triggers
3. Serialization saves:
   - ✅ `editor_content`: `"10 PRINT \"HELLO\""`
   - ❌ `program_lines`: `{}` (empty - program not run yet)
4. When restored:
   - ✅ Editor displays the program text
   - ❌ Program manager is empty (RUN/LIST see nothing)

### Why It Happened

In the web UI, the program manager is only populated when:
- User runs the program
- User loads a file
- User enters immediate mode commands that modify program

Simply typing in the editor does NOT automatically update the program manager. So if the user:
1. Typed a program
2. Ran it (program manager populated)
3. Edited it further (program manager still has old version)
4. State saved (saves edited editor content but old program manager)
5. Restored (editor shows new edits, program manager has old version)

## Fix

Added `_sync_program_from_editor()` method that is called **before serialization**:

```python
def serialize_state(self) -> dict:
    # Sync program manager from editor content before serializing
    # This ensures we capture any edits that haven't been run yet
    self._sync_program_from_editor()

    # ... rest of serialization
```

### Implementation (nicegui_backend.py:3311)

```python
def _sync_program_from_editor(self) -> None:
    """Sync program manager from editor content.

    This ensures the program manager reflects the current editor content,
    even if the user hasn't run the program yet. Important for serialization.
    """
    if not self.editor:
        return  # No editor yet

    try:
        # Get current editor content
        editor_content = self.editor.value or ""

        # Clear existing program
        self.program.clear()

        # Parse each line from editor
        for line in editor_content.split('\n'):
            line = line.strip()
            if not line:
                continue  # Skip blank lines

            # Try to parse as a numbered line (e.g., "10 PRINT")
            import re
            match = re.match(r'^(\d+)\s+(.*)$', line)
            if match:
                line_num = int(match.group(1))
                rest = match.group(2).strip()
                if rest:  # Only add if there's content after line number
                    self.program.add_or_replace_line(line_num, line)
    except Exception as e:
        # If sync fails, log but don't crash - we'll serialize what we have
        sys.stderr.write(f"Warning: Failed to sync program from editor: {e}\n")
        sys.stderr.flush()
```

## Testing

### Before Fix

```
1. Browser A: Type "10 PRINT 'A'" and run → Works
2. Browser B: Type "10 PRINT 'B'" and run → Works
3. Browser A: Refresh → Editor shows "10 PRINT 'A'" but RUN shows nothing
```

### After Fix

```
1. Browser A: Type "10 PRINT 'A'" and run → Works
2. Browser B: Type "10 PRINT 'B'" and run → Works
3. Browser A: Refresh → Editor shows "10 PRINT 'A'" AND RUN executes it ✅
```

## Additional Benefits

This fix also ensures that:
- Unsaved program edits are captured when switching sessions
- Program state is always consistent between editor and program manager
- Manual testing is more reliable (no need to run before switching browsers)

## Bug #2: Tuple Unpacking Error in _serialize_program()

**Reported by user**: Console shows repeated error:
```
Warning: Failed to save session state: 'tuple' object has no attribute 'text'
```

### Root Cause

The `_serialize_program()` method was treating the return value of `self.program.get_lines()` as objects with `.line_number` and `.text` attributes:

```python
for line in self.program.get_lines():
    result[line.line_number] = line.text  # ERROR: line is a tuple!
```

But `ProgramManager.get_lines()` actually returns `List[Tuple[int, str]]` where each tuple is `(line_number, line_text)`.

### Fix

Changed to properly unpack the tuples:

```python
def _serialize_program(self) -> Dict[int, str]:
    result = {}
    # get_lines() returns List[Tuple[int, str]]
    for line_number, line_text in self.program.get_lines():
        result[line_number] = line_text
    return result
```

### Testing

**Before**: Console flooded with warnings every 5 seconds
**After**: No warnings, serialization works correctly

## Files Modified

- `src/ui/web/nicegui_backend.py`
  - Bug #1: Added `_sync_program_from_editor()` method (line 3311)
  - Bug #1: Modified `serialize_state()` to call sync before serializing (line 3240)
  - Bug #2: Fixed `_serialize_program()` to unpack tuples correctly (line 3355)

## Related Documentation

- Session Storage Audit: `docs/dev/SESSION_STORAGE_AUDIT.md`
- Storage Design: `docs/dev/STORAGE_ABSTRACTION_DESIGN.md`
- Setup Guide: `docs/dev/REDIS_SESSION_STORAGE_SETUP.md`
