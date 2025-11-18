---
category: string
description: Prints I blanks on the terminal
keywords: ['function', 'print', 'spc', 'statement']
syntax: SPC (I)
title: SPC
type: function
---

# SPC

## Syntax

```basic
SPC (I)
```

## Description

Prints I blanks on the terminal. SPC may only be used with PRINT and LPRINT statements. I must be in the range 0 to 255.

## Example

```basic
PRINT "OVER" SPC(15) "THERE"
```

Output:
```
OVER               THERE
```

## See Also
- [SPACE$](space_dollar.md) - Returns a string of spaces
- [TAB](tab.md) - Move to specific column position
- [PRINT](../statements/print.md) - Output to screen
- [LPRINT](../statements/lprint-lprint-using.md) - Output to printer
- [POS](pos.md) - Get current cursor position
