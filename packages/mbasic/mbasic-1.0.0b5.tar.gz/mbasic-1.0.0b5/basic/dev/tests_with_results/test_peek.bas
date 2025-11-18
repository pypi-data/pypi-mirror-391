10 REM Test PEEK Function
20 PRINT "Testing PEEK"
30 PRINT "============"
40 PRINT
50 REM PEEK returns random value 0-255
60 PRINT "Test 1: PEEK returns values in range 0-255"
70 OK = 0
80 FOR I = 1 TO 20
90 V = PEEK(0)
100 IF V >= 0 AND V <= 255 THEN OK = OK + 1
110 NEXT I
120 PRINT "Tested 20 PEEK calls"
130 IF OK = 20 THEN PRINT "All values in range 0-255: PASS" ELSE PRINT "Some values out of range: FAIL"
140 PRINT
150 REM Test 2: PEEK accepts any address (ignored)
160 PRINT "Test 2: PEEK accepts various addresses"
170 A = PEEK(0)
180 B = PEEK(100)
190 C = PEEK(65535)
200 REM Check ranges without printing actual values
210 IF A >= 0 AND A <= 255 THEN PRINT "PEEK(0) in range 0-255: PASS" ELSE PRINT "PEEK(0) out of range: FAIL"
220 IF B >= 0 AND B <= 255 THEN PRINT "PEEK(100) in range 0-255: PASS" ELSE PRINT "PEEK(100) out of range: FAIL"
230 IF C >= 0 AND C <= 255 THEN PRINT "PEEK(65535) in range 0-255: PASS" ELSE PRINT "PEEK(65535) out of range: FAIL"
240 PRINT
250 REM Test 3: PEEK used for RND seeding (common pattern)
260 PRINT "Test 3: PEEK for random seeding pattern"
270 R = PEEK(0)
280 IF R >= 0 AND R <= 255 THEN PRINT "Random seed in range 0-255: PASS" ELSE PRINT "Random seed out of range: FAIL"
290 PRINT
300 PRINT "PEEK tests complete!"
310 END
