# Web UI (NiceGUI) - Missing Features vs TK

**Date:** 2025-10-28
**Status:** Work in Progress
**Current Version:** 1.0.176

This document tracks what the NiceGUI web UI is missing compared to the full TK UI implementation.

---

## CRITICAL MISSING FEATURES

### 1. Auto-Numbering
**Status:** ❌ NOT IMPLEMENTED
**User Impact:** HIGH - Users expect auto-numbering like in TK

**TK Behavior:**
- When you type without a line number (e.g., `PRINT "Hello"`), TK automatically adds a line number
- Default start: 10, increment: 10 (so lines are 10, 20, 30, ...)
- Configurable in Settings dialog
- Can be toggled on/off

**What's Needed:**
- Detect when user enters text without line number in editor
- Auto-prepend line number using current auto-number settings
- Increment counter after each auto-numbered line
- Add settings UI for auto-number start/increment/enable

---

## FILE OPERATIONS

### 2. File Open Dialog
**Status:** ❌ NOT IMPLEMENTED
**TK Has:** File > Open with native file picker, recent files menu
**Web Has:** Button exists but does nothing

### 3. File Save Dialog
**Status:** ❌ NOT IMPLEMENTED
**TK Has:** File > Save, Save As with native file picker
**Web Has:** Button exists but does nothing

### 4. Recent Files Menu
**Status:** ❌ NOT IMPLEMENTED
**TK Has:** Submenu showing last 10 files opened
**Web Has:** Nothing

### 5. Current File Tracking
**Status:** ❌ NOT IMPLEMENTED
**TK Has:** Tracks current filename, shows in title bar
**Web Has:** `self.current_file = None` but not used

---

## EDITOR FEATURES

### 6. Multi-Line Editor
**Status:** ❌ NOT IMPLEMENTED
**TK Has:** Full program visible in editor pane, scroll to edit any line
**Web Has:** Single-line entry field, must type line + "Add Line" button

**This is a MAJOR UX difference!**

### 7. Line Numbering in Editor
**Status:** ❌ NOT IMPLEMENTED
**TK Has:** Custom `LineNumberedText` widget with line numbers in gutter
**Web Has:** Program display is readonly textarea

### 8. Status Column (Breakpoints/Errors)
**Status:** ❌ NOT IMPLEMENTED
**TK Has:** Left margin with symbols:
- ● = Breakpoint
- ? = Parse error
- ▶ = Current execution line
- ⏸ = Paused line

### 9. Syntax Highlighting
**Status:** ❌ NOT IMPLEMENTED
**TK Has:** None (monospace plain text)
**Web Has:** None

### 10. Cut/Copy/Paste (Editor)
**Status:** ❌ NOT IMPLEMENTED
**TK Has:** Edit menu + Ctrl+X/C/V
**Web Has:** Browser default only (no menu items)

### 11. Undo/Redo
**Status:** ❌ NOT IMPLEMENTED
**TK Has:** Unlimited undo/redo (Tk native)
**Web Has:** None

### 12. Find/Replace
**Status:** ❌ NOT IMPLEMENTED (TK doesn't have it either)

---

## EXECUTION & DEBUGGING

### 13. Breakpoints
**Status:** ❌ NOT IMPLEMENTED
**TK Has:**
- Ctrl+B to toggle breakpoint on current line
- Blue dot indicator in status column
- Program pauses when breakpoint hit
- Edit > Clear All Breakpoints

**Web Has:** Nothing

### 14. Step Line / Step Statement
**Status:** ❌ NOT IMPLEMENTED
**TK Has:**
- Step Line: Execute one full BASIC line
- Step Statement: Execute one statement (for multi-statement lines)
- Toolbar buttons + menu items

**Web Has:** Toolbar button exists but does nothing

### 15. Continue from Breakpoint
**Status:** ❌ NOT IMPLEMENTED
**TK Has:** Continue button resumes from paused/breakpoint state
**Web Has:** Toolbar button exists but does nothing

### 16. Current Line Indicator
**Status:** ❌ NOT IMPLEMENTED
**TK Has:** ▶ symbol in status column shows currently executing line
**Web Has:** Nothing

---

## WINDOWS & VIEWS

### 17. Variables Window
**Status:** ❌ NOT IMPLEMENTED
**TK Has:**
- View > Variables (Ctrl+W)
- Shows all variables with name, type, value
- Sortable columns (name, type, value, accessed, written, read count)
- Search/filter functionality
- Auto-refreshes during execution
- Persistent window position

**Web Has:** Nothing

### 18. Execution Stack Window
**Status:** ❌ NOT IMPLEMENTED
**TK Has:**
- View > Execution Stack (Ctrl+K)
- Shows GOSUB/FOR/WHILE stack
- Displays line numbers, statement types
- Sortable columns

**Web Has:** Nothing

---

## IMMEDIATE MODE

### 19. Immediate Mode Pane
**Status:** ❌ NOT IMPLEMENTED
**TK Has:**
- Bottom pane with "Ok >" prompt
- Execute immediate commands (PRINT, LIST, etc.)
- Access to program variables
- Command history with up/down arrows
- Shows execution status (Running, Paused, Error)

**Web Has:** Nothing (immediate commands not possible)

---

## SETTINGS & CONFIGURATION

### 20. Settings Dialog
**Status:** ❌ NOT IMPLEMENTED
**TK Has:** Edit > Settings with tabs:
- **General:** Auto-numbering (start, increment, enabled)
- **Keyboard:** Customize shortcuts (Ctrl+R, Ctrl+H, etc.)
- **Editor:** Font, colors, tab stops

**Web Has:** Nothing

### 21. Keyboard Shortcuts
**Status:** ❌ NOT IMPLEMENTED
**TK Has:** Configurable shortcuts for common operations
**Web Has:** Nothing (relies on menu/toolbar clicks)

---

## HELP SYSTEM

### 22. Help Browser
**Status:** ❌ NOT IMPLEMENTED
**TK Has:**
- Help > Help Topics (Ctrl+H)
- Integrated help window with search
- Statement documentation
- UI-specific help
- Markdown rendering

**Web Has:** Menu item says "Help system coming soon"

### 23. About Dialog
**Status:** ❌ NOT IMPLEMENTED
**TK Has:** Help > About shows version info
**Web Has:** Menu item shows notification (not a dialog)

---

## ERROR HANDLING & RECOVERY

### 24. Edit-and-Continue
**Status:** ❌ NOT IMPLEMENTED
**TK Has:**
- When error occurs, program pauses
- Can edit the problematic line
- Press Continue to resume from edited line
- Error indicator (?) shows in status column

**Web Has:** Error shown, program stops, must re-run

### 25. Parse Error Indicators
**Status:** ❌ NOT IMPLEMENTED
**TK Has:** Red ? symbol in status column for lines with syntax errors
**Web Has:** Nothing (errors only shown when running)

---

## OUTPUT FEATURES

### 26. Output Selection/Copy
**Status:** ⚠️ PARTIAL
**TK Has:** Right-click context menu (Copy, Select All) in output pane
**Web Has:** Browser default selection/copy (no menu)

### 27. Clear Output Button
**Status:** ✅ IMPLEMENTED
**Web Has:** Working button

---

## PROGRAM MANAGEMENT

### 28. NEW Command
**Status:** ✅ IMPLEMENTED
**Web Has:** Working (File > New, toolbar button)

### 29. List Program
**Status:** ✅ IMPLEMENTED
**Web Has:** Working (outputs to console)

### 30. Line Editing
**Status:** ⚠️ PARTIAL
**TK Has:** Multi-line editor, click any line to edit
**Web Has:** Single-line entry, must type line number + text

---

## EXECUTION FEATURES

### 31. Run Program
**Status:** ✅ IMPLEMENTED
**Web Has:** Working with tick-based execution

### 32. Stop Program
**Status:** ✅ IMPLEMENTED
**Web Has:** Working

### 33. INPUT Statement
**Status:** ✅ IMPLEMENTED
**Web Has:** Inline input field below output (v1.0.174)
**Note:** Has async deadlock in pytest, but works in manual testing

### 34. OUTPUT (PRINT)
**Status:** ✅ IMPLEMENTED
**Web Has:** Working

---

## SUMMARY

### Feature Count
- **Total TK Features Audited:** ~60
- **Web UI Has (Working):** ~10
- **Web UI Missing:** ~50
- **Feature Parity:** ~17%

### Priority Categories

**CRITICAL (User Blocking):**
1. Auto-numbering - Users expect this!
2. Multi-line editor - Current single-line entry is very limiting
3. File Open/Save - Can't persist work
4. Immediate mode - Can't test commands interactively

**HIGH (Core Functionality):**
5. Breakpoints
6. Step/Continue debugging
7. Variables window
8. Error indicators
9. Help system

**MEDIUM (Nice to Have):**
10. Settings dialog
11. Keyboard shortcuts
12. Recent files menu
13. Execution stack window
14. Cut/copy/paste menu items

**LOW (Polish):**
15. Undo/redo
16. About dialog
17. Output context menu

---

## Recommended Implementation Order

### Phase 1: Basic Usability
1. **Auto-numbering** - Critical for user experience
2. **File Open/Save** - Can't save work without this
3. **Multi-line editor** - Replace single-line entry with full editor

### Phase 2: Core Features
4. **Immediate mode** - Interactive testing
5. **Variables window** - See program state
6. **Help system** - User documentation

### Phase 3: Debugging
7. **Breakpoints** - Set/clear/display
8. **Step/Continue** - Line-by-line debugging
9. **Current line indicator** - Show execution position
10. **Error indicators** - Visual parse errors

### Phase 4: Polish
11. **Settings dialog** - Configuration
12. **Recent files** - Convenience
13. **Keyboard shortcuts** - Power users
14. **Execution stack** - Advanced debugging

---

## Notes

- TK UI is ~3400 lines
- Web UI is ~500 lines
- Significant work needed to reach feature parity
- Many features require architectural changes (multi-line editor, immediate mode)
- Some features easier in web (keyboard shortcuts, async INPUT)
- File operations need browser file API or server-side storage

---

## Test Results (Current)

**6 tests passing:**
- ✅ UI loads
- ✅ Add program line
- ✅ New program
- ✅ Clear output
- ✅ List program
- ✅ Run program

**1 test skipped:**
- ⏭️ INPUT statement (async deadlock in test env, works manually)
