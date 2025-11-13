# BASIC Language Reference

**Note:** This is a quick reference guide. For a beginner-friendly tutorial, see [Getting Started](getting-started.md). For complete statement and function documentation, see [Statements](language/statements/index.md) and [Functions](language/functions/index.md).

## Program Structure

BASIC programs consist of numbered lines:

```
10 REM This is a comment
20 PRINT "Hello, World!"
30 END
```

## Basic Commands

### Output

- **PRINT** - Display text or values
  - `PRINT "Hello"`
  - `PRINT X, Y, Z`

### Input

- **INPUT** - Get user input
  - `INPUT "Enter value"; X`
  - `INPUT A$`

### Assignment

- **LET** - Assign value (LET is optional)
  - `LET X = 10`
  - `A$ = "Hello"`

### Control Flow

- **GOTO** - Jump to line number
  - `GOTO 100`

- **GOSUB** / **RETURN** - Subroutine call
  - `GOSUB 1000`
  - `RETURN`

- **IF...THEN** - Conditional execution
  - `IF X > 10 THEN PRINT "Big"`
  - `IF A$ = "Y" THEN GOTO 100`

- **FOR...NEXT** - Loop
  - `FOR I = 1 TO 10`
  - `NEXT I`

### Data Types

- Numeric variables: `X`, `Y`, `COUNT`
- String variables: `A$`, `NAME$`
- Arrays: `DIM A(10)`, `DIM B$(20)`

## Functions

- **ABS(x)** - Absolute value
- **INT(x)** - Integer part
- **RND** - Random number (0-1)
- **SQR(x)** - Square root
- **SIN(x)**, **COS(x)**, **TAN(x)** - Trigonometry
- **LEN(s$)** - String length
- **LEFT$(s$,n)**, **RIGHT$(s$,n)**, **MID$(s$,start,len)** - Substrings

[Back to main help](index.md)
