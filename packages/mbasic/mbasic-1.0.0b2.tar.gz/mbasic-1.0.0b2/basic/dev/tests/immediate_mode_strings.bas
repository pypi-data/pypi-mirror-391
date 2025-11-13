10 REM Test immediate mode with strings
20 REM Set breakpoint at line 100
30 REM At breakpoint, try:
40 REM   PRINT NAME$
50 REM   PRINT CITY$
60 REM   NAME$ = "Modified Name"
70 REM   PRINT NAME$
80 REM Then continue to see modified string
90 REM
100 NAME$ = "John Doe"
110 CITY$ = "San Francisco"
120 AGE = 25
130 PRINT "Name: "; NAME$
140 PRINT "City: "; CITY$
150 PRINT "Age: "; AGE
160 REM
170 PRINT
180 PRINT "Full info: "; NAME$; " from "; CITY$; ", age "; AGE
190 END
