---
category: type-conversion
description: Converts X to a double-precision floating-point number
keywords: ['cdbl', 'convert', 'double', 'precision', 'float', 'function', 'number']
syntax: CDBL(X)
related: ['cint', 'csng', 'fix', 'int']
title: CDBL
type: function
---

# CDBL

## Syntax

```basic
CDBL(X)
```

**Versions:** Extended, Disk

## Description

Converts X to a double-precision floating-point number. Double-precision numbers have approximately 16 digits of precision and range from approximately ±2.938736×10^-308 to ±1.797693×10^308.

If X is a single-precision number or integer, it is converted to double-precision format. If X is a string representation of a number, it is converted to double-precision format.

## Example

```basic
10 A! = 123.456!
20 B# = CDBL(A!)
30 PRINT A!, B#
RUN
123.456  123.456
Ok

10 PRINT CDBL(5)
RUN
5
Ok
```

## Notes

- Single-precision numbers use ! as a type suffix
- Double-precision numbers use # as a type suffix
- Converting from single to double precision preserves all available precision

## See Also
- [CINT](cint.md) - Converts X to an integer by rounding the fractional portion
- [CSNG](csng.md) - Converts X to a single-precision floating-point number
- [FIX](fix.md) - Returns the truncated integer part of X
- [INT](int.md) - Return the largest integer less than or equal to a number (floor function)
