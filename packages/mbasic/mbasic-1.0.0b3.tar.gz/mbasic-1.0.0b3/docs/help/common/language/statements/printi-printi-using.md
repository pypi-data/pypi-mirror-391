---
category: file-io
description: To write data to a sequential disk file
keywords: ['command', 'data', 'field', 'file', 'for', 'if', 'input', 'line', 'number', 'open']
syntax: PRINT#<file number>,[USING<string exp>;]<list of expressions>
title: PRINT# AND PRINT# USING
type: statement
---

# PRINT# AND PRINT# USING

## Syntax

```basic
PRINT#<file number>, [<list of expressions>]
PRINT#<file number>, USING <string exp>; <list of expressions>
```

**Versions:** Disk

## Purpose

To write data to a sequential disk file.

## Remarks

PRINT# writes data to a sequential file opened for output (mode "O") or append (mode "A"). The file number must refer to a file opened with the OPEN statement.

**PRINT#** works exactly like PRINT except output goes to the file instead of the screen:
- Items separated by commas are printed in print zones
- Items separated by semicolons are printed adjacent to each other
- A semicolon at the end suppresses the carriage return

**PRINT# USING** formats output using a format string, just like PRINT USING:
- # for digit positions
- . for decimal point
- $$ for floating dollar sign
- ** for asterisk fill
- , for thousands separator

The file must be opened before using PRINT#. Data written with PRINT# can be read back with INPUT# or LINE INPUT#.

## See Also
- [OPEN](open.md) - Open a file for output
- [CLOSE](close.md) - Close the file when done
- [INPUT#](input_hash.md) - Read data from sequential file
- [LINE INPUT#](inputi.md) - Read entire line from file
- [WRITE#](writei.md) - Write data with automatic delimiters
- [PRINT](print.md) - Output to screen
- [PRINT USING](print.md) - Formatted output to screen
- [EOF](../functions/eof.md) - Test for end of file
