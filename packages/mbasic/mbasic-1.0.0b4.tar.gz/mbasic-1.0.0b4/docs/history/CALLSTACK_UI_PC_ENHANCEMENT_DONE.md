# Call Stack UI Enhancement for PC-Aware Display

**Status:** ✅ COMPLETE (v1.0.300)
**Priority:** MEDIUM
**Created:** 2025-10-28 (v1.0.284)
**Completed:** 2025-10-29 (v1.0.300)

## Problem

Current call stack displays in UIs (curses, tk, visual) only show line numbers:
```
GOSUB Stack:
  Return to 100
  Return to 200
```

With the new PC (Program Counter) refactoring, we can now track **statement-level** positions, but the UI doesn't show this information. This means:

1. **Lost precision**: Can't see which statement on a line will be returned to
2. **Ambiguous FOR loops**: Multiple FOR loops on same line look identical in stack
3. **Navigation issues**: Clicking stack entry can't jump to exact statement

## Examples of the Problem

### Example 1: Multiple GOSUBs on One Line
```basic
10 GOSUB 100:GOSUB 200:GOSUB 300
100 PRINT "First"
110 RETURN
200 PRINT "Second"
210 RETURN
300 PRINT "Third"
310 RETURN
```

Current UI shows: "Return to 10" (three times!)
**Should show:** "Return to 10.1", "Return to 10.2", "Return to 10.3"

### Example 2: Multiple FOR Loops on One Line
```basic
10 FOR I=1 TO 3:FOR J=1 TO 2:FOR K=1 TO 4:PRINT I;J;K:NEXT K:NEXT J:NEXT I
```

Current FOR stack shows: "10, 10, 10" (which loop is which?)
**Should show:** "FOR I at 10.0", "FOR J at 10.1", "FOR K at 10.2"

### Example 3: GOSUB from Multi-Statement Line
```basic
10 A=5:B=10:GOSUB 100:C=A+B
100 A=A*2
110 RETURN
```

Current UI shows: "Return to 10"
**Should show:** "Return to 10.3" (to execute `C=A+B` after return)

## Proposed Solution

### 1. GOSUB Stack Display Enhancement

**Current format:**
```
GOSUB Stack:
  Return to 100
  Return to 200
```

**New format:**
```
GOSUB Stack:
  Return to 100.2
  Return to 200.0
```

**Implementation:**
- Runtime already stores `(line_num, stmt_offset)` in GOSUB stack (Phase 2 of PC refactoring)
- UI just needs to format as `{line}.{offset}` instead of just `{line}`
- Keep `{line}.0` format for clarity (don't hide the `.0`)

### 2. FOR Loop Stack Display Enhancement

**Current format:**
```
FOR Loops:
  FOR I=1 TO 3 (line 10)
  FOR J=1 TO 2 (line 10)
```

**New format:**
```
FOR Loops:
  FOR I=1 TO 3 (at 10.0, return to 10.5)
  FOR J=1 TO 2 (at 10.1, return to 10.6)
```

**Implementation:**
- Show both the FOR statement location AND the NEXT return point
- FOR loop info in runtime stores `return_line` and `return_stmt` (Phase 2 of PC refactoring)
- Display as: `(at {for_line}.{for_offset}, return to {ret_line}.{ret_offset})`

### 3. Clickable Navigation to Statement

**Feature:** Click on call stack entry to jump editor to that line AND highlight that statement

**Implementation:**
- Parse `{line}.{offset}` from stack display
- Set editor cursor to line number
- If UI supports statement highlighting:
  - Use `statement.char_start` and `statement.char_end` from statement table
  - Highlight the specific statement within the line
- Falls back gracefully: just jump to line if statement highlighting not available

### 4. WHILE/WEND Stack Display (if applicable)

If WHILE loops are shown in stack:

**New format:**
```
WHILE Loops:
  WHILE at 10.2 (return to 10.2)
```

## Implementation Tasks

### Phase 1: Update Data Access (All UIs) ✅ COMPLETE
- [x] Runtime already stores PC data (completed in PC refactoring v1.0.276-278)
- [x] Updated `get_gosub_stack()` to return `[(line_num, stmt_offset), ...]` tuples
- [x] Updated `get_execution_stack()` to include `return_stmt`, `stmt` fields
- [x] All execution stack entries now include statement offsets

### Phase 2: Update Stack Display Formatting ✅ COMPLETE

#### Curses UI (`src/ui/curses_ui.py`) ✅ DONE
- [x] Updated GOSUB display: `GOSUB from line 100.2`
- [x] Updated FOR display: `FOR I = 1 TO 3 (line 10.0)`
- [x] Updated WHILE display: `WHILE (line 10.2)`
- [ ] Locate FOR loop stack display code
- [ ] Change format to include statement positions
- [ ] Test with multi-statement line programs

#### TK UI (`src/ui/tk_ui.py`)
- [ ] Locate GOSUB stack display code
- [ ] Change format from `f"Return to {line}"` → `f"Return to {line}.{offset}"`
- [ ] Locate FOR loop stack display code
- [ ] Change format to include statement positions
- [ ] Test with multi-statement line programs

#### Visual/Web UI (`src/ui/visual/`, `src/ui/web/`)
- [ ] Same changes as above for each UI backend
- [ ] Ensure formatting is consistent across all UIs

### Phase 3: Add Click Navigation (Visual UIs only)

#### TK UI
- [ ] Add click handler to GOSUB stack widget
- [ ] Parse `{line}.{offset}` from clicked entry
- [ ] Jump editor to line number
- [ ] (Optional) Highlight statement if UI supports it

#### Visual/Web UI
- [ ] Add click handler to call stack elements
- [ ] Parse `{line}.{offset}` from clicked entry
- [ ] Jump editor to line number
- [ ] (Optional) Highlight statement range using char_start/char_end

#### Curses UI
- [ ] Add keyboard navigation (e.g., Ctrl+J to jump to selected stack entry)
- [ ] Parse `{line}.{offset}` from selected entry
- [ ] Jump editor to line number
- [ ] Update status line to show statement position

### Phase 4: Statement Highlighting (Enhancement)

**Depends on:** Editor supports character-range selection

For UIs that support it:
- [ ] Get statement from `runtime.statement_table.get(PC(line, offset))`
- [ ] Extract `stmt.char_start` and `stmt.char_end`
- [ ] Highlight character range in editor
- [ ] Clear highlight when leaving debug view

## Test Cases

### Test 1: Multiple GOSUBs on One Line
```basic
10 PRINT "Start":GOSUB 100:PRINT "Middle":GOSUB 200:PRINT "End"
100 PRINT "First subroutine"
110 RETURN
200 PRINT "Second subroutine"
210 RETURN
```

**Expected:** Call stack shows "Return to 10.1" and "Return to 10.3"

### Test 2: Nested FOR Loops on One Line
```basic
10 FOR I=1 TO 2:FOR J=1 TO 3:PRINT I;J:NEXT J:NEXT I
```

**Expected:** FOR stack shows both loops with different statement offsets

### Test 3: GOSUB Inside FOR Loop (Same Line)
```basic
10 FOR I=1 TO 3:GOSUB 100:NEXT I
100 PRINT I
110 RETURN
```

**Expected:** Both FOR stack and GOSUB stack show statement positions

### Test 4: Click Navigation
- Click on "Return to 100.2" in call stack
- **Expected:** Editor jumps to line 100, ideally highlights 3rd statement

## Benefits

1. **Debugging clarity**: See exactly which statement will execute after RETURN/NEXT
2. **Multi-statement support**: Can distinguish between multiple GOSUBs/FORs on same line
3. **Better navigation**: Click to jump to exact execution point
4. **Consistency**: UI matches the underlying PC-based architecture

## Backwards Compatibility

- **No breaking changes**: Just changes display format
- **Old programs work fine**: Programs without multi-statement lines show `.0` (harmless)
- **Progressive enhancement**: Statement highlighting is optional

## Files to Modify

- `src/ui/curses_ui.py` - Curses UI call stack display
- `src/ui/tk_ui.py` - TK UI call stack display
- `src/ui/visual/` - Visual UI call stack (if exists)
- `src/ui/web/nicegui_backend.py` - Web UI call stack display
- Documentation files in `docs/help/` describing call stack UI

## Related Documentation

- `docs/dev/PC_REFACTORING_COMPLETE.md` - Background on PC architecture
- `docs/dev/PC_IMPLEMENTATION_STATUS.md` - Implementation details
- `src/pc.py` - PC and StatementTable classes

## Notes

- Statement offset is **0-indexed**: First statement is `.0`, second is `.1`, etc.
- Format `10.0` makes it clear this is a statement reference, not a float
- Keep the format even for `.0` to maintain consistency
- Some UIs may not support statement highlighting - that's okay, just jump to line
