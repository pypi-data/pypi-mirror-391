---
category: string
description: Returns a one-character string whose ASCII code is the specified value
keywords: ['chr', 'chr$', 'ascii', 'character', 'string', 'convert', 'function']
syntax: CHR$(I)
related: ['asc', 'str_dollar']
title: CHR$
type: function
---

# CHR$

## Syntax

```basic
CHR$(I)
```

## Description

Returns a one-character string whose character has the ASCII code I. This function is commonly used to send special characters or control codes to the screen or printer.

The argument I must be in the range 0-255. Values outside this range will produce an "Illegal function call" error.

## Example

```basic
10 PRINT CHR$(65)
RUN
A
Ok

10 PRINT CHR$(7)    ' Ring the bell
20 PRINT CHR$(13)   ' Carriage return
30 PRINT CHR$(10)   ' Line feed
```

## See Also
- [ASC](asc.md) - Returns a numerical value that is the ASCII code of the first character of the string X$
- [HEX$](hex_dollar.md) - Returns a string which represents the hexadecimal value of the decimal argument
- [INSTR](instr.md) - Searches for the first occurrence of string Y$ in X$ and returns the position at which the match is found
- [LEFT$](left_dollar.md) - Return the leftmost N characters from a string
- [LEN](len.md) - Returns the number of characters in X$
- [MID$](mid_dollar.md) - Extract a substring from the middle of a string
- [MID$ Assignment](../statements/mid-assignment.md) - Replace characters within a string variable
- [OCT$](oct_dollar.md) - Returns a string which represents the octal value of the decimal argument
- [RIGHT$](right_dollar.md) - Return the rightmost N characters from a string
- [SPACE$](space_dollar.md) - Returns a string of I spaces
- [SPC](spc.md) - Prints I blanks on the terminal
- [STR$](str_dollar.md) - Convert a number to its string representation
- [STRING$](string_dollar.md) - Returns a string of length I whose characters all have ASCII code J or the first character of X$
- [VAL](val.md) - Returns the numerical value of string X$
