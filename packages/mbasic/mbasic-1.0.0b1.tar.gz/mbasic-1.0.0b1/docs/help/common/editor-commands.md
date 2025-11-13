# Editor Commands

MBASIC provides a full-featured editor with commands for managing programs, debugging, and editing code.

## Command Categories

Each UI provides keyboard shortcuts and commands for:

### Program Management
- Run program
- Save/Load programs
- Create new program
- List program to output
- Open help system
- Quit IDE

### Debugging
- Run program
- Step through code (statement or line)
- Set/remove breakpoints
- Continue execution
- Stop execution
- View variables
- View execution stack

### Editing
- Navigate between lines
- Move cursor within lines
- Save and advance
- Delete characters
- Standard text editing operations

### Help Navigation
- Scroll through help
- Follow links
- Navigate topics
- Exit help

## UI-Specific Keyboard Shortcuts

**Important:** Keyboard shortcuts vary by UI. See your UI-specific help for the exact keybindings:

- **Tk UI:** See Tk UI help for complete keyboard shortcuts
- **Curses UI:** See Curses UI help for complete keyboard shortcuts
- **Web UI:** See Web UI help for complete keyboard shortcuts

Each UI uses different keys due to platform constraints (e.g., Curses can't use Ctrl+S for save as it's used for terminal flow control).

## General Tips

- Each UI provides help within the application - use the help command to access it
- Context-sensitive help is available for BASIC keywords
- Error messages can typically be cleared with ESC or similar key
- Mouse support varies by UI (Tk and Web have full mouse support)

## See Also

- [Getting Started](getting-started.md)
- [BASIC Language Reference](language/index.md)
- [Debugging Features](debugging.md)
