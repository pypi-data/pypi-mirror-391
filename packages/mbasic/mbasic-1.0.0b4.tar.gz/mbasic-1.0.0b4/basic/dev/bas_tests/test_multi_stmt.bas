10 REM Test program for multi-statement line highlighting
20 REM This tests the statement-level debugging feature
30 REM
40 PRINT "=== Multi-Statement Line Test ==="
50 PRINT
60 REM Simple multi-statement line with PRINT
70 PRINT "A"; : PRINT "B"; : PRINT "C"
80 PRINT
90 REM Multi-statement with variables
100 A = 10 : B = 20 : C = A + B
110 PRINT "A="; A; " B="; B; " C="; C
120 PRINT
130 REM Multi-statement with FOR loop
140 FOR I = 1 TO 3 : PRINT "I="; I : NEXT I
150 PRINT
160 REM Multi-statement with IF/THEN
170 X = 5 : IF X > 3 THEN PRINT "X is large" : PRINT "X="; X
180 PRINT
190 REM Multi-statement with GOTO
200 A = 1 : PRINT "Before GOTO" : GOTO 220
210 PRINT "Skipped"
220 PRINT "After GOTO"
230 PRINT
240 REM Multi-statement with GOSUB
250 PRINT "Before GOSUB" : GOSUB 280 : PRINT "After GOSUB"
260 PRINT
270 GOTO 300
280 PRINT "  In subroutine" : RETURN
290 REM
300 PRINT "=== Test Complete ==="
310 END
