---
category: control-flow
description: To branch to multiple line numbers based on expression value
keywords: ['branch', 'command', 'error', 'for', 'function', 'gosub', 'goto', 'if', 'line', 'next']
syntax: ON <expression> GOTO <list of line numbers>
title: ON...GOSUB/ON...GOTO
type: statement
---

# ON...GOSUB/ON...GOTO

## Syntax

```basic
ON <expression> GOTO <list of line numbers>
ON <expression> GOSUB <list of line numbers>
```

**Versions:** 8K, Extended, Disk

## Purpose

To branch to one of several specified line numbers, depending on the value returned when an expression is evaluated.

## Remarks

The value of `<expression>` determines which line number in the list will be used for branching. For example, if the value is three, the third line number in the list will be the destination of the branch. (If the value is a non-integer, the fractional portion is rounded.)

In the ON...GOSUB statement, each line number in the list must be the first line number of a subroutine.

If the value of `<expression>` is zero or greater than the number of items in the list (but less than or equal to 255), BASIC continues with the next executable statement. If the value of `<expression>` is negative or greater than 255, an "Illegal function call" error occurs.

## Example

```basic
100 ON L-1 GOTO 150,300,320,390
```

## See Also
- [FOR...NEXT](for-next.md) - Execute statements repeatedly with a loop counter
- [GOSUB...RETURN](gosub-return.md) - Branch to and return from a subroutine
- [GOTO](goto.md) - Branch unconditionally to a specified line number
- [IF...THEN...ELSE](if-then-else-if-goto.md) - Make decisions and control program flow based on conditional expressions
- [WHILE...WEND](while-wend.md) - Execute statements in a loop while a condition is true
