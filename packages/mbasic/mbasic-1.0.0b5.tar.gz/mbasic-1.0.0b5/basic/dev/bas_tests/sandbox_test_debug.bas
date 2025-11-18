10 REM Test file I/O - write 3 lines, then read and print
20 PRINT "Opening file for output..."
30 OPEN "O", 1, "testfile.txt"
40 PRINT #1, "First line of text"
50 PRINT #1, "Second line of text"
60 PRINT #1, "Third line of text"
70 CLOSE 1
80 PRINT "File written. Now reading back..."
90 OPEN "I", 1, "testfile.txt"
95 PRINT "File opened. EOF ="; EOF(1)
100 IF EOF(1) THEN 140
110 LINE INPUT #1, A$
115 PRINT "Read line: "; A$
120 PRINT A$
130 GOTO 100
140 CLOSE 1
150 PRINT "Done reading file."
160 END
