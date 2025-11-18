10 REM Test immediate mode after stopping (Ctrl+X or Ctrl+Q)
20 REM Run this program, then press stop while it's running
30 REM Try immediate mode commands:
40 REM   PRINT I
50 REM   PRINT TOTAL
60 REM   TOTAL = 999
70 REM Then continue to see modified value
80 REM
100 TOTAL = 0
110 PRINT "Summing numbers 1 to 100..."
120 PRINT "Press Ctrl+X to stop and inspect variables"
130 REM
140 FOR I = 1 TO 100
150   TOTAL = TOTAL + I
160   IF I MOD 10 = 0 THEN PRINT "Progress:"; I; "of 100, Total ="; TOTAL
170 NEXT I
180 REM
190 PRINT "Final total:"; TOTAL
200 END
