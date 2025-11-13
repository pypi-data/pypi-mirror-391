---
category: system
description: Display help for a specific setting
keywords: ['help', 'setting', 'documentation', 'describe']
syntax: HELPSETTING "setting.name"
title: HELPSETTING
type: statement
related: ['setsetting', 'showsettings']
---

# HELPSETTING

## Syntax

```basic
HELPSETTING "setting.name"
```

**Versions:** MBASIC Extension

## Purpose

To display detailed help information for a specific interpreter setting.

## Remarks

HELPSETTING displays comprehensive documentation for a named setting, including:
- Full setting name
- Description of what the setting controls
- Valid values and data type
- Default value
- Scope (session, user, system)
- Related settings
- Usage examples

This is useful for understanding what a setting does before changing it, or for discovering the valid values for a setting.

## Example

```basic
HELPSETTING "display.width"
HELPSETTING "editor.tab_size"

10 INPUT "Setting name"; S$
20 HELPSETTING S$
30 INPUT "New value"; V
40 SETSETTING S$ V
```

## Notes

- This is a modern extension not present in original MBASIC 5.21
- Setting names are case-insensitive
- Unknown setting names produce an error message
- Use SHOWSETTINGS to discover available setting names

## See Also
- [SETSETTING](setsetting.md) - Configure interpreter settings
- [SHOWSETTINGS](showsettings.md) - Display all current settings
- [LIMITS](limits.md) - Display resource usage and limits
