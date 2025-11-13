10 REM Test Error Handling (ON ERROR, RESUME, ERR, ERL)
20 PRINT "Testing Error Handling"
30 PRINT "======================"
40 PRINT
50 REM Test 1: Basic error trap with RESUME NEXT
60 PRINT "Test 1: ON ERROR with RESUME NEXT"
70 ON ERROR GOTO 1000
80 PRINT "Before error"
90 X = 10 / 0
100 PRINT "After error (via RESUME NEXT)"
110 ON ERROR GOTO 0
120 GOTO 200
130 REM
1000 REM Error handler - RESUME NEXT
1010 PRINT "Error caught! ERR ="; ERR
1020 RESUME NEXT
1030 REM
200 REM Test 2: RESUME to retry the error line
210 PRINT
220 PRINT "Test 2: RESUME to retry (with fix)"
230 Y = 0
240 ON ERROR GOTO 2000
250 Z = 10 / Y
260 PRINT "Division succeeded: 10 /"; Y; "="; Z
270 ON ERROR GOTO 0
280 GOTO 300
290 REM
2000 REM Fix Y and retry
2010 PRINT "Error! Setting Y=2 and retrying"
2020 Y = 2
2030 RESUME
2040 REM
300 REM Test 3: RESUME to specific line number
310 PRINT
320 PRINT "Test 3: RESUME to specific line"
330 ON ERROR GOTO 3000
340 A = 5 / 0
350 PRINT "Skipped line"
360 PRINT "Target line reached"
370 ON ERROR GOTO 0
380 GOTO 400
390 REM
3000 REM Resume to line 360
3010 PRINT "Resuming to line 360"
3020 RESUME 360
3030 REM
400 REM Test 4: Check ERR and ERL values
410 PRINT
420 PRINT "Test 4: Check ERR and ERL values"
430 ON ERROR GOTO 4000
440 B = 7 / 0
450 GOTO 500
460 REM
4000 REM Display error info
4010 PRINT "ERR ="; ERR; "(division by zero)"
4020 PRINT "ERL ="; ERL; "(should be 440)"
4030 RESUME 500
4040 REM
500 REM Test 5: Disable error trapping
510 PRINT
520 PRINT "Test 5: ON ERROR GOTO 0 (disable)"
530 ON ERROR GOTO 5000
540 C = 10 / 2
550 PRINT "No error: 10 / 2 ="; C
560 ON ERROR GOTO 0
570 GOTO 600
580 REM
5000 PRINT "ERROR: Handler called when it shouldn't!"
5010 END
5020 REM
600 REM Test 6: Multiple errors with counter
610 PRINT
620 PRINT "Test 6: Count multiple errors"
630 EC = 0
640 ON ERROR GOTO 6000
650 D = 1 / 0
660 E = 2 / 0
670 F = 3 / 0
680 PRINT "Errors caught:"; EC
690 ON ERROR GOTO 0
700 GOTO 800
710 REM
6000 REM Count and continue
6010 EC = EC + 1
6020 RESUME NEXT
6030 REM
800 PRINT
810 PRINT "Error handling tests complete!"
820 END
