# MBASIC Compiler Setup

## Requirements

### 1. z88dk Installation (Required)

The MBASIC compiler generates C code that must be compiled with z88dk to create CP/M executables for Z80.

**Important**: `z88dk.zcc` must be in your PATH for the compiler to work.

### 2. tnylpo Installation (Optional but Recommended)

tnylpo is a CP/M emulator for testing compiled programs. While not required for compilation, it's needed to run and test the generated .COM files.

**Important**: `tnylpo` must be in your PATH for test scripts to work.

### Installation Options

#### Option 1: Snap (Ubuntu/Debian)
```bash
sudo snap install z88dk

# Add snap binaries to PATH (add to ~/.bashrc or ~/.profile)
export PATH="$PATH:/snap/bin"
```

#### Option 2: Build from Source
```bash
git clone https://github.com/z88dk/z88dk.git
cd z88dk
./build.sh
export PATH="$PATH:$HOME/z88dk/bin"
```

#### Option 3: Docker
```bash
docker pull z88dk/z88dk
# Create wrapper script in PATH
echo '#!/bin/bash
docker run --rm -v "$PWD":/src -w /src z88dk/z88dk z88dk.zcc "$@"' > ~/bin/z88dk.zcc
chmod +x ~/bin/z88dk.zcc
```

### Verify Installation

#### Check z88dk
```bash
# Check that z88dk.zcc is in PATH
which z88dk.zcc

# Test with our utility
python3 utils/check_z88dk.py

# Test compilation
z88dk.zcc --version
```

#### Check tnylpo (if installed)
```bash
# Check that tnylpo is in PATH
which tnylpo

# Test with our utility
python3 utils/check_tnylpo.py
```

### tnylpo Installation

See `docs/dev/TNYLPO_SETUP.md` for detailed tnylpo installation instructions.

Quick install:
```bash
# Clone and build
git clone https://github.com/agn453/tnylpo.git
cd tnylpo
make
sudo make install  # Or copy to ~/bin and add to PATH
```

## Compiling BASIC Programs

### Step 1: Generate C Code
```bash
python3 test_compile.py program.bas
# Creates program.c
```

### Step 2: Compile to CP/M Executable
```bash
# For programs without strings
z88dk.zcc +cpm program.c -create-app -lm -o program

# For programs with strings (need mb25_string runtime)
z88dk.zcc +cpm program.c runtime/strings/mb25_string.c -create-app -lm -o program
```

This creates `PROGRAM.COM` that can run on CP/M systems.

## String Runtime Library

Programs that use strings require the mb25_string runtime library:

1. Copy `runtime/strings/mb25_string.h` and `runtime/strings/mb25_string.c` to your build directory
2. Include both files when compiling:
   ```bash
   z88dk.zcc +cpm program.c mb25_string.c -create-app -lm -o program
   ```

## Troubleshooting

### "z88dk.zcc: command not found"
- z88dk is not installed or not in PATH
- Run `echo $PATH` to check your PATH
- Run `find / -name z88dk.zcc 2>/dev/null` to locate the binary
- Add the directory containing z88dk.zcc to your PATH

### Compilation Errors
- Check that you're using the correct z88dk target: `+cpm` for CP/M
- For floating point, ensure `-lm` is included
- For strings, ensure mb25_string.c is included in compilation

## Compiler Implementation Note

The compiler uses `/usr/bin/env z88dk.zcc` to find the z88dk compiler in PATH. This approach is portable across different installation methods (snap, source build, docker, etc.) as long as `z88dk.zcc` is accessible in PATH.

See `src/codegen_backend.py:get_compiler_command()` for the implementation.