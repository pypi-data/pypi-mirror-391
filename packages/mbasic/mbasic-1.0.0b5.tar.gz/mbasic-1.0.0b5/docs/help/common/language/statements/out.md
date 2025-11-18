---
category: hardware
description: To send a byte to a machine output port
keywords: ['command', 'data', 'for', 'number', 'out', 'put', 'statement']
syntax: OUT I,J
title: OUT
type: statement
---

# OUT

## Implementation Note

⚠️ **Emulated as No-Op**: This feature requires direct hardware I/O port access and is not implemented in this Python-based interpreter.

**Behavior**: Statement is parsed and executes successfully, but performs no operation

**Why**: Cannot access hardware I/O ports from a Python interpreter. OUT was used to control hardware devices through port-based I/O.

**Alternative**: There is no modern equivalent for hardware port I/O. For memory writes, use [POKE](poke.md), though note it also performs no actual operation.

**Historical Reference**: The documentation below is preserved from the original MBASIC 5.21 manual for historical reference.

---

## Syntax

```basic
OUT I,J
```

## Purpose

To send a byte to a machine output port.

## Remarks

I and J are integer expressions in the range 0 to 255. The integer expression I is the port number, and the integer expression J is the data to be transmitted.

## Example

```basic
100 OUT 32,100
```

## See Also
- [CALL](call.md) - To call an assembly language subroutine
- [POKE](poke.md) - To write a byte into a memory location
- [WAIT](wait.md) - To suspend program execution while monitoring the status of a machine input port
