10 REM Test immediate mode with single-step debugging
20 REM Use Ctrl+T to step through the program
30 REM After each step, check variables in immediate mode
40 REM Try:
50 REM   PRINT A
60 REM   PRINT B
70 REM   PRINT C
80 REM
100 A = 10
110 PRINT "A ="; A
120 B = 20
130 PRINT "B ="; B
140 C = A + B
150 PRINT "C ="; C
160 REM
170 A = A * 2
180 PRINT "A doubled ="; A
190 B = B + 5
200 PRINT "B + 5 ="; B
210 C = A - B
220 PRINT "C (A-B) ="; C
230 END
