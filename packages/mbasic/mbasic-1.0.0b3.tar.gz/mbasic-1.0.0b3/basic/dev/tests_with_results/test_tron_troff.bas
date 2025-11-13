10 REM Test TRON/TROFF Trace Mode
20 PRINT "Testing TRON/TROFF"
30 PRINT "=================="
40 PRINT
50 REM Test 1: Normal execution without trace
60 PRINT "Test 1: Without trace"
70 A = 10 : B = 20 : C = A + B
80 PRINT "Result:"; C
90 PRINT
100 REM Test 2: TRON with single statements per line
110 PRINT "Test 2: TRON with single statements"
120 TRON
130 X = 5
140 Y = 10
150 Z = X * Y
160 PRINT "Result:"; Z
170 TROFF
180 PRINT
190 REM Test 3: TRON with multiple statements per line
200 PRINT "Test 3: TRON with multiple statements"
210 TRON
220 A = 1 : B = 2 : C = 3
230 D = A + B : E = C + D
240 PRINT "A="; A; "B="; B; "C="; C
250 PRINT "D="; D; "E="; E
260 TROFF
270 PRINT
280 REM Test 4: Trace with IF statement
290 PRINT "Test 4: TRON with IF/THEN"
300 TRON
310 IF A < 5 THEN PRINT "Less" ELSE PRINT "More"
320 TROFF
330 PRINT
340 REM Test 5: Trace with loops
350 PRINT "Test 5: TRON with FOR loop"
360 TRON
370 FOR I = 1 TO 3 : PRINT I; : NEXT I
380 TROFF
390 PRINT
400 PRINT
410 REM Test 6: Trace with GOSUB
420 PRINT "Test 6: TRON with GOSUB"
430 TRON
440 GOSUB 1000 : PRINT "Back"
450 TROFF
460 PRINT
470 REM Test 7: Turn trace on and off multiple times
480 PRINT "Test 7: Toggle TRON/TROFF"
490 TRON : X = 100 : TROFF
500 Y = 200
510 TRON : Z = X + Y : TROFF
520 PRINT "Final:"; Z
530 PRINT
540 PRINT "TRON/TROFF tests complete!"
550 END
560 REM
1000 REM Subroutine
1010 S = 99 : PRINT "In sub, S="; S
1020 RETURN
