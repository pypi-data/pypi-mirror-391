# Cross-Platform Output Encoding Policy

**Classification**: T0 - Constitutional (Security & Reliability)  
**Status**: Permanent Directive  
**Date**: November 11, 2025  
**Scope**: All CodeSentinel output operations

---

## Issue Summary

**Problem**: Unicode characters (✓, ✗, →, etc.) in console output cause `UnicodeEncodeError` on Windows platforms using CP-1252 encoding.

**Root Cause**: Windows console default encoding (cp1252) cannot represent Unicode characters outside the ASCII range. Python's `print()` function on Windows attempts to encode strings using the console's default encoding, causing crashes when Unicode symbols are encountered.

**Impact**: Complete script failure when Unicode symbols are used in status messages, logging, or reports.

---

## Incident Details

### What Happened

During Phase 2 implementation of the satellite instruction management system:

1. **Initial Implementation**: Used Unicode check/cross symbols (✓/✗) in output
2. **Failure Point**: `manage_satellites.py` crashed with `UnicodeEncodeError: 'charmap' codec can't encode character '\u2713'`
3. **Attempted Fix**: Tried wrapping stdout with UTF-8 encoding using `io.TextIOWrapper`
4. **Result**: Partial success but garbled output in PowerShell
5. **Final Solution**: Replaced all Unicode symbols with ASCII-safe alternatives (`[OK]`, `[FAIL]`)

### Files Affected

- `tools/codesentinel/manage_satellites.py`
- `tools/codesentinel/defrag_instructions.py`

### Error Traceback

```
UnicodeEncodeError: 'charmap' codec can't encode character '\u2713' in position 0: character maps to <undefined>
  File "...\encodings\cp1252.py", line 19, in encode
    return codecs.charmap_encode(input,self.errors,encoding_table)[0]
```

---

## Permanent Policy: ASCII-Safe Output

### Core Principle

**ALL user-facing output must use ASCII-safe characters (0x00-0x7F) only.**

### Rationale

1. **Platform Independence**: ASCII is universally supported across all platforms and encodings
2. **Reliability**: No encoding-related crashes regardless of console configuration
3. **Consistency**: Output appears identical on Windows, macOS, Linux
4. **Minimalism**: Simple, robust solution without complex encoding handling

### Approved Symbol Mappings

| Purpose | ❌ FORBIDDEN | ✅ APPROVED |
|---------|-------------|-------------|
| Success/OK | ✓ ✔ ☑ | `[OK]` `PASS` `SUCCESS` |
| Failure/Error | ✗ ✘ ☒ | `[FAIL]` `ERROR` `FAILED` |
| Warning | ⚠ ⚡ | `[WARN]` `WARNING` |
| Info | ℹ ➡ | `[INFO]` `->` `=>` |
| Bullet points | • ● ○ | `-` `*` |
| Arrows | → ← ↑ ↓ | `->` `<-` `^` `v` |
| Checkboxes | ☐ ☑ | `[ ]` `[x]` |

### Implementation Requirements

1. **Console Output**: Use only ASCII characters in `print()`, `logger.info()`, etc.
2. **File Output**: UTF-8 is acceptable for files (`.md`, `.txt`, `.json`) as they are not console-bound
3. **Error Messages**: ASCII-safe error messages only
4. **Progress Indicators**: Use ASCII characters (`[=====>    ]` not `█░░░░`)

---

## Prevention Strategy

### Code Review Checklist

Before committing any code with console output:

- [ ] No Unicode symbols (✓✗→←•) in `print()` statements
- [ ] No Unicode symbols in `logger.*()` statements
- [ ] No Unicode symbols in exception messages
- [ ] All status indicators use ASCII alternatives

### Automated Detection

Add to pre-commit hooks or linting:

```python
# Forbidden Unicode symbols in Python files
FORBIDDEN_SYMBOLS = ['✓', '✗', '→', '←', '•', '●', '○', '☑', '☐', '⚠']

def check_ascii_output(file_content: str) -> bool:
    """Verify no forbidden Unicode symbols in output statements."""
    for symbol in FORBIDDEN_SYMBOLS:
        if symbol in file_content:
            return False
    return True
```

### Developer Guidelines

1. **Default to ASCII**: When adding any console output, use ASCII characters first
2. **Test on Windows**: If developing on macOS/Linux, test on Windows before committing
3. **Documentation Exception**: Markdown documentation files (`.md`) CAN use Unicode for readability
4. **Configuration Files**: JSON/TOML/YAML files can use UTF-8 safely

---

## Technical Background

### Why Windows is Different

- **Unix/macOS**: Default UTF-8 encoding for console
- **Windows**: Default CP-1252 (or CP-850) encoding, limited to Western European characters
- **Python Behavior**: Uses `sys.stdout.encoding` which reflects console encoding

### Why UTF-8 Wrapping Failed

```python
# This approach is fragile:
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
```

**Problems**:

1. PowerShell still displays garbled output (encoding mismatch)
2. Doesn't work with redirected output or piped commands
3. Breaks some IDE consoles
4. Adds complexity and failure points

**ASCII approach is superior**: Simple, robust, universal.

---

## Migration Guide

### Converting Existing Code

**Before**:

```python
print(f"✓ Task completed successfully")
print(f"✗ Task failed")
logger.info(f"Processing file → {path}")
```

**After**:

```python
print(f"[OK] Task completed successfully")
print(f"[FAIL] Task failed")
logger.info(f"Processing file -> {path}")
```

### Exception: Documentation

Markdown files can safely use Unicode:

```markdown
<!-- This is FINE in .md files -->
✓ Feature implemented
✗ Known limitation
→ Next steps
```

---

## Testing Requirements

All new features with console output must:

1. **Pass on Windows**: Test on Windows 10/11 PowerShell and cmd.exe
2. **Pass on Linux**: Test on Ubuntu/Debian with standard terminal
3. **Pass on macOS**: Test on macOS terminal
4. **Pass Redirected**: Test `python script.py > output.txt`
5. **Pass Piped**: Test `python script.py | grep pattern`

---

## Related Policies

- **T0-1: Security First** - Reliability is a security concern (crashed scripts expose vulnerabilities)
- **T3-1: Minimalism** - ASCII-only output is the minimal, simplest solution
- **T4a: Platform Independence** - All CodeSentinel operations must be platform-independent

---

## Version History

- **2025-11-11**: Initial policy created after Phase 2 encoding incident
