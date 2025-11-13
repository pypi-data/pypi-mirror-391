---
category: error-handling
description: To enable error trapping and specify the first line of the error handling subroutine
keywords: ['command', 'error', 'execute', 'for', 'goto', 'if', 'line', 'number', 'print', 'statement']
syntax: ON ERROR GOTO <line number>
title: ON ERROR GOTO
type: statement
---

# ON ERROR GOTO

## Syntax

```basic
ON ERROR GOTO <line number>
```

## Purpose

To enable error trapping and specify the first line of the error handling subroutine.

## Remarks

Once error trapping has been enabled, all errors detected, including direct mode errors (e.g., Syntax errors), will cause a jump to the specified error handling subroutine. If `<line number>` does not exist, an "Undefined line" error results.

To disable error trapping, execute an ON ERROR GOTO 0. Subsequent errors will print an error message and halt execution.

An ON ERROR GOTO 0 statement that appears in an error trapping subroutine causes BASIC-80 to stop and print the error message for the error that caused the trap. It is recommended that all error trapping subroutines execute an ON ERROR GOTO 0 if an error is encountered for which there is no recovery action.

**NOTE:** If an error occurs during execution of an error handling subroutine, the BASIC error message is printed and execution terminates. Error trapping does not occur within the error handling subroutine.

## Example

```basic
10 ON ERROR GOTO 1000
20 INPUT "Enter a number: "; N
30 PRINT "Result:"; 100 / N
40 END

1000 REM Error handler
1010 IF ERR = 11 THEN PRINT "Division by zero!"
1020 IF ERR = 13 THEN PRINT "Type mismatch!"
1030 RESUME NEXT
```

This example sets up error handling for division by zero and type mismatches.

## See Also
- [ERROR](error.md) - To simulate the occurrence of a BASIC-80 error or to allow error codes to be defined by the user
- [RESUME](resume.md) - Continue program execution after error recovery
- [ERR/ERL](err-erl-variables.md) - Error code and line number variables
