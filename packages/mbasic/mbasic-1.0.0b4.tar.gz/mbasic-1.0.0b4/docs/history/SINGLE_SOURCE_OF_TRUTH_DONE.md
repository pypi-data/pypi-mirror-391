# Single Source of Truth for Program Data

⏳ **Status:** TODO

## Problem

Currently, the TK UI maintains the program in TWO places:

1. **Editor Text Widget** (`self.editor_text.text`) - User-visible text
2. **Program Object** (`self.program`) - Parser's AST representation

This duplication causes sync issues:

### Sync Problems

**Issue 1: Invisible errors**
- If editor text has `10 PRINT X`
- But program object has `10 PRINT Y` (due to bug)
- User sees X in editor, but program runs Y
- Bug is invisible until runtime

**Issue 2: Constant sync operations**
- Every edit requires `_save_editor_to_program()`
- Every program change requires `_refresh_editor()`
- Easy to forget one direction, causing desync

**Issue 3: State confusion**
- Which is the "real" version?
- What if save fails but editor changed?
- What if refresh fails but program changed?

### Current Sync Points

**Editor → Program:**
- `_save_editor_to_program()` - Parse editor text, update program object
- Called before RUN, LIST, SAVE, etc.
- Can fail silently if parse errors

**Program → Editor:**
- `_refresh_editor()` - Serialize program object, update editor text
- Called after LOAD, RENUM, NEW, etc.
- Loses cursor position, undo history

## Root Cause

**Premature optimization**: Keeping parsed AST in memory to avoid re-parsing.

**Reality**: Parsing is FAST (modern CPUs parse thousands of lines per second). The convenience of a single source of truth outweighs the parsing cost.

## Proposed Solution

### Option A: Program Object as Single Source (RECOMMENDED)

**Editor becomes a VIEW of the program object:**

1. **Reading**: Generate editor text from program object on-demand
2. **Writing**: Parse editor changes immediately into program object
3. **No duplication**: Only program object stores the "truth"

```python
class TkBackend:
    def __init__(self):
        self.program = Program()  # Single source of truth
        # No self.editor_text caching

    def _get_editor_content(self):
        """Generate editor text from program object"""
        lines = []
        for line_num in sorted(self.program.lines.keys()):
            line_node = self.program.lines[line_num]
            source = serialize_line(line_node)
            lines.append(source)
        return '\n'.join(lines)

    def _refresh_editor(self):
        """Regenerate editor from program"""
        content = self._get_editor_content()
        self.editor_text.text.delete('1.0', 'end')
        self.editor_text.text.insert('1.0', content)

    def _on_line_change(self, line_index):
        """User edited a line - parse it into program"""
        line_text = self.editor_text.text.get(f'{line_index}.0', f'{line_index}.end')

        # Parse and update program object immediately
        try:
            success, error = self.program.add_line_from_text(line_text)
            if not success:
                # Show error, but keep line in editor for fixing
                self._show_error(error)
        except ParseError as e:
            self._show_error(f"Parse error: {e}")
```

**Pros:**
- Program object is always correct (it's the only copy)
- RUN/SAVE/etc. work directly from program object
- Parser validates immediately, no silent errors
- Serialization tested constantly (every refresh)

**Cons:**
- Need to regenerate editor text more often
- May impact performance for very large programs (>10000 lines)
- Cursor position management becomes more complex

### Option B: Editor Text as Single Source

**Program object generated on-demand when needed:**

1. **Reading**: Parse editor text when RUN/SAVE/etc.
2. **Writing**: Modify editor text directly
3. **No duplication**: Only editor text stores the "truth"

```python
class TkBackend:
    def __init__(self):
        # No self.program cached
        pass

    def _get_program(self):
        """Parse editor text into program object"""
        program = Program()
        editor_content = self.editor_text.text.get('1.0', 'end')

        for line in editor_content.split('\n'):
            line = line.strip()
            if line:
                success, error = program.add_line_from_text(line)
                if not success:
                    raise ParseError(error)

        return program

    def cmd_run(self):
        """Parse editor, then run"""
        try:
            program = self._get_program()
            # Run the program
            self._execute_program(program)
        except ParseError as e:
            self._show_error(f"Parse error: {e}")
```

**Pros:**
- Editor text is what user sees (no hidden state)
- Auto-numbering works directly on text
- Undo/redo works naturally
- Cursor position preserved

**Cons:**
- Parse entire program every time (RUN, SAVE, etc.)
- Errors only found when command runs
- Can't validate incrementally
- RENUM requires parsing, modifying AST, serializing back

## Recommended Approach

**Option A (Program Object as Truth)** because:

1. **Validation**: Parser runs on every change, catching errors early
2. **Correctness**: What you run is what's in the AST (no surprises)
3. **Operations**: RENUM, SAVE, RUN work directly on AST
4. **Performance**: Modern computers parse thousands of lines instantly

### Implementation Strategy

**Phase 1: Eliminate `_save_editor_to_program()` calls**
- Parse lines immediately on change
- Use text widget events: `<<Modified>>`
- Update program object incrementally (only changed lines)

**Phase 2: Make `_refresh_editor()` fast**
- Only regenerate changed lines
- Preserve cursor position
- Preserve undo history if possible

**Phase 3: Remove editor → program sync**
- Remove `_save_editor_to_program()` method
- All changes go through event handlers
- Program object is always current

## Current Architecture

```
┌─────────────────┐         ┌─────────────────┐
│  Editor Text    │ ◄─────► │ Program Object  │
│  (user types)   │  sync   │   (AST/parsed)  │
└─────────────────┘         └─────────────────┘
        │                            │
        │ _save_editor_to_program() │
        └──────────────►│            │
                        │            │
        ┌───────────────┘            │
        │ _refresh_editor()          │
        ◄────────────────────────────┘
```

**Problems:**
- Bidirectional sync is complex
- Easy to forget sync call
- Desync causes invisible bugs

## Proposed Architecture

```
┌─────────────────┐
│ Program Object  │  ◄──── Single Source of Truth
│   (AST/parsed)  │
└─────────────────┘
        │
        │ serialize (on-demand)
        ▼
┌─────────────────┐
│  Editor Text    │  ◄──── View (regenerated as needed)
│  (user types)   │
└─────────────────┘
        │
        │ parse (immediate)
        │
        └────────────►  Updates program object
```

**Benefits:**
- Unidirectional flow
- Program object always correct
- Editor is just a view

## Testing Plan

### Before Implementation
1. Create comprehensive test suite for current behavior
2. Test all commands: RUN, LIST, SAVE, LOAD, RENUM, NEW
3. Test auto-numbering, Ctrl+I, paste operations
4. Test error handling (syntax errors, etc.)

### During Implementation
1. Implement incremental parsing (parse one line at a time)
2. Benchmark parsing speed (ensure <100ms for 1000 lines)
3. Test cursor position preservation
4. Test undo/redo behavior

### After Implementation
1. Re-run all tests
2. Verify no regressions
3. Test edge cases:
   - Very large programs (>5000 lines)
   - Rapid typing/editing
   - Syntax errors mid-edit
   - Copy/paste large blocks

## Performance Considerations

**Parsing Speed (estimated):**
- Simple line (10 PRINT X): ~0.01ms
- Complex line (IF/THEN/ELSE): ~0.05ms
- 1000 line program: ~20ms
- 10000 line program: ~200ms

**Acceptable latency:**
- <50ms: Unnoticeable
- 50-100ms: Barely noticeable
- 100-200ms: Noticeable but acceptable
- >200ms: Feels sluggish

**Optimization if needed:**
- Incremental parsing (only changed lines)
- Background parsing (parse in worker thread)
- Dirty flag (skip refresh if no changes)

## Edge Cases

### Case 1: User typing mid-line
```
User types: "10 PRINT"
Parse: Incomplete statement (error)
Action: Keep in editor, don't update program object
User types: " X"
Parse: Complete statement (success)
Action: Update program object with line 10
```

### Case 2: Syntax error
```
User types: "10 PRINNT X"  (typo)
Parse: Unknown keyword PRINNT (error)
Action: Show red error marker, keep in editor
User fixes: "10 PRINT X"
Parse: Success
Action: Update program object, clear error marker
```

### Case 3: Multi-line paste
```
User pastes 100 lines
Parse: Line by line, updating program object
Action: Show progress, update editor incrementally
Result: Program object has all 100 lines
```

## Implementation Files

### Files to Modify
- `src/ui/tk_ui.py` - Main UI class
  - Remove `_save_editor_to_program()`
  - Make `_refresh_editor()` smarter
  - Add incremental parsing on text change

### Files to Keep
- `src/program.py` - Program object (single source of truth)
- `src/ui/ui_helpers.py` - Serialization functions (for generating editor text)

### New Files
- `src/ui/incremental_parser.py` - Parse individual lines efficiently
- `tests/test_single_source.py` - Test suite for new architecture

## Migration Plan

**Step 1: Add logging**
- Log every `_save_editor_to_program()` call
- Log every `_refresh_editor()` call
- Analyze sync patterns

**Step 2: Incremental parsing**
- Implement line-by-line parsing
- Test with current architecture
- Ensure performance acceptable

**Step 3: Switch to on-demand generation**
- Change `_refresh_editor()` to generate from program object
- Keep `_save_editor_to_program()` for now (compatibility)

**Step 4: Event-based updates**
- Add text change events
- Parse changed lines immediately
- Remove manual sync calls

**Step 5: Remove duplication**
- Remove `_save_editor_to_program()` entirely
- Program object is single source
- Editor generated on-demand

**Step 6: Optimize**
- Profile performance
- Add incremental updates if needed
- Benchmark large programs

## Priority

**MEDIUM-HIGH** - This is an architectural issue that affects reliability and maintainability. Should be addressed after critical bugs but before new features.

## Notes

- Classic BASIC interpreters had the same issue (line editor vs. program memory)
- Solution: Editor was just a view, program was always parsed
- Modern editors (VS Code, etc.) use same approach (AST is truth, text is view)
- Counterexample: Text editors keep text as truth, highlighting is regenerated

## Decision

Need to decide: Which is more important?
1. **Correctness**: Program object is truth (recommended)
2. **User experience**: Editor text is truth

For an interpreter, correctness is more important. Recommend **Option A**.
