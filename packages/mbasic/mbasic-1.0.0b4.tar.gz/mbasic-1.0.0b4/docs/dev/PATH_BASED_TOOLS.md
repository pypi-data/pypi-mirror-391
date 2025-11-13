# PATH-Based Tool Requirements

## Overview

The MBASIC compiler toolchain uses `/usr/bin/env` to find required tools in PATH. This approach ensures portability across different installation methods and operating systems.

## Required Tools

### z88dk (Required)
- **Purpose**: Compiles generated C code to CP/M executables
- **Binary**: `z88dk.zcc`
- **Used by**: Compiler backend (`src/codegen_backend.py`)
- **Invocation**: `/usr/bin/env z88dk.zcc`
- **Check**: `python3 utils/check_z88dk.py`

### tnylpo (Optional but Recommended)
- **Purpose**: CP/M emulator for testing compiled programs
- **Binary**: `tnylpo`
- **Used by**: Test scripts (`test_compile/test_compile.py`)
- **Invocation**: `/usr/bin/env tnylpo`
- **Check**: `python3 utils/check_tnylpo.py`

## Quick Setup Check

Run this single command to verify your toolchain:
```bash
python3 utils/check_compiler_tools.py
```

## Why PATH-Based?

### Portability
- Works with any installation location
- No hardcoded paths to maintain
- Users choose their preferred installation method

### Installation Flexibility
Supports all these installation methods:
- System package managers (when available)
- Snap packages (add `/snap/bin` to PATH)
- Building from source
- Docker containers with wrapper scripts
- Custom installations in `~/bin` or elsewhere

### Standard Practice
- `/usr/bin/env` is the standard Unix/Linux way to find executables
- Used by shebangs in scripts worldwide
- Respects user's PATH preferences

## PATH Configuration

### Check Your PATH
```bash
echo $PATH
```

### Add Directory to PATH

#### Temporary (current session only)
```bash
export PATH="$PATH:/new/directory"
```

#### Permanent (add to ~/.bashrc or ~/.profile)
```bash
echo 'export PATH="$PATH:/new/directory"' >> ~/.bashrc
source ~/.bashrc
```

### Common Directories to Add

- **Snap binaries**: `/snap/bin`
- **User binaries**: `$HOME/bin` or `~/bin`
- **Local binaries**: `/usr/local/bin`
- **Custom tools**: Any directory with your tools

## Implementation Details

### Code Changes

#### z88dk Compiler Path
```python
# Before (hardcoded):
return ['/snap/bin/z88dk.zcc', '+cpm', ...]

# After (PATH-based):
return ['/usr/bin/env', 'z88dk.zcc', '+cpm', ...]
```

#### tnylpo Emulator Path
```python
# Before (direct call):
subprocess.run(['tnylpo', com_file])

# After (PATH-based):
subprocess.run(['/usr/bin/env', 'tnylpo', com_file])
```

### Files Modified
- `src/codegen_backend.py` - z88dk compiler invocation
- `test_compile/test_compile.py` - tnylpo emulator invocation

### Documentation Created
- `docs/dev/COMPILER_SETUP.md` - z88dk installation guide
- `docs/dev/TNYLPO_SETUP.md` - tnylpo installation guide
- `docs/dev/COMPILER_Z88DK_PATH_CHANGE.md` - z88dk path change details
- `docs/dev/PATH_BASED_TOOLS.md` - This document

### Utilities Created
- `utils/check_z88dk.py` - Verify z88dk installation
- `utils/check_tnylpo.py` - Verify tnylpo installation
- `utils/check_compiler_tools.py` - Check entire toolchain

## Troubleshooting

### Tool Not Found
If `/usr/bin/env` can't find a tool:

1. **Check if installed**: `which toolname`
2. **Check PATH**: `echo $PATH`
3. **Find the tool**: `find / -name toolname 2>/dev/null`
4. **Add to PATH**: See "PATH Configuration" above

### Permission Denied
If tool exists but won't run:

1. **Check permissions**: `ls -l /path/to/tool`
2. **Make executable**: `chmod +x /path/to/tool`

### Wrong Version Found
If wrong version is in PATH:

1. **Check which is found**: `which -a toolname`
2. **Check PATH order**: Earlier directories take precedence
3. **Adjust PATH order or use full path temporarily

## Benefits Summary

1. **No configuration needed** - Works out of the box if tools are in PATH
2. **Cross-platform** - Same code works on Linux, macOS, WSL, etc.
3. **User choice** - Install tools however you prefer
4. **Future-proof** - New installation methods automatically supported
5. **Standard practice** - Follows Unix/Linux conventions

## See Also

- [COMPILER_SETUP.md](COMPILER_SETUP.md) - Complete compiler setup guide
- [TNYLPO_SETUP.md](TNYLPO_SETUP.md) - tnylpo installation guide
- [UTILITY_SCRIPTS_INDEX.md](https://github.com/avwohl/mbasic/blob/main/utils/UTILITY_SCRIPTS_INDEX.md) - Check utilities