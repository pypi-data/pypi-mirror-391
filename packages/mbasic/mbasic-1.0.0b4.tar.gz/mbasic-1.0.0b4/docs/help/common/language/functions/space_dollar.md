---
category: string
description: Returns a string of I spaces
keywords: ['space', 'space$', 'spaces', 'string', 'function', 'formatting']
syntax: SPACE$(I)
related: ['string_dollar', 'spc', 'tab']
title: SPACE$
type: function
---

# SPACE$

## Syntax

```basic
SPACE$(I)
```

**Versions:** Extended, Disk

## Description

Returns a string consisting of I spaces. This is equivalent to STRING$(I, 32) since 32 is the ASCII code for a space character.

SPACE$ is commonly used for formatting output or creating padding in strings.

## Example

```basic
10 A$ = "HELLO"
20 B$ = "WORLD"
30 PRINT A$ + SPACE$(5) + B$
RUN
HELLO     WORLD
Ok

10 PRINT "NAME:" + SPACE$(10) + "AGE:"
RUN
NAME:          AGE:
Ok
```

## Notes

- The argument I must be in the range 0-255
- SPACE$(0) returns an empty string
- For variable spacing in PRINT statements, see SPC() and TAB()

## See Also
- [ASC](asc.md) - Returns a numerical value that is the ASCII code of the first character of the string X$
- [CHR$](chr_dollar.md) - Returns a one-character string whose ASCII code is the specified value
- [HEX$](hex_dollar.md) - Returns a string which represents the hexadecimal value of the decimal argument
- [INSTR](instr.md) - Searches for the first occurrence of string Y$ in X$ and returns the position at which the match is found
- [LEFT$](left_dollar.md) - Return the leftmost N characters from a string
- [LEN](len.md) - Returns the number of characters in X$
- [MID$](mid_dollar.md) - Extract a substring from the middle of a string
- [MID$ Assignment](../statements/mid-assignment.md) - Replace characters within a string variable
- [OCT$](oct_dollar.md) - Returns a string which represents the octal value of the decimal argument
- [RIGHT$](right_dollar.md) - Return the rightmost N characters from a string
- [SPC](spc.md) - Prints I blanks on the terminal
- [STR$](str_dollar.md) - Convert a number to its string representation
- [STRING$](string_dollar.md) - Returns a string of length I whose characters all have ASCII code J or the first character of X$
- [TAB](tab.md) - Spaces to position I on the terminal
- [VAL](val.md) - Returns the numerical value of string X$
