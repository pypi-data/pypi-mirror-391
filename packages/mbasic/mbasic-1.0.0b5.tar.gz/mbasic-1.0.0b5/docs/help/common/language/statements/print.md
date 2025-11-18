---
title: PRINT
type: statement
category: input-output
keywords: ['print', 'output', 'display', 'console', 'write', 'show', 'terminal', 'question mark']
aliases: ['?']
description: Output text and values to the screen
syntax: PRINT [expression[;|,]...]
related: ['input', 'print-using', 'write', 'lprint']
---

# PRINT

## Syntax

```basic
PRINT [<list of expressions>]
```

**Versions:** 8K, Extended, Disk

## Purpose

To output data at the terminal.

## Remarks

`<list of expressions>` consists of the numeric and/or string expressions to be printed.

### Print Positions

The position of each printed item is determined by the punctuation used to separate the items in the list:

- **Semicolon (;)** - No spaces between items
- **Comma (,)** - Advance to next print zone (every 14 columns)
- **No punctuation at end** - New line after print
- **Semicolon at end** - No new line after print

### Special Forms

- **PRINT by itself** - Prints a blank line
- **?** - Shorthand for PRINT

### Print Zones

When items are separated by commas, values are printed in zones of 14 columns each:
- Columns 1-14 (first zone)
- Columns 15-28 (second zone)
- Columns 29-42 (third zone)
- Columns 43-56 (fourth zone)
- Columns 57-70 (fifth zone)

If a value is too long for a zone, it will be printed in the next zone.

### Numeric Output

Numbers are printed with:
- A leading space for positive numbers (where minus sign would go)
- A minus sign for negative numbers
- A trailing space

## Example

```basic
10 PRINT "Hello, World!"
20 PRINT "The answer is"; 42
30 PRINT "First", "Second", "Third"  ' Tab-separated
40 X = 5: Y = 10
50 PRINT X; "+"; Y; "="; X + Y
60 PRINT    ' Blank line
70 ? "This also works"  ' ? is shorthand for PRINT
```

Output:
```
Hello, World!
The answer is 42
First         Second        Third
 5 + 10 = 15

This also works
```

## See Also
- [PRINT USING](lprint-lprint-using.md) - Formatted output
- [INPUT](input.md) - Read user input
- [WRITE](write.md) - Output data with delimiters
- [LPRINT](lprint-lprint-using.md) - Print to line printer
- [PRINT#](printi-printi-using.md) - Write to file