# Understanding Case Handling in MBASIC

## What is "Case Handling"?

MBASIC, like all classic BASIC interpreters, is **case-insensitive**. This means:

```basic
10 MyVariable = 5
20 myvariable = 10
30 MYVARIABLE = 15
```

All three lines refer to the **same variable**. The value is now 15.

But here's the new question: **Which spelling should MBASIC show you?** Should it be `MyVariable`, `myvariable`, or `MYVARIABLE`?

This is what "case handling" controls.

---

## Why Does This Matter?

### Problem 1: Accidental Typos

Imagine you're writing a program:

```basic
10 TotalCount = 0
20 FOR I = 1 TO 10
30   TotalCont = TotalCount + I   ← Typo! Missing 'u' in TotalCount
40 NEXT I
50 PRINT TotalCount
```

**What happens?**
- Without case conflict detection: Prints `0` (the loop creates a new variable `TotalCont` but never updates `TotalCount`!)
- With case conflict detection: Error at line 30 - catches the typo immediately

This is a **real bug** that's hard to spot. Case handling can catch it.

### Problem 2: Inconsistent Style

When copying code from different sources:

```basic
10 REM From Program A
20 PlayerScore = 100
30 REM From Program B
40 playerscore = 200
```

Is this one variable or two? (It's one!) But it looks confusing.

### Problem 3: Team Projects

When multiple people work on the same program, everyone may have different habits:

```basic
REM Person A likes: TargetAngle
REM Person B likes: targetangle
REM Person C likes: TARGETANGLE
```

Without case handling, the same variable appears three different ways in your code!

---

## How MBASIC Solves This

MBASIC gives you **two separate case handling systems**:

1. **Variable Case Handling** - Controls how variable names are displayed
2. **Keyword Case Handling** - Controls how keywords like PRINT, FOR, IF are displayed

You can configure each independently!

---

## Variable Case Handling

### Setting: `variables.case_conflict`

Controls what MBASIC does when the same variable appears with different cases.

### Option 1: `first_wins` (Default)

**What it does:** The first spelling you use becomes the official spelling.

```basic
10 TargetAngle = 45
20 targetangle = 90  ← MBASIC uses "TargetAngle" everywhere
30 PRINT TargetAngle  ← Displays "TargetAngle = 90"
```

**When to use:**
- Solo projects
- When you want freedom to type casually
- You're consistent naturally

**Pros:** Flexible, doesn't interrupt your work
**Cons:** Won't catch typos

### Option 2: `error`

**What it does:** Shows an error if you spell the same variable differently.

```basic
10 TotalCount = 0
20 TotalCont = TotalCont + 5  ← ERROR!
```

Error message:
```
Variable name case conflict: 'TotalCont' at line 20 vs 'TotalCount' at line 10
```

**When to use:**
- Team projects
- When you want to catch typos
- Professional/shared code

**Pros:** Catches bugs immediately
**Cons:** Requires fixing before running

### Option 3: `prefer_upper`

**What it does:** Always uses the version with MOST CAPITAL LETTERS.

```basic
10 targetangle = 45   ← 0 capital letters
20 TargetAngle = 90   ← 2 capital letters
30 TARGETANGLE = 100  ← 11 capital letters (winner!)
```

MBASIC shows: `TARGETANGLE = 100` everywhere

**When to use:**
- Classic BASIC style (retro computing)
- Want that vintage look

### Option 4: `prefer_lower`

**What it does:** Always uses the version with most lowercase letters.

```basic
10 COUNTER = 10  ← 7 capital letters
20 counter = 20  ← 7 lowercase letters (winner!)
```

MBASIC shows: `counter = 20`

**When to use:**
- Modern style (like Python)
- Easier to read for long sessions

### Option 5: `prefer_mixed`

**What it does:** Prefers camelCase or PascalCase style.

```basic
10 targetangle = 10   ← All lowercase
20 TARGETANGLE = 20   ← All uppercase
30 TargetAngle = 30   ← Mixed case (winner!)
```

MBASIC shows: `TargetAngle = 30`

**When to use:**
- Modern readable code
- Professional appearance
- Mixed with other languages

---

## Keyword Case Handling

### Setting: `keywords.case_style`

Controls how keywords (PRINT, FOR, IF, END, etc.) are displayed.

### Option 1: `force_lower` (Default)

**What it does:** All keywords shown in lowercase.

```basic
You type:    10 PRINT "hello"
             20 Print "world"
             30 print "!"

MBASIC shows: 10 print "hello"
              20 print "world"
              30 print "!"
```

**When to use:**
- Default MBASIC 5.21 style
- Matches original behavior

### Option 2: `force_upper`

**What it does:** All keywords shown in UPPERCASE.

```basic
You type:    10 print "hello"
             20 Print "world"

MBASIC shows: 10 PRINT "hello"
              20 PRINT "world"
```

**When to use:**
- Classic BASIC appearance
- Vintage computing feel
- Visually distinct from variables

### Option 3: `force_capitalize` ⭐ Popular!

**What it does:** Keywords shown as Capitalized (first letter uppercase).

```basic
You type:    10 PRINT "hello"
             20 for i = 1 to 10
             30 IF x = 5 THEN GOTO 100

MBASIC shows: 10 Print "hello"
              20 For i = 1 To 10
              30 If x = 5 Then Goto 100
```

**When to use:**
- Modern readable style
- Teaching/tutorials
- Professional documentation
- Easier on the eyes than ALL CAPS

**Why it's popular:**
- More readable than `PRINT` or `print`
- Looks professional
- Similar to modern languages
- Clear but not shouty

### Option 4: `first_wins`

**What it does:** First spelling of each keyword becomes official.

```basic
You type:    10 Print "hello"
             20 PRINT "world"

MBASIC shows: 10 Print "hello"
              20 Print "world"  ← Uses first spelling
```

**When to use:**
- You have a preferred style and stick to it
- Importing code from different sources

### Option 5: `error`

**What it does:** Error if same keyword spelled differently.

```basic
10 Print "hello"
20 PRINT "world"  ← ERROR: Keyword case conflict!
```

**When to use:**
- Enforcing strict style guidelines
- Team projects with coding standards

### Option 6: `preserve`

**What it does:** Every keyword stays exactly as you typed it.

```basic
You type:    10 PRINT "hello"
             20 print "world"
             30 Print "!"

MBASIC shows: 10 PRINT "hello"
              20 print "world"
              30 Print "!"
```

**When to use:**
- Maximum flexibility
- Artistic code formatting
- Special presentations

---

## Common Scenarios

### Scenario 1: Solo Hobbyist

**You want:** Freedom to code casually, no interruptions

**Settings:**
```basic
SET "variables.case_conflict" "first_wins"
SET "keywords.case_style" "force_lower"
```

**Result:** Type naturally, MBASIC handles everything silently.

---

### Scenario 2: Teaching/Tutorials

**You want:** Clear, readable code for students

**Settings:**
```basic
SET "variables.case_conflict" "prefer_mixed"
SET "keywords.case_style" "force_capitalize"
```

**Result:**
```basic
10 For Count = 1 To 10
20   Print "Number:"; Count
30 Next Count
```

Professional and easy to read!

---

### Scenario 3: Team Project

**You want:** Catch mistakes, enforce consistency

**Settings:**
```basic
SET "variables.case_conflict" "error"
SET "keywords.case_style" "force_capitalize"
```

**Result:** Any inconsistency is flagged immediately. Forces team to agree on style.

---

### Scenario 4: Retro/Vintage Look

**You want:** Classic BASIC appearance

**Settings:**
```basic
SET "variables.case_conflict" "prefer_upper"
SET "keywords.case_style" "force_upper"
```

**Result:**
```basic
10 FOR COUNT = 1 TO 10
20   PRINT "NUMBER:"; COUNT
30 NEXT COUNT
```

Looks like it came from a 1970s terminal!

---

### Scenario 5: Modern Python-like Style

**You want:** Contemporary programming feel

**Settings:**
```basic
SET "variables.case_conflict" "prefer_lower"
SET "keywords.case_style" "force_capitalize"
```

**Result:**
```basic
10 For counter = 1 To 10
20   Print "value:"; counter
30 Next counter
```

Familiar to modern programmers!

---

## How to Change Settings

### View Current Settings

```basic
SHOW SETTINGS
```

Shows all settings and their values.

### View Specific Category

```basic
SHOW SETTINGS "variables"
SHOW SETTINGS "keywords"
```

### Change a Setting

```basic
SET "variables.case_conflict" "error"
SET "keywords.case_style" "force_capitalize"
```

### Get Help on a Setting

```basic
HELP SET "variables.case_conflict"
HELP SET "keywords.case_style"
```

Shows detailed explanation and examples.

---

## Configuration Files

Settings can be saved to files for persistence:

### Global Settings (All Projects)

File: `~/.mbasic/settings.json`

```json
{
  "variables.case_conflict": "first_wins",
  "keywords.case_style": "force_lower"
}
```

### Project Settings (This Project Only)

File: `.mbasic/settings.json` (in your project directory)

```json
{
  "variables.case_conflict": "error",
  "keywords.case_style": "force_capitalize"
}
```

Project settings override global settings.

---

## Debugging Case Issues

### Problem: "Why does my variable look different than I typed?"

**Answer:** Check your `variables.case_conflict` setting.

```basic
SHOW SETTINGS "variables.case_conflict"
```

If it's `first_wins`, the first spelling is used everywhere.

### Problem: "I want to find all case variations of a variable"

**Answer:** Use the `error` policy temporarily:

```basic
SET "variables.case_conflict" "error"
RUN
```

MBASIC will show you exactly where different cases appear.

Then fix them or change back to your preferred policy.

### Problem: "Keywords look weird after editing"

**Answer:** Check your `keywords.case_style`:

```basic
SHOW SETTINGS "keywords.case_style"
```

Change it to your preference:

```basic
SET "keywords.case_style" "force_capitalize"
```

---

## Best Practices

### For Personal Projects

1. Use `first_wins` for variables (freedom)
2. Use `force_capitalize` for keywords (readability)
3. Be consistent within each program

### For Team Projects

1. Use `error` for variables (catch mistakes)
2. Agree on keyword style (document it)
3. Add settings to `.mbasic/settings.json` in project

### For Published Code

1. Use consistent style throughout
2. Consider `prefer_mixed` for variables
3. Use `force_capitalize` for keywords
4. Test with `error` policy before publishing

### For Teaching

1. Use `force_capitalize` for keywords
2. Use `prefer_mixed` for variables
3. Show students the settings
4. Explain why consistency matters

---

## Technical Background

### Why is BASIC Case-Insensitive?

Historical reasons:
1. **1960s-70s computers**: Many terminals were uppercase-only
2. **Simplicity**: Easier for beginners (no remembering exact case)
3. **Compatibility**: Code works regardless of how typed

### Why Add Case Handling Now?

Modern benefits:
1. **Better error detection**: Catch typos automatically
2. **Code readability**: Consistent style is easier to read
3. **Team collaboration**: Everyone sees same style
4. **Educational**: Teaches good programming habits

### Comparison to Other Languages

| Language | Case Sensitive? | Variable Display |
|----------|----------------|------------------|
| Python | Yes | Exactly as typed |
| JavaScript | Yes | Exactly as typed |
| SQL | No | Varies by tool |
| **BASIC** | No | **You choose!** |

MBASIC gives you the best of both worlds:
- Case-insensitive (easy for beginners)
- Configurable display (professional results)

---

## Real-World Example

Here's a complete program showing the difference:

### With Default Settings

```basic
10 REM Calculate average
20 Total = 0
30 FOR count = 1 TO 5
40   INPUT "Enter number"; num
50   total = total + num
60 NEXT count
70 Average = total / count
80 PRINT "Average is:"; average
90 END
```

Variables appear with mixed cases (first-seen). Hard to read.

### With Recommended Settings

```basic
SET "variables.case_conflict" "prefer_mixed"
SET "keywords.case_style" "force_capitalize"
```

Result:
```basic
10 Rem Calculate average
20 Total = 0
30 For Count = 1 To 5
40   Input "Enter number"; Num
50   Total = Total + Num
60 Next Count
70 Average = Total / Count
80 Print "Average is:"; Average
90 End
```

Much more professional and readable!

---

## Quick Reference Card

### Most Popular Combinations

**Beginner Friendly:**
```basic
SET "variables.case_conflict" "first_wins"
SET "keywords.case_style" "force_capitalize"
```

**Professional:**
```basic
SET "variables.case_conflict" "prefer_mixed"
SET "keywords.case_style" "force_capitalize"
```

**Strict/Team:**
```basic
SET "variables.case_conflict" "error"
SET "keywords.case_style" "force_capitalize"
```

**Vintage:**
```basic
SET "variables.case_conflict" "prefer_upper"
SET "keywords.case_style" "force_upper"
```

**Modern:**
```basic
SET "variables.case_conflict" "prefer_lower"
SET "keywords.case_style" "force_capitalize"
```

---

## Summary

Case handling is about **making your code look the way you want** while catching mistakes.

**Key Points:**
1. BASIC remains case-insensitive (that won't change)
2. You control how variables and keywords are displayed
3. Settings can catch typos and enforce style
4. Different settings for different situations
5. Configuration saved per-project or globally

**Start Here:**
```basic
SHOW SETTINGS
HELP SET "variables.case_conflict"
HELP SET "keywords.case_style"
```

Experiment until you find what works for you!

---

## See Also

- `SETTINGS_AND_CONFIGURATION.md` - Complete settings reference
- `TK_UI_QUICK_START.md` - Using the graphical interface
- `QUICK_REFERENCE.md` - All MBASIC commands
