10 REM Test Ctrl+C interruption in single-line loop
20 REM This tests whether Ctrl+C can interrupt a tight loop
30 REM that's all on one line with multiple statements
40 REM
50 PRINT "=== Ctrl+C Interruption Test ==="
60 PRINT
70 PRINT "Test 1: Simple single-line loop"
80 PRINT "Press Ctrl+C to interrupt..."
90 FOR I = 1 TO 10 : PRINT "."; : NEXT I
100 PRINT
110 PRINT "Test 1 complete!"
120 PRINT
130 PRINT "Test 2: Long-running single-line loop"
140 PRINT "This will run for a while. Press Ctrl+C to interrupt..."
150 PRINT
160 FOR I = 1 TO 100000 : NEXT I
170 PRINT "Loop completed (or interrupted)"
180 PRINT
190 PRINT "Test 3: Nested single-line loop"
200 PRINT "Press Ctrl+C to interrupt..."
210 FOR I = 1 TO 5 : FOR J = 1 TO 10000 : NEXT J : PRINT I; : NEXT I
220 PRINT
230 PRINT "All tests complete!"
240 END
