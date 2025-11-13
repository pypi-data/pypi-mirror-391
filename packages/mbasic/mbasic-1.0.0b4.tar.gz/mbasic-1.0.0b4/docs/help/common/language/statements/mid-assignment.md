---
category: string
description: Replace characters within a string variable
keywords: ['mid', 'mid$', 'assignment', 'replace', 'string', 'substring', 'modify']
syntax: MID$(string-var, start[, length]) = expression
title: MID$ Assignment
type: statement
related: ['mid_dollar', 'left_dollar', 'right_dollar']
---

# MID$ Assignment

## Syntax

```basic
MID$(string-var, start[, length]) = string-expression
```

**Versions:** Extended, Disk

## Purpose

To replace characters within a string variable without creating a new string.

## Remarks

The MID$ assignment statement modifies a portion of an existing string variable by replacing characters starting at the specified position.

**string-var** - The string variable to be modified

**start** - The character position where replacement begins (1-based)

**length** - (Optional) The number of characters to replace. If omitted, all characters from start position to the end of the string-expression are used

The replacement follows these rules:
- Only existing characters in the string are replaced
- The string length never changes (no characters are added or removed)
- If length is specified, at most that many characters are replaced
- If the replacement string is shorter than length, only the available characters are replaced
- Characters beyond the original string length are ignored

## Example

```basic
10 A$ = "HELLO WORLD"
20 MID$(A$, 1, 5) = "GOODBYE"
30 PRINT A$
RUN
GOODB WORLD
Ok

10 B$ = "ABCDEFGH"
20 MID$(B$, 3) = "XY"
30 PRINT B$
RUN
ABXYEFGH
Ok

10 C$ = "1234567890"
20 MID$(C$, 5, 3) = "***"
30 PRINT C$
RUN
1234***890
Ok
```

## Notes

- The target string length never changes - only characters are replaced
- Position numbering starts at 1, not 0
- If start position is beyond string length, no replacement occurs
- This is more efficient than string concatenation for modifying strings

## See Also
- [ASC](../functions/asc.md) - Returns a numerical value that is the ASCII code of the first character of the string X$
- [CHR$](../functions/chr_dollar.md) - Returns a one-character string whose ASCII code is the specified value
- [HEX$](../functions/hex_dollar.md) - Returns a string which represents the hexadecimal value of the decimal argument
- [INSTR](../functions/instr.md) - Searches for the first occurrence of string Y$ in X$ and returns the position at which the match is found
- [LEFT$](../functions/left_dollar.md) - Return the leftmost N characters from a string
- [LEN](../functions/len.md) - Returns the number of characters in X$
- [MID$](../functions/mid_dollar.md) - Extract a substring from the middle of a string
- [OCT$](../functions/oct_dollar.md) - Returns a string which represents the octal value of the decimal argument
- [RIGHT$](../functions/right_dollar.md) - Return the rightmost N characters from a string
- [SPACE$](../functions/space_dollar.md) - Returns a string of I spaces
- [SPC](../functions/spc.md) - Prints I blanks on the terminal
- [STR$](../functions/str_dollar.md) - Convert a number to its string representation
- [STRING$](../functions/string_dollar.md) - Returns a string of length I whose characters all have ASCII code J or the first character of X$
- [VAL](../functions/val.md) - Returns the numerical value of string X$
