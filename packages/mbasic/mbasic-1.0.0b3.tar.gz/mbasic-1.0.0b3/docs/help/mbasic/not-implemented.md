---
description: Features not implemented in this MBASIC
keywords:
- not implemented
- unsupported
- limitations
- missing features
title: Not Implemented Features
type: reference
---

# Not Implemented Features

This document lists features found in other BASIC dialects that are **not** in MBASIC 5.21.

## Graphics (Not in MBASIC 5.21)

These graphics commands are from GW-BASIC and QuickBASIC, not MBASIC 5.21:

- **SCREEN** - Set graphics mode
- **PSET** - Plot pixel
- **LINE** - Draw line (GW-BASIC graphics version - not the LINE INPUT statement which IS implemented)
- **CIRCLE** - Draw circle
- **PAINT** - Fill area
- **DRAW** - Draw using string commands
- **GET/PUT** - Graphics block operations (not the file I/O GET/PUT which ARE implemented)
- **PALETTE** - Color palette
- **VIEW** - Set viewport
- **WINDOW** - Set coordinate system

**Why not implemented:** MBASIC 5.21 predates graphics BASIC. These features were added in GW-BASIC and later versions.

**Alternative:** Use modern graphics libraries outside BASIC if needed.

## Sound (Not in MBASIC 5.21)

Sound commands from later BASICs:

- **SOUND** - Generate tone
- **PLAY** - Play music string
- **BEEP** - System beep

**Why not implemented:** MBASIC 5.21 had no sound support.

**Alternative:** Use `PRINT CHR$(7)` for system beep (bell character).

## Advanced Control Flow (Not in MBASIC 5.21)

These are from QuickBASIC and later:

- **SELECT CASE** - Multi-way branch
- **DO...LOOP** - Flexible looping
- **EXIT FOR/WHILE** - Break out of loop
- **CONTINUE** - Skip to next iteration

**Why not implemented:** MBASIC 5.21 only has FOR...NEXT, WHILE...WEND, GOTO, GOSUB.

**Alternative:**
- Use IF...THEN for multi-way: `10 IF X=1 THEN GOTO 100: IF X=2 THEN GOTO 200`
- Use WHILE...WEND instead of DO...LOOP
- Use GOTO to exit loops early

## Procedures (Not in MBASIC 5.21)

QuickBASIC introduced structured programming:

- **SUB...END SUB** - Subroutines with parameters
- **FUNCTION...END FUNCTION** - Functions with return values
- **DECLARE** - Forward declarations
- **CALL** - Call subroutine by name
- **STATIC/SHARED** - Variable scope keywords
- **LOCAL** - Local variables

**Why not implemented:** MBASIC 5.21 only has GOSUB for subroutines and DEF FN for simple functions.

**Alternative:**
- Use GOSUB for subroutines (no parameters, global variables)
- Use DEF FN for single-expression functions

## Advanced Data Types (Not in MBASIC 5.21)

Later BASICs added:

- **LONG** - 32-bit integer
- **CURRENCY** - Fixed-point decimal
- **TYPE...END TYPE** - User-defined types/structures
- **VARIANT** - Variable type
- **CONST** - Named constants

**Why not implemented:** MBASIC 5.21 has only INTEGER, SINGLE, DOUBLE, STRING.

**Alternative:** Use what's available or define constants as variables.

## File Handling Extensions

Advanced file features from later versions:

- **BINARY** mode - Binary file access beyond GET/PUT
- **APPEND** mode - Simplified append
- **ACCESS READ/WRITE** - File locking
- **SHARED** - File sharing modes
- **FILEATTR** - File attributes
- **FREEFILE** - Find available file number
- **DIR$** - Directory listing
- **CHDIR/MKDIR/RMDIR** - Directory operations

**Why not implemented:** MBASIC 5.21 has basic sequential and random file I/O only.

**Available in MBASIC 5.21:**
- Sequential files (INPUT/OUTPUT mode)
- Random access files
- OPEN, CLOSE, GET, PUT, FIELD
- KILL (delete file)
- NAME (rename file)

## Event Handling (Not in MBASIC 5.21)

Event-driven features from GW-BASIC:

- **ON TIMER** - Timer events
- **ON KEY** - Keyboard events
- **ON COM/PEN/STRIG** - Hardware events
- **TIMER** - System timer

**Why not implemented:** MBASIC 5.21 is not event-driven.

**Alternative:** Poll for conditions in a loop.

## Memory Management

Advanced memory features:

- **CLEAR** (extended) - Set stack/string space
- **FRE(-1)** - Largest free block
- **FRE(-2)** - Stack space
- **SETMEM** - Set memory limits
- **ERDEV$** - Device error

**Available in MBASIC 5.21:**
- Basic CLEAR (clear variables)
- FRE(0) (free memory)
- PEEK/POKE (limited in this implementation)

## Hardware Access

CP/M-specific or hardware features:

- **INP/OUT/WAIT** - I/O ports (not portable)
- **USR** - Machine language calls (not portable)
- **BLOAD/BSAVE** - Binary load/save
- **DEF SEG** - Segment register
- **CALL ABSOLUTE** - Call machine code

**Why not implemented:** Not portable to modern systems, hardware-specific.

**Note:** PEEK/POKE are emulated with virtual memory in this implementation.

## String Enhancements

Later BASIC features:

- **LCASE$/UCASE$** - Change case (use your own routine)
- **LTRIM$/RTRIM$/TRIM$** - Trim whitespace (use LEFT$/RIGHT$/MID$)
- **REPLACE$** - String replacement
- **SPLIT** - Split string
- **JOIN** - Join strings

**Available in MBASIC 5.21:**
- LEFT$, RIGHT$, MID$ - Extract substrings
- INSTR - Find substring
- LEN - String length
- STR$/VAL - Number conversion

## What IS Available

MBASIC 5.21 includes:

✓ All standard statements (FOR, WHILE, IF, GOTO, GOSUB, etc.)
✓ File I/O (sequential and random)
✓ Arrays (multi-dimensional)
✓ String manipulation (LEFT$, RIGHT$, MID$, INSTR, etc.)
✓ Math functions (SIN, COS, TAN, LOG, EXP, SQR, etc.)
✓ Error handling (ON ERROR GOTO, RESUME, ERR, ERL)
✓ User-defined functions (DEF FN)
✓ Data statements (DATA, READ, RESTORE)
✓ All four data types (INTEGER, SINGLE, DOUBLE, STRING)

## See Also

- [Compatibility Guide](compatibility.md) - What works from CP/M MBASIC
- [Features](features.md) - What is implemented
- [Language Reference](../common/language/index.md) - All available features
