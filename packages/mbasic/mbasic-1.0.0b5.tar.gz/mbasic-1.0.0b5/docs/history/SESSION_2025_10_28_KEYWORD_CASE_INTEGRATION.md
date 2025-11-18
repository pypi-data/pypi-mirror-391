# Keyword Case Settings Integration - Session 2025-10-28

**Version:** 1.0.153
**Date:** 2025-10-28
**Status:** ✅ Complete

## Summary

Integrated the `keywords.case_style` setting with the lexer so that keyword case policies (especially the 'error' policy) are properly enforced across all UIs. Previously, the setting existed but was not being used - all lexers defaulted to `force_lower` policy.

## Problem Statement

The keyword case error policy was implemented but not integrated:
- ✅ Core: `CaseKeeperTable` could raise `ValueError` on case conflicts when policy='error'
- ✅ Settings: `keywords.case_style` setting existed with 'error' option
- ❌ Integration: Lexer instances were not using the setting - always defaulted to 'force_lower'
- ❌ Result: Setting `keywords.case_style = error` had no effect

## Solution

Added a helper function `create_keyword_case_manager()` that reads the setting and creates a properly configured `KeywordCaseManager`. Updated all Lexer instantiations to use this helper.

## Implementation Details

### 1. Helper Function (`src/lexer.py:10-23`)

```python
def create_keyword_case_manager() -> KeywordCaseManager:
    """
    Create a KeywordCaseManager configured from settings.

    Returns:
        KeywordCaseManager with policy from settings, or default policy
    """
    try:
        from src.settings import get
        policy = get("keywords.case_style", "force_lower")
        return KeywordCaseManager(policy=policy)
    except Exception:
        # If settings unavailable, use default
        return KeywordCaseManager(policy="force_lower")
```

**Features:**
- Reads `keywords.case_style` from settings
- Falls back to 'force_lower' if settings unavailable
- Handles exceptions gracefully
- Returns ready-to-use `KeywordCaseManager`

### 2. UI Integration

Updated all Lexer instantiations to pass the settings-configured manager:

**TK UI** (`src/ui/tk_ui.py:743`):
```python
keyword_mgr = create_keyword_case_manager()
lexer = Lexer(program_text, keyword_case_manager=keyword_mgr)
```

**Curses UI** (`src/ui/curses_ui.py:847`):
```python
keyword_mgr = create_keyword_case_manager()
lexer = Lexer(code_text, keyword_case_manager=keyword_mgr)
```

**Web UI** (`src/ui/web/web_ui.py:413, 943`):
```python
keyword_mgr = create_keyword_case_manager()
lexer = Lexer(code, keyword_case_manager=keyword_mgr)
```

**Convenience function** (`src/lexer.py:503`):
```python
def tokenize(source: str) -> List[Token]:
    keyword_mgr = create_keyword_case_manager()
    lexer = Lexer(source, keyword_case_manager=keyword_mgr)
    return lexer.tokenize()
```

### 3. Error Display

Error messages automatically surface through existing UI error handling:

**TK UI:**
- Errors caught by try/except around lexer.tokenize()
- Displayed in output area
- Status set to "Parse error - fix and retry"

**Curses UI:**
- Errors caught by existing error handling
- Displayed in curses error display

**Web UI:**
- Errors caught and displayed in web interface

**Error message format:**
```
Case conflict: 'print' at line 2:4 vs 'PRINT' at line 1:4
```

Includes:
- Both conflicting cases ('print' vs 'PRINT')
- Line numbers (2 vs 1)
- Column positions (both at column 4)

## Files Modified

### Implementation
- `src/lexer.py` (+18 lines)
  - Added `create_keyword_case_manager()` function
  - Updated `tokenize()` to use settings

- `src/ui/tk_ui.py` (+2 lines)
  - Import `create_keyword_case_manager`
  - Create and pass manager to Lexer

- `src/ui/curses_ui.py` (+3 lines)
  - Import `create_keyword_case_manager`
  - Create and pass manager to Lexer

- `src/ui/web/web_ui.py` (+6 lines)
  - Import `create_keyword_case_manager` (2 locations)
  - Create and pass manager to Lexer (2 locations)

### Testing
- `tests/regression/lexer/test_keyword_case_settings_integration.py` (NEW, 128 lines)
  - 7 unit tests covering all scenarios
  - All tests passing

- `tests/manual/test_keyword_case_error_ui.md` (NEW)
  - Comprehensive manual test instructions
  - Test cases for all UIs
  - Verification checklist

- `tests/manual/test_keyword_case_error_display.bas` (NEW)
  - Example program with case conflicts
  - For manual testing

## Testing Results

### Unit Tests
```bash
$ python3 tests/regression/lexer/test_keyword_case_settings_integration.py
test_create_keyword_case_manager_respects_settings ... ok
test_error_policy_no_conflict ... ok
test_error_policy_raises_on_conflict ... ok
test_first_wins_policy ... ok
test_force_lower_policy ... ok
test_force_upper_policy ... ok
test_preserve_policy ... ok

Ran 7 tests in 0.001s
OK
```

### Regression Tests
```bash
$ python3 tests/run_regression.py --category lexer
✅ ALL REGRESSION TESTS PASSED
```

### Manual Testing

**Test program:**
```basic
10 PRINT "First"
20 print "Second"
30 PRINT "Third"
```

**With `keywords.case_style = error`:**
```
ValueError: Case conflict: 'print' at line 2:4 vs 'PRINT' at line 1:4
```

**With `keywords.case_style = force_lower`:**
```
Runs successfully (no error)
```

## Usage Examples

### Setting the Policy

```bash
# In CLI mode
SET keywords.case_style error

# In Python
from src.settings import set
set('keywords.case_style', 'error')
```

### Checking Current Policy

```bash
# In CLI mode
SHOW SETTINGS keywords

# Output:
# keywords.case_style = error
```

### What Each Policy Does

**force_lower** (default):
- Converts all keywords to lowercase
- No errors on case conflicts
- `PRINT`, `print`, `Print` → all become `print`

**force_upper**:
- Converts all keywords to UPPERCASE
- No errors on case conflicts
- `PRINT`, `print`, `Print` → all become `PRINT`

**force_capitalize**:
- Converts all keywords to Capitalized
- No errors on case conflicts
- `PRINT`, `print`, `Print` → all become `Print`

**first_wins**:
- First occurrence sets case for all future uses
- No errors on case conflicts
- `Print`, `PRINT`, `print` → all become `Print`

**preserve**:
- Keeps each keyword exactly as typed
- No errors on case conflicts
- `PRINT`, `print`, `Print` → stay as typed

**error**:
- Raises ValueError on first case conflict
- Forces consistent casing throughout program
- `PRINT`, `print` → ERROR!

## Technical Notes

### Why This Pattern?

**Benefits of `create_keyword_case_manager()`:**
1. **Single source of truth** - One function reads settings
2. **Graceful degradation** - Falls back if settings unavailable
3. **Easy to test** - Can mock settings in tests
4. **Minimal changes** - UIs just call helper and pass result
5. **No circular imports** - Lazy import of settings module

### Error Flow

1. User sets `keywords.case_style = error`
2. UI creates Lexer with `create_keyword_case_manager()`
3. Lexer reads program, calls `register_keyword()` for each keyword
4. `CaseKeeperTable` detects case conflict
5. `ValueError` raised with clear message
6. UI's try/except catches error
7. Error displayed to user

### Performance Impact

**Negligible:**
- Helper function called once per tokenization
- Settings lookup is fast (dict access)
- No performance difference vs. hardcoded policy
- KeywordCaseManager reuses same CaseKeeperTable logic

## Future Enhancements

Possible improvements (not implemented):
1. **IDE-style error markers** - Highlight conflicting keywords in editor
2. **Quick fixes** - Offer to auto-correct case conflicts
3. **Batch reports** - Show all conflicts, not just first
4. **Policy suggestions** - Recommend policy based on existing code style

## Related Documentation

- Settings system: `src/settings.py`, `src/settings_definitions.py`
- Case keeper implementation: `src/case_keeper.py`
- Keyword case manager: `src/keyword_case_manager.py`
- Lexer: `src/lexer.py`
- Manual tests: `tests/manual/test_keyword_case_error_ui.md`

## Commit Info

**Version:** 1.0.153
**Commit:** e5aa312
**Message:** "Integrate keywords.case_style setting with lexer - errors now surface in all UIs"

## Before and After

### Before (v1.0.152)
```python
# Setting existed but wasn't used
settings.set('keywords.case_style', 'error')

# All lexers used default policy
lexer = Lexer(code)  # Always force_lower!

# No errors raised
code = '''10 PRINT "test"
20 print "test"'''
tokenize(code)  # SUCCESS (should error!)
```

### After (v1.0.153)
```python
# Setting is now respected
settings.set('keywords.case_style', 'error')

# Lexers use settings-configured manager
keyword_mgr = create_keyword_case_manager()
lexer = Lexer(code, keyword_case_manager=keyword_mgr)

# Errors raised correctly
code = '''10 PRINT "test"
20 print "test"'''
tokenize(code)  # ValueError: Case conflict!
```

## Success Criteria

✅ All criteria met:
- Settings are read and respected
- Error policy raises ValueError on conflicts
- Error messages are clear and actionable
- Errors display properly in all UIs
- Other policies continue to work
- All tests pass
- No performance regression
- No breaking changes
