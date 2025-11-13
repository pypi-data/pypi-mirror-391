10 REM Test immediate mode at breakpoint
20 REM Set breakpoint at line 60, then run
30 REM At breakpoint, try:
40 REM   PRINT X
50 REM   PRINT Y
60 REM   X = 100
70 REM   PRINT X
80 REM Then continue (Ctrl+G) to see X=100 used
90 REM
100 X = 10
110 Y = 20
120 PRINT "Before loop: X ="; X; ", Y ="; Y
130 REM
140 FOR I = 1 TO 5
150   X = X + I
160   Y = Y * 2
170   PRINT "Loop"; I; ": X ="; X; ", Y ="; Y
180 NEXT I
190 REM
200 PRINT "After loop: X ="; X; ", Y ="; Y
210 END
