---
category: file-io
description: To input an entire line to a string variable without delimiters
keywords: ['command', 'for', 'if', 'input', 'line', 'print', 'put', 'return', 'statement', 'string']
syntax: LINE INPUT [;"prompt string";]<string variable>
title: LINE INPUT
type: statement
---

# LINE INPUT

## Syntax

```basic
LINE INPUT [;"prompt string";]<string variable>
```

## Purpose

To input an entire line (up to 254 characters) to a string variable, without the use of delimiters.

## Remarks

The prompt string is a string literal that is printed at the terminal before input is accepted. A question mark is not printed unless it is part of the prompt string. All input from the end of the prompt to the carriage return is assigned to `<string variable>`.

If LINE INPUT is immediately followed by a semicolon (before the prompt string), then the carriage return typed by the user to end the input line does not echo a carriage return/line feed sequence at the terminal. This is the same behavior as with INPUT.

A LINE INPUT may be escaped by typing Control-C. BASIC-80 will return to command level and type Ok. Typing CONT resumes execution at the LINE INPUT.

## Example

```basic
10 LINE INPUT "Enter your full name: "; NAME$
20 LINE INPUT "Enter your address: "; ADDR$
30 PRINT
40 PRINT "Name: "; NAME$
50 PRINT "Address: "; ADDR$
```

Output:
```
Enter your full name: John Doe
Enter your address: 123 Main Street, Anytown USA

Name: John Doe
Address: 123 Main Street, Anytown USA
```

Note: LINE INPUT accepts the entire line including commas and quotes without requiring delimiters.

## See Also
- [INPUT](input.md) - Read input from keyboard with delimiters
- [LINE INPUT#](inputi.md) - Read an entire line from a file
- [INPUT$](../functions/input_dollar.md) - Read a specified number of characters
- [INKEY$](../functions/inkey_dollar.md) - Read a single character without waiting
