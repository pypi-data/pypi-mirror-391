# OSC 8 Hyperlinks Design

**Date:** 2025-11-12
**Status:** Approved

## Overview

Add clickable hyperlinks to the rich terminal output using OSC 8 escape sequences. Member, team, and project names will link to their PLN Directory profile pages. GitHub handles will link to their GitHub profiles.

## Requirements

- **Entity profile links:** Member, team, and project names link to `directory.plnetwork.io` profiles
- **GitHub links:** All GitHub handles link to `github.com/{handle}`
- **Rich mode only:** OSC 8 codes only appear in rich/TTY output
- **No visual change:** Links are invisible escape codes; output looks identical
- **Generic helper:** Reusable link generation for future extensions

## Architecture

**Formatter-level implementation:** All hyperlink logic lives in `OutputFormatter` class in `formatters.py`.

**Rationale:** The formatter already controls rich vs. plain output mode detection. Adding OSC 8 encoding here keeps all presentation logic together without coupling URL generation to models or API client.

## URL Patterns

### PLN Directory URLs
- Members: `https://directory.plnetwork.io/members/{uid}`
- Teams: `https://directory.plnetwork.io/teams/{uid}`
- Projects: `https://directory.plnetwork.io/projects/{uid}`

### GitHub URLs
- All entities: `https://github.com/{github_handler}`

## OSC 8 Format

Standard OSC 8 escape sequence format:
```
\x1b]8;;{URL}\x07{TEXT}\x1b]8;;\x07
```

**Example:**
```python
# Visible text: "Molly Mackinlay"
# With link: "\x1b]8;;https://directory.plnetwork.io/members/abc123\x07Molly Mackinlay\x1b]8;;\x07"
```

## Implementation

### New Helper Methods (private)

**`_make_link(self, text: str, url: str) -> str`**
- Returns OSC 8 wrapped text in rich mode
- Returns plain text in plain/JSON modes
- Checks `self.format_type` to determine output mode

**`_make_directory_url(self, entity_type: str, uid: str) -> str`**
- Constructs PLN Directory profile URL
- `entity_type`: "members", "teams", or "projects"
- Returns full URL string

**`_make_github_url(self, github_handler: str) -> str`**
- Constructs GitHub profile URL
- Returns `https://github.com/{github_handler}`

### Modified Methods

**Rich formatters only:**
- `_format_member_rich()`: Wrap name + GitHub handle
- `_format_team_rich()`: Wrap team name
- `_format_project_rich()`: Wrap project name

**No changes to:**
- `_format_member_plain()`
- `_format_team_plain()`
- `_format_project_plain()`
- `format_json()`

## Example Output

**Visual appearance (unchanged):**
```
Members (3 results):

  Molly Mackinlay
    GitHub: momack2

  Kevin Houng
    GitHub: houngkevin
```

**Actual output (with OSC 8 codes):**
```
Members (3 results):

  \x1b]8;;https://directory.plnetwork.io/members/abc123\x07Molly Mackinlay\x1b]8;;\x07
    GitHub: \x1b]8;;https://github.com/momack2\x07momack2\x1b]8;;\x07
```

Clicking "Molly Mackinlay" opens her directory profile. Clicking "momack2" opens her GitHub profile.

## Terminal Support

OSC 8 is supported by:
- iTerm2 (macOS)
- GNOME Terminal (Linux)
- Windows Terminal
- VS Code integrated terminal
- Many others

Terminals without OSC 8 support ignore the escape codes and display plain text normally.

## Testing

- **Unit tests:** Test `_make_link()` returns correct OSC 8 codes in rich mode, plain text otherwise
- **Integration tests:** Test formatted output contains proper escape sequences
- **Manual testing:** Verify clickable links in iTerm2 or compatible terminal

## Future Extensions

The generic `_make_link()` helper enables easy addition of:
- Website URLs (if added to models)
- Twitter/X profile links
- Email addresses (mailto: links)
- Any other URL-text pairs

Simply call `_make_link(text, url)` when formatting additional fields.

## Files Modified

- `src/pln_search/formatters.py` - Add helper methods and update rich formatters
- `tests/test_formatters.py` - Add tests for OSC 8 link generation

## References

- OSC 8 Specification: https://gist.github.com/egmontkob/eb114294efbcd5adb1944c9f3cb5feda
- PLN Directory: https://directory.plnetwork.io/
