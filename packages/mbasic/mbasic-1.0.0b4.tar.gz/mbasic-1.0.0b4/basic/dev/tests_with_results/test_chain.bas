10 REM Test CHAIN Statement
20 PRINT "Testing CHAIN"
30 PRINT "=============="
40 PRINT
50 REM Test 1: CHAIN with ALL to preserve variables
60 PRINT "Test 1: CHAIN with ALL flag (preserves variables)"
70 X = 42
80 Y$ = "Hello"
90 PRINT "Before CHAIN: X ="; X; ", Y$ = "; Y$
100 PRINT
110 PRINT "About to CHAIN to /tmp/chain_target.bas"
120 CHAIN "/tmp/chain_target.bas", , ALL
130 REM Lines below will not execute - CHAIN replaces the program
140 PRINT "This line should never print"
150 END
