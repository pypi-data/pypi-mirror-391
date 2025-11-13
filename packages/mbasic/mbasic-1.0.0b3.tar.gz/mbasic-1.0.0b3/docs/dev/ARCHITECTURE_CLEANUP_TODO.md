# Architecture Cleanup TODO

**Created:** 2025-11-10
**Status:** Not Started
**Priority:** High - Affects maintainability and bug potential

## Overview

The codebase has several architectural issues that make it difficult to maintain and prone to bugs:

1. **State Management Flags** - Multiple overlapping execution state flags
2. **Program Representation Duplication** - Text, AST, and serialized forms kept in sync manually
3. **Encapsulation Violations** - UIs directly access and modify interpreter/runtime internals

## Issue 1: State Management - Immutable PC Approach

### Current State (MESSY)

**Scattered mutable state across multiple objects:**
```python
runtime.stopped = True       # In runtime.py
runtime.halted = False       # Also in runtime.py
pc.halted = True            # DUPLICATE in pc.py!
interpreter.stepping = True  # In interpreter.py
ui.step_mode = "statement"  # In UI files
```

**Historical context:**
- Originally had ~8 different flags
- User asked to reduce them
- Some consolidation happened, but core problem remains: **mutable state everywhere**

### Problems

1. **Duplicate state:** `halted` exists in both PC and runtime - which is correct?
2. **No clear semantics:** `stopped` vs `halted` - what's the difference?
3. **UIs mutate internals:**
   ```python
   # curses_ui.py line 2068
   self.runtime.halted = False  # UI poking runtime

   # curses_ui.py line 3694
   self.runtime.stopped = True  # UI poking runtime
   ```
4. **Race conditions:** Multiple places can modify same flags
5. **Hard to reason about:** "Is it running?" requires checking 3+ flags

### Proposed Solution: IMMUTABLE PC

**Core principle:** PC is the ONLY source of truth. PC is immutable. No flags anywhere else.

```python
@dataclass(frozen=True)  # Immutable!
class ProgramCounter:
    line: int | None           # Where we are (None = not in program)
    statement: int             # Which statement on the line
    stop_reason: str | None    # None=running, "STOP"/"END"/"ERROR"/"BREAK"/"USER"
    error: ErrorInfo | None    # Only if stop_reason=="ERROR"

    def is_running(self) -> bool:
        """Ask the PC, not a separate flag"""
        return self.stop_reason is None

    def is_valid(self, program) -> bool:
        """Can we execute from current position?"""
        if self.line is None:
            return False
        return self.line in program.lines

    # Factory methods to create new PCs
    @classmethod
    def running_at(cls, line: int, statement: int = 0):
        """Create a PC that's running at a position"""
        return cls(line=line, statement=statement, stop_reason=None, error=None)

    @classmethod
    def stopped(cls, line: int, statement: int, reason: str):
        """Create a stopped PC"""
        return cls(line=line, statement=statement, stop_reason=reason, error=None)

    @classmethod
    def error(cls, line: int, statement: int, code: int, message: str, handler: int | None = None):
        """Create a PC stopped on error"""
        return cls(
            line=line,
            statement=statement,
            stop_reason="ERROR",
            error=ErrorInfo(code=code, message=message, on_error_handler=handler)
        )

    def advance(self, new_line: int, new_statement: int):
        """Create new PC at advanced position (still running)"""
        return ProgramCounter.running_at(new_line, new_statement)

    def stop(self, reason: str):
        """Create new PC that's stopped at current position"""
        return ProgramCounter.stopped(self.line, self.statement, reason)

    def resume(self):
        """Create new PC that's running from current position"""
        return ProgramCounter.running_at(self.line, self.statement)

@dataclass(frozen=True)
class ErrorInfo:
    """Error details (no position - PC has that)"""
    code: int
    message: str
    on_error_handler: int | None  # Line to jump to if ON ERROR GOTO active
```

**Usage examples:**

```python
# Start execution
pc = ProgramCounter.running_at(line=10, statement=0)

# Advance to next statement
pc = pc.advance(line=20, statement=0)

# STOP statement executes
pc = pc.stop(reason="STOP")

# Error happens
pc = ProgramCounter.error(line=150, statement=2, code=11, message="Division by zero")

# CONT command
def cmd_cont(self):
    if pc.is_running():
        print("?Already running")
        return

    if not pc.is_valid(program):
        print("?Can't continue")  # Line deleted or doesn't exist
        return

    # Create new running PC
    pc = pc.resume()

# UIs can't mutate - must create new PC
pc.line = 999  # ❌ AttributeError: can't set attribute
pc = ProgramCounter.running_at(line=999)  # ✓ Correct
```

### Benefits

1. **No duplicate state** - PC is the only state, no runtime.stopped/halted
2. **No mutation bugs** - Can't modify PC, must create new one
3. **UIs can't poke internals** - frozen dataclass prevents it
4. **Clear semantics** - `is_running()` is the only question
5. **Thread-safe** - Immutable objects are inherently thread-safe
6. **Easier debugging** - PC is a value, can print/compare/log it
7. **No "stopped vs halted" confusion** - only one concept: stop_reason

### Files to Modify

**Phase 1: Create immutable PC**
- [ ] `src/pc.py` - Rewrite as immutable dataclass with factory methods
- [ ] Add `ErrorInfo` dataclass

**Phase 2: Update interpreter to use immutable PC**
- [ ] `src/interpreter.py` - Replace all `pc.line = X` with `pc = pc.advance(X)`
- [ ] Remove all references to `runtime.stopped/halted`
- [ ] Use `pc.is_running()` instead of flag checks

**Phase 3: Update UIs to create new PCs**
- [ ] `src/ui/curses_ui.py` - Remove 20+ `runtime.halted/stopped` mutations
- [ ] `src/ui/tk_ui.py` - Remove state mutations
- [ ] `src/ui/web/nicegui_backend.py` - Remove state mutations
- [ ] All UIs: Replace mutations with PC creation

**Phase 4: Remove old flags**
- [ ] `src/runtime.py` - Delete `stopped` and `halted` fields
- [ ] Verify no remaining references

## Issue 2: Program Representation Duplication

### Current State

**Three representations exist:**

1. **Text (editor_lines)** - What the editor displays
   - Stored in: `curses_ui.editor_lines`, `tk_ui.editor_text`
   - Format: List of strings or Text widget content

2. **AST (line_asts)** - Parsed abstract syntax tree
   - Stored in: `interactive.line_asts`
   - Format: Dict mapping line number → AST node

3. **Serialized (statement_table)** - Runtime execution form
   - Stored in: `runtime.statement_table`
   - Format: List of executable statements

### Problems

1. **Manual synchronization:**
   ```python
   # Add line to AST
   self.line_asts[line_num] = parsed_ast

   # Add line to editor
   self.editor_lines.append(text)

   # Rebuild statement_table
   self.runtime.statement_table = ...
   ```

2. **Sync failures create bugs:**
   - Editor shows line 100 but AST doesn't have it
   - Runtime executes stale code from old statement_table
   - Line numbers in error messages don't match editor

3. **50+ places** in curses_ui.py alone juggle these representations

### Proposed Solution

- [ ] **Single source of truth:** AST should be canonical
- [ ] **Derived representations:**
  ```python
  editor_lines = program.to_text()  # Generated from AST
  statement_table = program.to_executable()  # Generated from AST
  ```
- [ ] **Lazy regeneration:** Only rebuild when needed
- [ ] **Hide internals:** Editor shouldn't access AST directly

### Files to Modify

- Create new: `src/program_model.py` - Unified program representation
- `src/interactive.py` - Replace line_asts with ProgramModel
- `src/ui/curses_ui.py` - Use ProgramModel API, remove direct AST access
- `src/ui/tk_ui.py` - Same
- `src/runtime.py` - Accept prebuilt statement_table from ProgramModel

## Issue 3: Encapsulation Violations

### Current State

**UIs directly access interpreter/runtime internals:**

```python
# curses_ui.py examples:
self.runtime.halted = False                    # Line 2068
self.runtime.stopped = True                    # Line 3694
self.runtime.pc = new_pc                       # (if exists)
self.program.line_asts[num] = ast             # Direct dict modification
```

### Problems

1. **No API contract** - UIs can modify anything
2. **Breaking changes hidden** - Renaming a field breaks all UIs
3. **State invariants violated** - PC set without updating NPC, etc.
4. **Testing nightmare** - Can't test interpreter without UI

### Proposed Solution

- [ ] **Define public API** for interpreter/runtime:
  ```python
  # Public methods (safe to call)
  interpreter.run()
  interpreter.step()
  interpreter.stop()
  interpreter.set_breakpoint(line)

  # Private internals (UIs should not touch)
  interpreter._runtime  # Not interpreter.runtime
  interpreter._pc       # Not interpreter.pc
  ```

- [ ] **Make fields private** (prefix with `_`)
- [ ] **Provide accessor methods** for legitimate UI needs
- [ ] **Document the contract** in docstrings

### Files to Modify

- `src/interpreter.py` - Make fields private, add public methods
- `src/runtime.py` - Same
- `src/interactive.py` - Same
- All UIs - Update to use public API only

## Implementation Plan

### Phase 1: Documentation (1-2 days)
- [ ] Document current state semantics
- [ ] Create state diagrams
- [ ] List all encapsulation violations

### Phase 2: State Management (3-5 days)
- [ ] Add state management methods to runtime
- [ ] Update all callers to use methods
- [ ] Remove direct flag access
- [ ] Add tests for state transitions

### Phase 3: Program Representation (5-7 days)
- [ ] Design ProgramModel class
- [ ] Migrate interactive.py to use ProgramModel
- [ ] Update UIs to use ProgramModel API
- [ ] Remove direct AST/line_asts access

### Phase 4: Encapsulation (3-5 days)
- [ ] Define public APIs
- [ ] Make internal fields private
- [ ] Update all UIs to use public API
- [ ] Add API documentation

### Phase 5: Testing & Validation (2-3 days)
- [ ] Write unit tests for new APIs
- [ ] Integration tests for UI interactions
- [ ] Manual testing of all UIs
- [ ] Performance regression testing

**Total Estimated Time:** 14-22 days

## Success Metrics

After completion:
- [ ] Zero direct assignments to `runtime.stopped/halted` outside runtime.py
- [ ] Single source of truth for program representation
- [ ] All interpreter/runtime fields are private (`_` prefix)
- [ ] UIs only call public methods, never access internal state
- [ ] State transitions documented and enforced
- [ ] Consistency checker finds fewer "unclear interaction" issues

## Notes

This refactoring will cause merge conflicts with any in-progress work. Recommend:
1. Complete all pending v20 fixes first
2. Create a feature branch for this refactoring
3. Merge incrementally (phase by phase) to catch regressions early

## Related Issues

- Consistency checker v1-v20 repeatedly flagged state management confusion
- CONT command bug (can't detect if program was edited) - architectural issue
- PC/NPC synchronization bugs - encapsulation issue
- Editor sync bugs - program representation issue
