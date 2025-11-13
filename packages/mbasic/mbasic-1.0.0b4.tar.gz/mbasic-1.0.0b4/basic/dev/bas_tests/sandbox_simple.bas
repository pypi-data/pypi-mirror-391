10 OPEN "O", 1, "test.txt"
20 PRINT #1, "Hello World"
30 CLOSE 1
40 PRINT "File written"
50 OPEN "I", 1, "test.txt"
60 LINE INPUT #1, A$
70 CLOSE 1
80 PRINT "Read: "; A$
90 END
