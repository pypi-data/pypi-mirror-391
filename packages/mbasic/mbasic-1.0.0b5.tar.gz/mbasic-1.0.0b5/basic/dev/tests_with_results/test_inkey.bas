10 REM Test INKEY$ Function
20 PRINT "Testing INKEY$"
30 PRINT "=============="
40 PRINT
50 REM Test 1: INKEY$ returns empty string when no key pressed (automated test)
60 PRINT "Test 1: INKEY$ in non-interactive mode"
70 K$ = INKEY$
80 IF K$ = "" THEN PRINT "INKEY$ returns empty string (no input): PASS" ELSE PRINT "FAIL"
90 PRINT
100 REM Test 2: Multiple INKEY$ calls
110 PRINT "Test 2: Multiple INKEY$ calls"
120 K1$ = INKEY$
130 K2$ = INKEY$
140 K3$ = INKEY$
150 IF K1$ = "" AND K2$ = "" AND K3$ = "" THEN PRINT "Multiple calls return empty: PASS" ELSE PRINT "FAIL"
160 PRINT
170 REM Test 3: INKEY$ in a loop (simulating keyboard polling)
180 PRINT "Test 3: INKEY$ polling loop"
190 COUNT = 0
200 FOR I = 1 TO 10
210 K$ = INKEY$
220 IF K$ = "" THEN COUNT = COUNT + 1
230 NEXT I
240 IF COUNT = 10 THEN PRINT "Polling loop returns empty (no keys): PASS" ELSE PRINT "FAIL"
250 PRINT
260 REM Test 4: Type checking
270 PRINT "Test 4: INKEY$ returns string type"
280 K$ = INKEY$
290 REM String concatenation test - only works with strings
300 TEST$ = K$ + "X"
310 IF TEST$ = "X" THEN PRINT "String type confirmed: PASS" ELSE PRINT "FAIL"
320 PRINT
330 PRINT "INKEY$ tests complete!"
340 PRINT
350 PRINT "Note: INKEY$ is designed for interactive use."
360 PRINT "In automated tests (non-TTY), it returns empty string."
370 PRINT "For interactive testing, use a program that waits for keypresses."
380 END
