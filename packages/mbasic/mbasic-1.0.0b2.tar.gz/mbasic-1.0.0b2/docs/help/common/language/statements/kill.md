---
category: file-management
description: To delete a file from disk
keywords: ['command', 'data', 'error', 'file', 'for', 'if', 'kill', 'open', 'program', 'read']
syntax: KILL <filename>
title: KILL
type: statement
---

# KILL

## Syntax

```basic
KILL <filename>
```

**Versions:** Disk

## Purpose

To delete a file from disk.

## Remarks

If a KILL statement is given for a file that is currently OPEN, a "File already open" error occurs (error code 55). KILL is used for all types of disk files: program files, random data files and sequential data files.

**Note**: CP/M automatically adds .BAS extension if none is specified when deleting BASIC program files.

## Example

```basic
10 KILL "TEMP.DAT"        ' Delete temporary file
20 KILL "OLD_DATA.TXT"    ' Delete old data file

' Delete file with error handling:
100 ON ERROR GOTO 200
110 INPUT "File to delete"; F$
120 KILL F$
130 PRINT "File deleted"
140 END
200 PRINT "Error: File not found or in use"
210 RESUME 140
```

## See Also
- [LOAD](load.md) - To load a file from disk into memory
- [MERGE](merge.md) - To merge a specified disk file into the      program currently in memory
- [NAME](name.md) - To change the name of a disk file
- [SAVE](save.md) - To save a program file on disk
