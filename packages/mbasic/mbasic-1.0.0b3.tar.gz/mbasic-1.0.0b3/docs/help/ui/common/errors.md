# Error Handling

MBASIC provides error handling capabilities to help you manage runtime errors and create more robust programs.

## Basic Error Handling

When an error occurs during program execution, MBASIC normally stops the program and displays an error message. You can override this behavior using error handling statements.

### The ON ERROR GOTO Statement

Sets up an error handler that will be called when an error occurs:

```basic
10 ON ERROR GOTO 1000
20 INPUT "Enter a number: ", N
30 PRINT 100 / N
40 END
1000 PRINT "Error"; ERR; "occurred at line"; ERL
1010 RESUME NEXT
```

### Error Information Variables

- **ERR** - Contains the error code of the most recent error
- **ERL** - Contains the line number where the error occurred

### The RESUME Statement

Controls how to continue after handling an error:

- **RESUME** - Retry the statement that caused the error
- **RESUME NEXT** - Continue with the statement after the error
- **RESUME line-number** - Continue at a specific line

## Common Error Codes

| Code | Error | Common Cause |
|------|-------|--------------|
| 2 | Syntax error | Incorrect BASIC syntax |
| 5 | Illegal function call | Invalid parameter to function |
| 6 | Overflow | Number too large |
| 11 | Division by zero | Dividing by zero |
| 14 | Out of string space | Too many/large strings |
| 53 | File not found | Trying to open non-existent file |

## Error Handling Example

```basic
10 ON ERROR GOTO 100
20 INPUT "Filename"; F$
30 OPEN "I", 1, F$
40 INPUT #1, A$
50 PRINT A$
60 CLOSE #1
70 END
100 IF ERR = 53 THEN PRINT "File not found!"
110 IF ERR = 62 THEN PRINT "End of file!"
120 RESUME 70
```

## Best Practices

1. **Always provide error handlers for file operations**
2. **Check ERR to determine the specific error**
3. **Use ERL to identify where the error occurred**
4. **Clean up resources (close files) in error handlers**
5. **Test error handlers with intentional errors**

## Disabling Error Handling

To turn off error handling and return to normal error behavior:

```basic
ON ERROR GOTO 0
```

## See Also

- [ON ERROR GOTO](../../common/language/statements/on-error-goto.md) - Set up error handling
- [ERR and ERL](../../common/language/statements/err-erl-variables.md) - Error information
- [RESUME](../../common/language/statements/resume.md) - Continue after error
- [Error Codes](../../common/language/appendices/error-codes.md) - Complete error code reference
