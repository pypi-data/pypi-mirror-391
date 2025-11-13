---
category: type-conversion
description: Converts X to an integer by rounding the fractional portion
keywords: ['cint', 'data', 'error', 'for', 'function', 'if', 'number', 'print', 'return']
syntax: CINT(X)
title: CINT
type: function
---

# CINT

## Syntax

```basic
CINT(X)
```

**Versions:** Extended, Disk

## Description

Converts X to an integer by rounding the fractional portion. If X is not in the range -32768 to 32767, an "Overflow" error occurs.

## Example

```basic
10 PRINT CINT(45.67)
RUN
46
Ok

10 PRINT CINT(12.3), CINT(12.5), CINT(12.9)
RUN
12  13  13
Ok
```

## Notes

CINT rounds to the nearest integer (.5 rounds up). If you need truncation instead of rounding, use FIX or INT.

## See Also
- [CDBL](cdbl.md) - Converts X to a double-precision floating-point number
- [CSNG](csng.md) - Converts X to a single-precision floating-point number
