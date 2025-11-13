---
description: Your first BASIC program - Hello World
keywords:
- hello world
- example
- first program
- beginner
title: Hello World Example
type: tutorial
---

# Hello World Example

The classic first program in any language.

## The Program

```basic
10 PRINT "Hello, World!"
20 END
```

## How It Works

**Line 10:** `PRINT "Hello, World!"`
- The PRINT statement outputs text to the screen
- Text in quotes is displayed exactly as written
- The semicolon at the end is optional

**Line 20:** `END`
- Tells BASIC to stop running the program
- Always good practice to end programs with END

## Running the Program

1. Type each line (the line number, then the statement)
2. Press Enter after each line
3. Type `RUN` and press Enter
4. You should see: `Hello, World!`

## Variations

### With Variables

```basic
10 MESSAGE$ = "Hello, World!"
20 PRINT MESSAGE$
30 END
```

### With Input

```basic
10 INPUT "Enter your name: ", NAME$
20 PRINT "Hello, "; NAME$; "!"
30 END
```

When you run this:
```
Enter your name: Alice
Hello, Alice!
```

### Multiple Greetings

```basic
10 PRINT "Hello, World!"
20 PRINT "Welcome to BASIC!"
30 PRINT "Let's learn programming!"
40 END
```

## Common Mistakes

**Forgetting the quotes:**
```basic
10 PRINT Hello, World!    ' ERROR: Syntax error
```
Must use quotes for text: `PRINT "Hello, World!"`

**Missing line numbers:**
```basic
PRINT "Hello"    ' ERROR: Syntax error
```
Every program line needs a number: `10 PRINT "Hello"`

## Next Steps

Now that you've written your first program, try:
- [Loop Examples](loops.md) - Repeating actions
- [Variables](../language/data-types.md) - Storing data
- [INPUT Statement](../language/statements/input.md) - Getting user input

## See Also

- [PRINT Statement](../language/statements/print.md)
- [END Statement](../language/statements/end.md)
- [Getting Started](../getting-started.md)
