10 REM Advanced multi-statement line test
20 REM Tests breakpoints and stepping through multi-statement lines
30 REM
40 PRINT "=== Advanced Multi-Statement Test ==="
50 PRINT
60 REM Test 1: Multiple assignments and calculations
70 A = 5 : B = 10 : C = A * B : D = C / 2
80 PRINT "A="; A; " B="; B; " C="; C; " D="; D
90 PRINT
100 REM Test 2: Nested FOR loops on one line (if supported)
110 FOR I = 1 TO 2 : FOR J = 1 TO 2 : PRINT I; ","; J; " "; : NEXT J : PRINT : NEXT I
120 PRINT
130 REM Test 3: Multiple IF/THEN on one line
140 X = 7 : IF X > 5 THEN Y = 1 : PRINT "Y="; Y
150 PRINT
160 REM Test 4: Array operations on one line
170 DIM A(3)
180 A(0) = 10 : A(1) = 20 : A(2) = 30 : A(3) = 40
190 PRINT "A(0)="; A(0); " A(3)="; A(3)
200 PRINT
210 REM Test 5: String operations on one line
220 A$ = "HELLO" : B$ = "WORLD" : C$ = A$ + " " + B$
230 PRINT C$
240 PRINT
250 REM Test 6: Single-line loop (can be interrupted with Ctrl+C)
260 REM Uncomment the next line to test interruption:
270 REM FOR I = 1 TO 1000000 : NEXT I
280 PRINT
290 PRINT "=== Test Complete ==="
300 END
