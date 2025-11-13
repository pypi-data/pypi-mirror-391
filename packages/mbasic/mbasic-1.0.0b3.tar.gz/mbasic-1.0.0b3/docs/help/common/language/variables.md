# Variables

Variables store data values that can change during program execution. MBASIC supports several variable types and provides flexible naming rules.

## Variable Naming Rules

Variable names in MBASIC:
- Must start with a letter (A-Z)
- Can contain letters, digits (0-9), and periods (.)
- Are limited to 40 characters
- Are not case-sensitive (ABC = abc = Abc)
- Cannot be reserved words (PRINT, FOR, etc.)

**Note on Variable Name Significance:** In the original MBASIC 5.21, only the first 2 characters of variable names were significant (AB, ABC, and ABCDEF would be the same variable). This Python implementation uses the full variable name for identification, allowing distinct variables like COUNT and COUNTER.

**Case Sensitivity:** Variable names are not case-sensitive by default (Count = COUNT = count), but the behavior when using different cases can be configured via the `variables.case_conflict` setting, which controls whether the first occurrence wins, an error is raised, or a specific case preference is applied.

## Variable Types

MBASIC supports four data types:

| Type | Range | Suffix | Bytes | Precision |
|------|-------|--------|-------|-----------|
| Integer | -32768 to 32767 | % | 2 | Exact |
| Single | ±2.93873E-39 to ±1.70141E+38 | ! | 4 | ~7 digits |
| Double | ±2.93873E-39 to ±1.70141D+38 | # | 8 | ~16 digits |
| String | 0 to 255 characters | $ | varies | N/A |

## Type Suffixes

Type suffixes explicitly declare variable types:

```basic
COUNT% = 100          ' Integer
NAME$ = "John"        ' String
PRICE! = 19.95        ' Single precision
TOTAL# = 123456.789   ' Double precision
```

If no suffix is used, variables default to single precision unless changed by DEF statements.

## Type Declaration Statements

You can set default types for variable names:

```basic
DEFINT I-N    ' Variables I through N default to integer
DEFSTR S      ' Variables starting with S default to string
DEFSNG A-H    ' Variables A through H default to single
DEFDBL D-E    ' Variables D through E default to double
```

Type suffixes override DEF declarations:
```basic
DEFINT I-N
I = 100       ' Integer (due to DEFINT)
I! = 100.5    ' Single (suffix overrides)
```

## Variable Assignment

Variables are assigned values using LET (optional) or direct assignment:

```basic
LET A = 10    ' Explicit LET
B = 20        ' Implicit assignment (LET is optional)
C$ = "Text"   ' String assignment
```

## Variable Scope

All variables in MBASIC are global throughout the program. There are no local variables.

Variables maintain their values until:
- Explicitly changed
- Program ends
- NEW command is issued
- RUN command is issued (clears all variables)

## Arrays

Arrays store multiple values under one variable name:

### Declaring Arrays

```basic
DIM A(10)           ' 11 elements: A(0) through A(10)
DIM B(5,5)          ' 36 elements: B(0,0) through B(5,5)
DIM NAME$(100)      ' 101 string elements
```

### Implicit Arrays

Arrays with 10 or fewer elements don't need DIM:
```basic
A(5) = 100          ' Creates array A(0) through A(10) automatically
```

### Array Bounds

Default lower bound is 0. Use OPTION BASE to change:
```basic
OPTION BASE 1       ' Arrays start at 1
DIM A(10)           ' Elements A(1) through A(10)
```

## Special Variables

Some variables have special meanings:

- **ERL** - Line number of last error (read-only)
- **ERR** - Error code of last error (read-only)

## Memory Considerations

- Integers use least memory (2 bytes)
- Strings use 3 bytes overhead + 1 byte per character
- Arrays require memory for all elements at declaration

## Examples

### Mixed Types
```basic
10 DEFINT I-N
20 COUNT = 0          ' Integer (DEFINT)
30 TOTAL# = 0         ' Double (suffix)
40 NAME$ = "Product"  ' String (suffix)
50 PRICE = 19.95      ' Single (default)
```

### Array Processing
```basic
10 DIM SCORES%(10)    ' Integer array
20 FOR I = 1 TO 10
30   INPUT "Score"; SCORES%(I)
40 NEXT I
```

### String Variables
```basic
10 FIRST$ = "John"
20 LAST$ = "Smith"
30 FULL$ = FIRST$ + " " + LAST$
40 PRINT FULL$        ' Prints: John Smith
```

## Common Pitfalls

1. **Case sensitivity**: Variable names are case-insensitive (see `variables.case_conflict` setting for handling conflicts)
2. **Type mismatches**: Assigning string to numeric variable causes error
3. **Array bounds**: Exceeding declared dimensions causes "Subscript out of range"
4. **Memory limits**: Too many variables can cause "Out of memory"

## See Also

- [Data Types](data-types.md) - Detailed type information
- [DIM](statements/dim.md) - Array declaration
- [DEFINT/SNG/DBL/STR](statements/defint-sng-dbl-str.md) - Type declarations
- [OPTION BASE](statements/option-base.md) - Set array lower bound
- [LET](statements/let.md) - Variable assignment
