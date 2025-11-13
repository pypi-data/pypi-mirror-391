10 REM Test immediate mode with arrays
20 REM Set breakpoint at line 130
30 REM At breakpoint, try:
40 REM   PRINT A(1)
50 REM   PRINT A(2)
60 REM   A(3) = 999
70 REM   PRINT A(3)
80 REM Then continue to see modified array value
90 REM
100 DIM A(10)
110 FOR I = 1 TO 10
120   A(I) = I * 10
130   PRINT "A("; I; ") ="; A(I)
140 NEXT I
150 REM
160 PRINT
170 PRINT "Sum of array elements:"
180 SUM = 0
190 FOR I = 1 TO 10
200   SUM = SUM + A(I)
210 NEXT I
220 PRINT "Total ="; SUM
230 END
