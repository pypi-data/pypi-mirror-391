10 REM Test Math Rounding Functions
20 REM Tests INT, FIX, CINT and their differences
30 PRINT "Testing Math Rounding Functions"
40 PRINT "================================"
50 PRINT
60 REM Test INT - rounds down to next lowest integer
70 PRINT "INT function (rounds toward negative infinity):"
80 PRINT "INT(2.3) ="; INT(2.3); "(expected: 2)"
90 PRINT "INT(2.7) ="; INT(2.7); "(expected: 2)"
100 PRINT "INT(-2.3) ="; INT(-2.3); "(expected: -3)"
110 PRINT "INT(-2.7) ="; INT(-2.7); "(expected: -3)"
120 PRINT "INT(5.0) ="; INT(5.0); "(expected: 5)"
130 PRINT "INT(0.9) ="; INT(0.9); "(expected: 0)"
140 PRINT "INT(-0.9) ="; INT(-0.9); "(expected: -1)"
150 PRINT
160 REM Test FIX - truncates toward zero
170 PRINT "FIX function (truncates toward zero):"
180 PRINT "FIX(2.3) ="; FIX(2.3); "(expected: 2)"
190 PRINT "FIX(2.7) ="; FIX(2.7); "(expected: 2)"
200 PRINT "FIX(-2.3) ="; FIX(-2.3); "(expected: -2)"
210 PRINT "FIX(-2.7) ="; FIX(-2.7); "(expected: -2)"
220 PRINT "FIX(5.0) ="; FIX(5.0); "(expected: 5)"
230 PRINT "FIX(0.9) ="; FIX(0.9); "(expected: 0)"
240 PRINT "FIX(-0.9) ="; FIX(-0.9); "(expected: 0)"
250 PRINT
260 REM Test CINT - rounds to nearest integer (banker's rounding)
270 PRINT "CINT function (rounds to nearest integer):"
280 PRINT "CINT(2.3) ="; CINT(2.3); "(expected: 2)"
290 PRINT "CINT(2.7) ="; CINT(2.7); "(expected: 3)"
300 PRINT "CINT(-2.3) ="; CINT(-2.3); "(expected: -2)"
310 PRINT "CINT(-2.7) ="; CINT(-2.7); "(expected: -3)"
320 PRINT "CINT(5.0) ="; CINT(5.0); "(expected: 5)"
330 PRINT "CINT(0.9) ="; CINT(0.9); "(expected: 1)"
340 PRINT "CINT(-0.9) ="; CINT(-0.9); "(expected: -1)"
350 PRINT
360 REM Test CINT with .5 values (banker's rounding - round to even)
370 PRINT "CINT with .5 values (banker's rounding):"
380 PRINT "CINT(2.5) ="; CINT(2.5); "(expected: 2 - round to even)"
390 PRINT "CINT(3.5) ="; CINT(3.5); "(expected: 4 - round to even)"
400 PRINT "CINT(4.5) ="; CINT(4.5); "(expected: 4 - round to even)"
410 PRINT "CINT(5.5) ="; CINT(5.5); "(expected: 6 - round to even)"
420 PRINT "CINT(-2.5) ="; CINT(-2.5); "(expected: -2 - round to even)"
430 PRINT "CINT(-3.5) ="; CINT(-3.5); "(expected: -4 - round to even)"
440 PRINT
450 REM Test differences between INT and FIX
460 PRINT "Key difference - INT vs FIX with negatives:"
470 PRINT "INT(-2.7) ="; INT(-2.7); ", FIX(-2.7) ="; FIX(-2.7)
480 PRINT "INT rounds DOWN, FIX truncates TOWARD ZERO"
490 PRINT
500 REM Test type suffix behavior
510 PRINT "Testing integer type suffix (%):"
520 A% = 10.7
530 B% = 20.3
540 C% = -5.9
550 PRINT "A% = 10.7 becomes"; A%; "(uses CINT)"
560 PRINT "B% = 20.3 becomes"; B%; "(uses CINT)"
570 PRINT "C% = -5.9 becomes"; C%; "(uses CINT)"
580 PRINT
590 REM Edge cases
600 PRINT "Edge cases:"
610 PRINT "INT(0) ="; INT(0)
620 PRINT "FIX(0) ="; FIX(0)
630 PRINT "CINT(0) ="; CINT(0)
640 PRINT "INT(1) ="; INT(1)
650 PRINT "FIX(1) ="; FIX(1)
660 PRINT "CINT(1) ="; CINT(1)
670 PRINT
680 PRINT "Test complete!"
690 END
