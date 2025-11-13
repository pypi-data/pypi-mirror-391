10 REM Test Binary Conversion Functions
20 REM MKI$, MKS$, MKD$ convert numbers to binary strings
30 REM CVI, CVS, CVD convert binary strings back to numbers
40 PRINT "Testing Binary Conversion"
50 PRINT "========================="
60 PRINT
70 REM Test 1: MKI$ and CVI (Integer)
80 PRINT "Test 1: MKI$ and CVI (Integer)"
90 N% = 12345
100 S$ = MKI$(N%)
110 PRINT "Original integer:"; N%
120 PRINT "Binary string length:"; LEN(S$)
130 R% = CVI(S$)
140 PRINT "Converted back:"; R%
150 IF R% = N% THEN PRINT "Match: OK" ELSE PRINT "ERROR"
160 PRINT
170 REM Test 2: MKS$ and CVS (Single precision)
180 PRINT "Test 2: MKS$ and CVS (Single)"
190 F! = 3.14159
200 S$ = MKS$(F!)
210 PRINT "Original single:"; F!
220 PRINT "Binary string length:"; LEN(S$)
230 R! = CVS(S$)
240 PRINT "Converted back:"; R!
250 PRINT
260 REM Test 3: MKD$ and CVD (Double precision)
270 PRINT "Test 3: MKD$ and CVD (Double)"
280 D# = 123.456789012345
290 S$ = MKD$(D#)
300 PRINT "Original double:"; D#
310 PRINT "Binary string length:"; LEN(S$)
320 R# = CVD(S$)
330 PRINT "Converted back:"; R#
340 PRINT
350 REM Test 4: Negative numbers
360 PRINT "Test 4: Negative numbers"
370 N% = -500
380 S$ = MKI$(N%)
390 R% = CVI(S$)
400 PRINT "Integer -500 -> binary -> back:"; R%
410 F! = -2.5
420 S$ = MKS$(F!)
430 R! = CVS(S$)
440 PRINT "Single -2.5 -> binary -> back:"; R!
450 PRINT
460 REM Test 5: Zero values
470 PRINT "Test 5: Zero values"
480 PRINT "MKI$(0) then CVI:"; CVI(MKI$(0))
490 PRINT "MKS$(0) then CVS:"; CVS(MKS$(0))
500 PRINT "MKD$(0) then CVD:"; CVD(MKD$(0))
510 PRINT
520 REM Test 6: Multiple conversions
530 PRINT "Test 6: Array of integers"
540 DIM A%(3)
550 A%(0) = 100 : A%(1) = 200 : A%(2) = 300
560 FOR I = 0 TO 2
570 S$ = MKI$(A%(I))
580 V% = CVI(S$)
590 PRINT "A%("; I; ") ="; A%(I); "-> binary ->"; V%;
600 IF V% = A%(I) THEN PRINT "OK" ELSE PRINT "ERROR"
610 NEXT I
620 PRINT
630 PRINT "Binary conversion tests complete!"
640 END
