# Compiler z88dk Path Change

## Change Summary
Changed from hardcoded snap path to portable PATH-based lookup.

## Before
```python
return ['/snap/bin/z88dk.zcc', '+cpm', source_file, '-create-app', '-lm', '-o', output_file]
```

## After
```python
return ['/usr/bin/env', 'z88dk.zcc', '+cpm', source_file, '-create-app', '-lm', '-o', output_file]
```

## Benefits
1. **Portability**: Works with any z88dk installation method (snap, source build, docker, etc.)
2. **Flexibility**: Users can install z88dk however they prefer
3. **Standard Practice**: Using `/usr/bin/env` is the standard Unix way to find executables in PATH
4. **No Configuration**: No need to configure compiler paths or modify code for different systems

## User Requirements
- z88dk must be installed
- `z88dk.zcc` must be in PATH
- Can verify with: `which z88dk.zcc`

## Installation Methods Supported
All of these now work as long as the binary is in PATH:
- Snap: `sudo snap install z88dk` (add /snap/bin to PATH)
- Source: Build from GitHub
- Docker: With wrapper script
- Package manager: Any future package manager installations
- Custom: Any custom installation location

## Implementation
See: `src/codegen_backend.py:get_compiler_command()`

This change makes the compiler more user-friendly and follows Unix best practices for finding executables.