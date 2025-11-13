# Printf Elimination Investigation - TODO

## Status: Future Optimization - Investigate Later

## Background

We've already optimized PRINT statements to use direct character output (putchar/fputc) instead of malloc+printf+free, saving ~16% code size. However, printf family functions are still linked into the binary due to other usage.

## Current Printf/Sprintf Usage

### Already Linked (No savings from eliminating printf for output)

The following uses of sprintf mean printf formatting code is **already linked**:

1. **Number-to-String Conversion (STR$, HEX$, OCT$)**
   - `sprintf(_str, "%g", num)` for STR$() - line 2463, 2899
   - `sprintf(_hex, "%X", num)` for HEX$() - line 2493, 2928
   - `sprintf(_oct, "%o", num)` for OCT$() - line 2501, 2935
   - **These are necessary for BASIC functionality**

2. **PRINT USING formatting**
   - `sprintf(_out, "%.*f", _decimals, _val)` - line 2239
   - `sprintf(_out, "%.0f", _val)` - line 2243
   - Complex numeric formatting required by BASIC spec

3. **DATA/READ numeric conversion**
   - `sprintf(_num_str, "%g", data_numeric[data_pointer])` - line 1451

### Could Replace (Minimal/No Code Size Benefit)

Since printf is already linked via sprintf, these replacements save little/no code:

1. **Numeric PRINT output** (~10 occurrences)
   ```c
   printf("%g\n", value)      → sprintf(buf, "%g", value); putchar loop
   fprintf(fp, "%d", val)     → sprintf(buf, "%d", val); fputc loop
   ```
   **Benefit**: Minimal (printf already linked)

2. **Error messages to stderr** (~8 occurrences)
   ```c
   fprintf(stderr, "?Out of memory\n")  → fputs("?Out of memory\n", stderr)
   ```
   **Benefit**: Small - eliminates fprintf variant, keeps printf

3. **Simple prompts** (~5 occurrences)
   ```c
   printf("? ")      → fputs("? ", stdout) or putchar('?'); putchar(' ')
   printf("\n")      → putchar('\n')  [already done for PRINT]
   ```
   **Benefit**: Minimal (printf already linked)

4. **ANSI escape codes**
   ```c
   printf("\033[2J\033[H")  → fputs("\033[2J\033[H", stdout)
   ```
   **Benefit**: Minimal

## Options for True Printf Elimination

### Option 1: Keep Current Approach ✅ (Recommended for now)
- Printf already linked via sprintf
- Replacing printf() calls saves minimal space
- PRINT statements already optimized (putchar)
- **Effort**: None
- **Benefit**: Already achieved main optimization

### Option 2: Replace sprintf with Custom Functions
Write custom number formatting to eliminate entire printf family:

**Required Functions:**
- `itoa()` / `utoa()` - integer to ASCII
- `ftoa()` - float to ASCII (complex!)
  - Need to handle: exponential notation, precision, rounding
  - BASIC STR$() uses "%g" format (shortest representation)
- `itoah()` - integer to hex (for HEX$)
- `itoo()` - integer to octal (for OCT$)

**Affected Code:**
- STR$() function (~2 places)
- HEX$() function (~2 places)
- OCT$() function (~2 places)
- PRINT USING numeric formatting (~3 places)
- DATA/READ conversion (~1 place)

**Effort**: High
- Implementing ftoa() with proper rounding/precision is complex
- Need to match BASIC's "%g" format exactly
- Test extensively for edge cases (very small/large numbers)

**Benefit**: Could save 1-2KB if printf family completely eliminated
- Depends on z88dk's printf implementation size
- May not be worth effort vs. benefit

### Option 3: Hybrid Approach
- Keep sprintf for float formatting (complex)
- Write custom itoa for integers (simple)
- Could eliminate some printf variants

**Effort**: Medium
**Benefit**: Small (sprintf for floats already pulls in most printf code)

## Investigation Tasks

1. **Measure printf family code size**
   - Compile minimal test with/without printf
   - Compile minimal test with/without sprintf
   - Determine actual size of printf formatting code

2. **Check z88dk alternatives**
   - Does z88dk provide lightweight printf variants?
   - Are there #defines to reduce printf features?
   - Research z88dk printf library options

3. **Profile actual usage**
   - Which printf features are actually used? (%, g, d, X, o, .*f)
   - Could we use a smaller printf subset?

4. **Test feasibility**
   - Implement basic ftoa() prototype
   - Measure code size vs. printf
   - Check if it's worth the complexity

## Recommendation

**Defer this optimization** until:
1. We've measured the actual size impact (investigation task #1)
2. We've exhausted other optimization opportunities
3. Code size is still a critical constraint

The current approach (putchar for PRINT, sprintf for conversions) is a good balance of simplicity vs. optimization.

## References

- Original optimization discussion: See conversation where we eliminated malloc and optimized PRINT
- Size test results: putchar approach saved 1206 bytes (16%) over printf
- Printf already linked: sprintf() required for STR$/HEX$/OCT$ functions

## Related Files

- `src/codegen_backend.py` - All printf/sprintf usage
- `size_test_*.c` - Size comparison tests showing putchar savings
