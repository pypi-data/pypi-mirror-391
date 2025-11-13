10 REM Test breakpoints with multi-statement lines
20 REM This tests whether breakpoints stop at the right statement
30 REM when a line contains multiple statements
40 REM
50 REM Instructions:
60 REM 1. Set a breakpoint on line 100
70 REM 2. Run the program
80 REM 3. Use Step Statement to advance through each statement
90 REM 4. Observe which statement is highlighted
100 REM
110 PRINT "=== Breakpoint Multi-Statement Test ==="
120 PRINT
130 REM Set a breakpoint on the next line and step through
140 A = 1 : B = 2 : C = 3 : D = 4 : E = 5
150 PRINT "A="; A; " B="; B; " C="; C; " D="; D; " E="; E
160 PRINT
170 REM Set a breakpoint here and step through
180 PRINT "First"; : PRINT " Second"; : PRINT " Third"
190 PRINT
200 REM Set a breakpoint here for loop statements
210 FOR I = 1 TO 3 : PRINT "I="; I; : NEXT I
220 PRINT
230 REM Set a breakpoint here for conditional statements
240 X = 10 : IF X > 5 THEN PRINT "Large"; : PRINT " Value"
250 PRINT
260 REM Set a breakpoint here for GOSUB
270 PRINT "Before"; : GOSUB 310 : PRINT "After"
280 PRINT
290 PRINT "=== Test Complete ==="
300 GOTO 330
310 REM Subroutine
320 PRINT " Middle"; : RETURN
330 END
