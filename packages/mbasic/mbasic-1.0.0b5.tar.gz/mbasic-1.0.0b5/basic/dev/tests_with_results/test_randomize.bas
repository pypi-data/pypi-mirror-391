10 REM Test RANDOMIZE statement
20 PRINT "Testing RANDOMIZE"
30 PRINT "================"
40 PRINT
50 PRINT "Test 1: RANDOMIZE with same seed gives same sequence"
60 RANDOMIZE 42
70 R1 = RND
80 R2 = RND
90 R3 = RND
100 REM Reset with same seed
110 RANDOMIZE 42
120 S1 = RND
130 S2 = RND
140 S3 = RND
150 IF R1 = S1 AND R2 = S2 AND R3 = S3 THEN PRINT "Same seed test: PASS" ELSE PRINT "Same seed test: FAIL"
160 PRINT
170 PRINT "Test 2: Different seeds give different sequences"
180 RANDOMIZE 123
190 D1 = RND
200 D2 = RND
210 RANDOMIZE 456
220 E1 = RND
230 E2 = RND
240 IF D1 <> E1 OR D2 <> E2 THEN PRINT "Different seed test: PASS" ELSE PRINT "Different seed test: FAIL"
250 PRINT
260 PRINT "Test 3: RND generates values between 0 and 1"
270 RANDOMIZE 99
280 PASS = 1
290 FOR I = 1 TO 10
300 V = RND
310 IF V < 0 OR V >= 1 THEN PASS = 0
320 NEXT I
330 IF PASS = 1 THEN PRINT "Range test: PASS" ELSE PRINT "Range test: FAIL"
340 PRINT
350 PRINT "RANDOMIZE tests complete!"
360 END
