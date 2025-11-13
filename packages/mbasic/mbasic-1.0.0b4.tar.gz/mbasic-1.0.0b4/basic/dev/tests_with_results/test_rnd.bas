10 REM Test RND Random Number Function
20 REM Note: Random values change each run, so we test ranges only
30 PRINT "Testing RND (Random Numbers)"
40 PRINT "============================"
50 PRINT
60 REM Test 1: RND returns value between 0 and 1
70 PRINT "Test 1: RND range (should be 0 to 1)"
80 OK = 0
90 FOR I = 1 TO 5
100 X = RND
110 IF X >= 0 AND X < 1 THEN OK = OK + 1
120 NEXT I
130 PRINT OK; "out of 5 values in range [0, 1)"
140 PRINT
150 REM Test 2: Generate random integers in range 1-6 (dice)
160 PRINT "Test 2: Random integers 1-6 (dice roll)"
170 OK = 0
180 FOR I = 1 TO 10
190 D = INT(RND * 6) + 1
200 IF D >= 1 AND D <= 6 THEN OK = OK + 1
210 NEXT I
220 PRINT OK; "out of 10 values in range [1, 6]"
230 PRINT
240 REM Test 3: Random integers in different range (1-100)
250 PRINT "Test 3: Random integers 1-100"
260 OK = 0
270 FOR I = 1 TO 5
280 R = INT(RND * 100) + 1
290 IF R >= 1 AND R <= 100 THEN OK = OK + 1
300 NEXT I
310 PRINT OK; "out of 5 values in range [1, 100]"
320 PRINT
330 REM Test 4: RND in expressions
340 PRINT "Test 4: RND in expressions"
350 A = RND * 10
360 B = RND * 100
370 C = INT(RND * 20) + 10
380 OK = 0
390 IF A >= 0 AND A < 10 THEN OK = OK + 1
400 IF B >= 0 AND B < 100 THEN OK = OK + 1
410 IF C >= 10 AND C <= 29 THEN OK = OK + 1
420 PRINT OK; "out of 3 expressions in correct range"
430 PRINT
440 REM Test 5: Multiple RND calls in one line
450 PRINT "Test 5: Multiple RND in one expression"
460 S = RND + RND + RND
470 IF S >= 0 AND S < 3 THEN PRINT "Sum in range [0, 3): OK" ELSE PRINT "ERROR"
480 PRINT
490 REM Test 6: RND produces different values
500 PRINT "Test 6: RND produces variety"
510 A = RND
520 B = RND
530 C = RND
540 IF A <> B AND B <> C THEN PRINT "Values differ: OK" ELSE PRINT "WARNING: Same values"
550 PRINT
560 PRINT "RND tests complete!"
570 END
