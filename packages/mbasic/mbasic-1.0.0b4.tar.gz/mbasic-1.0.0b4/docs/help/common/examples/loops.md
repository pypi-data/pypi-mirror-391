---
description: Examples of loops in BASIC - FOR, WHILE, and more
keywords:
- loops
- for
- while
- next
- wend
- example
title: Loop Examples
type: tutorial
---

# Loop Examples

Learn how to repeat actions using loops.

## FOR-NEXT Loops

The most common type of loop - repeats a fixed number of times.

### Counting to 10

```basic
10 FOR I = 1 TO 10
20   PRINT I
30 NEXT I
40 END
```

Output:
```
1
2
3
...
10
```

### Counting by Twos

```basic
10 FOR I = 2 TO 20 STEP 2
20   PRINT I
30 NEXT I
40 END
```

Output: `2 4 6 8 10 12 14 16 18 20`

### Counting Backwards

```basic
10 FOR I = 10 TO 1 STEP -1
20   PRINT I
30 NEXT I
40 PRINT "Blastoff!"
50 END
```

Output:
```
10
9
8
...
1
Blastoff!
```

### Multiplication Table

```basic
10 INPUT "Which table: ", N
20 FOR I = 1 TO 12
30   PRINT N; " x "; I; " = "; N * I
40 NEXT I
50 END
```

Example output:
```
Which table: 5
5 x 1 = 5
5 x 2 = 10
5 x 3 = 15
...
5 x 12 = 60
```

## WHILE-WEND Loops

Repeat while a condition is true.

### Keep Adding Until Over 100

```basic
10 SUM = 0
20 COUNT = 1
30 WHILE SUM < 100
40   SUM = SUM + COUNT
50   COUNT = COUNT + 1
60 WEND
70 PRINT "Final sum: "; SUM
80 PRINT "Numbers added: "; COUNT - 1
90 END
```

### Password Checker

```basic
10 PASSWORD$ = "SECRET"
20 ATTEMPTS = 0
30 WHILE ATTEMPTS < 3
40   INPUT "Enter password: ", GUESS$
50   IF GUESS$ = PASSWORD$ THEN GOTO 100
60   ATTEMPTS = ATTEMPTS + 1
70   PRINT "Wrong! Try again."
80 WEND
90 PRINT "Too many attempts!": END
100 PRINT "Access granted!"
110 END
```

## Nested Loops

Loops inside loops.

### Multiplication Table Grid

```basic
10 FOR ROW = 1 TO 10
20   FOR COL = 1 TO 10
30     PRINT ROW * COL;
40   NEXT COL
50   PRINT  ' Start new line
60 NEXT ROW
70 END
```

### Pattern Printing

```basic
10 FOR I = 1 TO 5
20   FOR J = 1 TO I
30     PRINT "*";
40   NEXT J
50   PRINT  ' New line
60 NEXT I
70 END
```

Output:
```
*
**
***
****
*****
```

## Arrays and Loops

Loops are perfect for working with arrays.

### Fill an Array

```basic
10 DIM NUMBERS(10)
20 FOR I = 1 TO 10
30   NUMBERS(I) = I * I
40 NEXT I
50 PRINT "Squares from 1 to 10:"
60 FOR I = 1 TO 10
70   PRINT I; "squared = "; NUMBERS(I)
80 NEXT I
90 END
```

### Sum Array Elements

```basic
10 DIM VALUES(5)
20 DATA 10, 20, 30, 40, 50
30 ' Fill array
40 FOR I = 1 TO 5
50   READ VALUES(I)
60 NEXT I
70 ' Calculate sum
80 SUM = 0
90 FOR I = 1 TO 5
100   SUM = SUM + VALUES(I)
110 NEXT I
120 PRINT "Total: "; SUM
130 END
```

## Breaking Out of Loops

Use GOTO to exit early from a loop.

**Note:** MBASIC 5.21 does not have EXIT FOR or EXIT WHILE statements (those were added in later BASIC versions). GOTO is the standard way to exit loops early in BASIC-80.

### Find First Match

```basic
10 DIM NAMES$(5)
20 DATA "Alice", "Bob", "Carol", "Dave", "Eve"
30 FOR I = 1 TO 5
40   READ NAMES$(I)
50 NEXT I
60 INPUT "Search for: ", SEARCH$
70 FOR I = 1 TO 5
80   IF NAMES$(I) = SEARCH$ THEN GOTO 120
90 NEXT I
100 PRINT "Not found!": END
120 PRINT "Found at position "; I
130 END
```

## Common Loop Mistakes

**Infinite WHILE loop:**
```basic
10 X = 0
20 WHILE X < 10
30   PRINT X   ' Forgot to increment X!
40 WEND
```
Fix: Add `X = X + 1` inside the loop

**Wrong STEP direction:**
```basic
10 FOR I = 10 TO 1    ' Will never run!
20   PRINT I
30 NEXT I
```
Fix: Use `STEP -1` to count backwards

**Modifying loop variable:**
```basic
10 FOR I = 1 TO 10
20   I = I + 1  ' DON'T DO THIS!
30 NEXT I
```
Fix: Use a different variable inside the loop

## See Also

- [FOR-NEXT Statement](../language/statements/for-next.md)
- [WHILE-WEND Statement](../language/statements/while-wend.md)
- [Arrays (DIM)](../language/statements/dim.md)
- [GOTO Statement](../language/statements/goto.md)
