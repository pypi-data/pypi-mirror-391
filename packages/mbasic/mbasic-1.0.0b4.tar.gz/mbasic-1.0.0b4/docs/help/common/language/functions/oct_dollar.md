---
category: string
description: Returns a string which represents the octal value of the decimal argument
keywords: ['oct', 'oct$', 'octal', 'convert', 'function', 'string', 'number']
syntax: OCT$(X)
related: ['hex_dollar', 'str_dollar']
title: OCT$
type: function
---

# OCT$

## Syntax

```basic
OCT$(X)
```

**Versions:** Extended, Disk

## Description

Returns a string which represents the octal value of the decimal argument. X is rounded to an integer before OCT$(X) is evaluated.

The returned string contains only the digits 0-7, representing the octal (base-8) value of X.

## Example

```basic
10 INPUT X
20 A$ = OCT$(X)
30 PRINT X; "DECIMAL IS "; A$; " OCTAL"
RUN
? 64
64 DECIMAL IS 100 OCTAL
Ok

10 PRINT OCT$(255)
RUN
377
Ok
```

## See Also
- [ASC](asc.md) - Returns a numerical value that is the ASCII code of the first character of the string X$
- [CHR$](chr_dollar.md) - Returns a one-character string whose ASCII code is the specified value
- [HEX$](hex_dollar.md) - Returns a string which represents the hexadecimal value of the decimal argument
- [INSTR](instr.md) - Searches for the first occurrence of string Y$ in X$ and returns the position at which the match is found
- [LEFT$](left_dollar.md) - Return the leftmost N characters from a string
- [LEN](len.md) - Returns the number of characters in X$
- [MID$](mid_dollar.md) - Extract a substring from the middle of a string
- [MID$ Assignment](../statements/mid-assignment.md) - Replace characters within a string variable
- [RIGHT$](right_dollar.md) - Return the rightmost N characters from a string
- [SPACE$](space_dollar.md) - Returns a string of I spaces
- [SPC](spc.md) - Prints I blanks on the terminal
- [STR$](str_dollar.md) - Convert a number to its string representation
- [STRING$](string_dollar.md) - Returns a string of length I whose characters all have ASCII code J or the first character of X$
- [VAL](val.md) - Returns the numerical value of string X$
