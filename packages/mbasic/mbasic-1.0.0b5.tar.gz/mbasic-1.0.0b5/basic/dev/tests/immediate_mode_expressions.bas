10 REM Test immediate mode with expressions and calculations
20 REM Set breakpoint at line 100
30 REM At breakpoint, try:
40 REM   PRINT X + Y
50 REM   PRINT X * Y
60 REM   PRINT SQR(X)
70 REM   PRINT X > Y
80 REM   Z = X + Y + 5
90 REM   PRINT Z
100 REM
110 X = 25
120 Y = 36
130 PRINT "X ="; X
140 PRINT "Y ="; Y
150 REM
160 PRINT "X + Y ="; X + Y
170 PRINT "X * Y ="; X * Y
180 PRINT "SQR(Y) ="; SQR(Y)
190 END
