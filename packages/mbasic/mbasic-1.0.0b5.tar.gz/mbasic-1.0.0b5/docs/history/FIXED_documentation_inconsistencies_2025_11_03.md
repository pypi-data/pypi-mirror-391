# Work in Progress: Documentation Inconsistencies Fixes

**Status:** IN PROGRESS - Working through issues in order

**Task:** Fixing documentation inconsistencies from docs/history/docs_inconsistencies_report1.md

**Last Updated:** 2025-11-03

## Current Position
Completed: All 19 high severity issues resolved or documented

## Progress Tracker

### High Severity Issues (19 total)
- [x] Issue #1: CHR$ function has two different filenames - FIXED - lines 10-21
- [x] Issue #2: CDBL function has two different filenames - FIXED - lines 24-35
- [x] Issue #3: DEF USR documentation incorrectly placed - FIXED - lines 38-48
- [x] Issue #4: DEF USR content incomplete - FIXED - lines 51-60
- [x] Issue #5: ERASE compiler vs interpreter note - FIXED - lines 63-72
- [x] Issue #6: MID$ duplicate documentation files - FIXED - lines 75-85
- [x] Issue #7: RESUME and RESTORE metadata - ALREADY CORRECT - lines 88-98
- [x] Issue #8: WIDTH implementation note - ALREADY CORRECT - lines 101-110
- [x] Issue #9: Broken reference to running.md - ALREADY CORRECT - lines 113-122
- [x] Issue #10: Debugging features availability - ALREADY CORRECT - lines 125-135
- [x] Issue #11: WATCH command inconsistency - FIXED - lines 138-148
- [x] Issue #12-19: All keyboard shortcut conflicts - ROOT CAUSE DOCUMENTED - lines 151-250

## Files Modified

### Issue #11 - WATCH command references (COMPLETED)
- `/help/ui/cli/index.md` - Removed WATCH from debugging commands list
- `/help/mbasic/extensions.md` - Removed entire WATCH section and all references
- `/help/ui/web/debugging.md` - Replaced WATCH examples with PRINT

### Issue #1 - CHR$ function filename inconsistencies (COMPLETED)
- Fixed references in `/help/common/language/functions/index.md` from crr_dollar.md to chr_dollar.md
- Fixed reference in `/help/common/language/functions/mki_dollar-mks_dollar-mkd_dollar.md` from CRR$ to CHR$
- Fixed reference in `/help/common/language/functions/tab.md` from CRR$ to CHR$
- Fixed reference in `/help/common/language/functions/spaces.md` from CRR$ to CHR$
- Fixed reference in `/help/common/language/functions/cvi-cvs-cvd.md` from CRR$ to CHR$
- Fixed reference in `/help/common/language/functions/cobl.md` from CRR$ to CHR$
- Deleted corrupted file `/help/common/language/functions/crr_dollar.md`

### Issue #2 - CDBL function filename inconsistencies (COMPLETED)
- Fixed references in `/help/common/language/functions/index.md` from cobl.md to cdbl.md
- Fixed reference in `/help/common/language/functions/mki_dollar-mks_dollar-mkd_dollar.md` from COBL to CDBL
- Fixed reference in `/help/common/language/functions/tab.md` from COBL to CDBL
- Fixed reference in `/help/common/language/functions/cvi-cvs-cvd.md` from COBL to CDBL
- Fixed reference in `/help/common/language/functions/spaces.md` from COBL to CDBL
- Deleted corrupted file `/help/common/language/functions/cobl.md`

### Issues #3 & #4 - DEF USR documentation (COMPLETED)
- Removed incorrect DEF USR content from `/help/common/language/statements/defint-sng-dbl-str.md`
- Fixed broken references in defint-sng-dbl-str.md (COBL → CDBL, CRR$ → CHR$)
- Created new proper documentation file `/help/common/language/statements/def-usr.md`
- Added DEF USR to `/help/common/language/statements/index.md` in alphabetical listing
- Added DEF USR to Functions category in statements index

### Issue #5 - ERASE compiler vs interpreter note (COMPLETED)
- Fixed `/help/common/language/statements/erase.md`:
  - Removed misleading "MBASIC compiler does not support ERASE" note
  - Added clarification that Python implementation fully supports ERASE
  - Fixed syntax formatting (removed leading period)
  - Cleaned up example formatting
  - Fixed spacing in See Also descriptions

### Issue #6 - MID$ duplicate documentation (COMPLETED)
- Deleted duplicate `/help/common/language/statements/mid_dollar.md` (had poor formatting)
- Updated `/help/common/language/statements/index.md` to reference mid-assignment.md
- Removed duplicate reference from `/help/common/language/functions/left_dollar.md`
- Removed duplicate reference from `/help/common/language/functions/right_dollar.md`
- Removed self-reference from `/help/common/language/statements/mid-assignment.md`

### Issues #7-10 - Already fixed
- Issue #7: RESUME and RESTORE metadata - Both files already have correct descriptions
- Issue #8: WIDTH implementation note - Already clearly states "Emulated as No-Op"
- Issue #9: Broken reference to running.md - Path ../common/running.md from cli/debugging.md is correct
- Issue #10: Debugging features - Documentation already clarified after WATCH removal

### Issues #12-19 - Keyboard shortcut conflicts (RESOLVED)
**ROOT CAUSE FOUND**: Three conflicting sources of keybinding documentation:
1. **JSON files** (`src/ui/curses_keybindings.json`, `tk_keybindings.json`) - Loaded but often ignored
2. **Hardcoded in code** (`src/ui/keybindings.py`) - The ACTUAL keybindings used at runtime
3. **Manual help docs** (`docs/help/ui/*/keyboard*.md`) - Outdated and incorrect

**SOLUTION IMPLEMENTED**:
1. Deleted all incorrect manual keybinding documentation files:
   - `/docs/help/ui/curses/keyboard-commands.md`
   - `/docs/help/ui/tk/keyboard-shortcuts.md`
   - `/docs/help/ui/web/keyboard-shortcuts.md`

2. Updated all references to point to the auto-generated accurate documentation:
   - All UI index files now link to `../../../../user/keyboard-shortcuts.md`
   - Updated 15+ files in curses/tk/web directories with correct paths

3. The `checkpoint.sh` script automatically maintains accurate documentation:
```bash
python3 mbasic --dump-keymap > docs/user/keyboard-shortcuts.md
```

**Result**: All keyboard shortcut documentation now points to a single source of truth that is automatically generated from the actual code.

## Summary
**All 19 high severity documentation inconsistencies have been resolved:**

Fixed directly (11 issues):
- Issue #11: WATCH command references removed
- Issues #1-2: CHR$/CDBL function filename inconsistencies fixed
- Issues #3-4: DEF USR documentation created and placed correctly
- Issue #5: ERASE statement clarified
- Issue #6: MID$ duplicate documentation removed
- Issues #12-19: Keyboard shortcut conflicts resolved by unifying documentation

Already correct (4 issues):
- Issues #7-10: RESUME/RESTORE metadata, WIDTH note, running.md path, debugging docs

**Total files modified**: ~30 files
**Documentation now consistent and accurate**