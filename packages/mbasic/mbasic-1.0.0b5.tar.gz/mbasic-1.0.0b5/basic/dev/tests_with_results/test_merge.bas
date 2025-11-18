10 REM Test MERGE Statement
20 PRINT "Testing MERGE"
30 PRINT "============="
40 PRINT
50 REM Test 1: Basic MERGE
60 PRINT "Test 1: MERGE overlay program"
70 PRINT "Main program lines: 10-200"
80 PRINT
90 REM Merge an overlay file that adds lines 1000-2020
100 MERGE "/tmp/merge_overlay.bas"
110 PRINT
120 PRINT "Test 2: Call merged subroutine"
130 GOSUB 1000
140 PRINT
150 PRINT "Test 3: Call second merged subroutine"
160 GOSUB 2000
170 PRINT
180 PRINT "MERGE tests complete!"
190 END
