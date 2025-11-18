10 REM ============================================
20 REM CONTINUE Feature Demonstration
30 REM ============================================
40 REM
50 REM Instructions:
60 REM 1. Set breakpoints on lines 100, 200, 300
70 REM 2. Run with Ctrl+R
80 REM 3. At each breakpoint, press 'c' to continue
90 REM
100 PRINT "PHASE 1: Initialization"
110 PRINT "Setting up variables..."
120 LET X = 10
130 LET Y = 20
140 LET Z = 30
150 PRINT "Variables: X="; X; " Y="; Y; " Z="; Z
160 PRINT "Phase 1 complete!"
170 PRINT
180 REM
190 REM Press 'c' at breakpoint 100 to jump here
200 PRINT "PHASE 2: Calculations"
210 PRINT "Computing sum..."
220 LET SUM = X + Y + Z
230 PRINT "Sum = "; SUM
240 PRINT "Computing product..."
250 LET PROD = X * Y
260 PRINT "Product = "; PROD
270 PRINT "Phase 2 complete!"
280 PRINT
290 REM
300 PRINT "PHASE 3: Loop demonstration"
310 PRINT "Counting from 1 to 5..."
320 FOR I = 1 TO 5
330   PRINT "  Count: "; I
340 NEXT I
350 PRINT "Phase 3 complete!"
360 PRINT
370 REM
380 PRINT "============================================"
390 PRINT "ALL PHASES COMPLETE!"
400 PRINT "============================================"
410 PRINT
420 PRINT "Notice how 'c' (continue) let you jump"
430 PRINT "between phases without seeing every line!"
440 END
