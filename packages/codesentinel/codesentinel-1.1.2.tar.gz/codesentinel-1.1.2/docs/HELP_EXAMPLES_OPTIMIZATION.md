# Help Examples Optimization Analysis

**Date:** November 11, 2025

## Current Examples: 23 Lines

Current help examples span 23 lines with several redundancies.

## Analysis: Redundancies & Consolidation

### GROUP 1: CLEAN COMMAND

Can reduce from 6 to 3 examples.

**Issue:** Lines with plain `clean` and `clean --dry-run` are redundant. Emoji examples (4-5) can consolidate.

**Optimized:**

- `codesentinel clean --all` - Clean everything
- `codesentinel clean --root` - Clean root directory
- `codesentinel clean --emojis --dry-run` - Preview emoji removal

**Savings:** 3 lines

---

### GROUP 2: SCHEDULE COMMAND

Keep both (2 examples) - `start` and `stop` are opposite operations.

**Savings:** 0 lines

---

### GROUP 3: UPDATE COMMAND

Can reduce from 3 to 2 examples.

**Issue:** Version bumping is specialized and discoverable via subcommand help.

**Optimized:**

- `codesentinel update docs` - Update repository documentation
- `codesentinel update changelog --version 1.2.3` - Update CHANGELOG

**Savings:** 1 line

---

### GROUP 4: INTEGRATE COMMAND

Can reduce from 3 to 2 examples.

**Issue:** Workflow targeting is discoverable in command help.

**Optimized:**

- `codesentinel integrate --new` - Integrate new commands
- `codesentinel integrate --all --dry-run` - Preview all

**Savings:** 1 line

---

### GROUP 5: DEV-AUDIT COMMAND

Replace 4 with 3 - add agent example, consolidate focus variations.

**Optimized:**

- `codesentinel dev-audit` - Run interactive audit
- `codesentinel dev-audit --agent` - Run with AI-assisted remediation
- `codesentinel !!!! --focus scheduler` - Quick audit (use --help for more)

**Savings:** 1 line (net) + adds critical agent feature

---

### GROUP 6: OTHER COMMANDS

Keep as-is (5 examples): status, scan, maintenance, alert

**Savings:** 0 lines

---

## Summary

| Group | Before | After | Saved |
|-------|--------|-------|-------|
| clean | 6 | 3 | 3 |
| update | 3 | 2 | 1 |
| integrate | 3 | 2 | 1 |
| dev-audit | 4 | 3 | 1 |
| **TOTAL** | **23** | **15** | **8 lines (35% reduction)** |

---

## Optimized Examples (15 lines)

```bash
codesentinel status                           # Show current status
codesentinel scan                             # Run security scan
codesentinel maintenance daily                # Run daily maintenance
codesentinel alert "Test message"             # Send test alert
codesentinel schedule start                   # Start maintenance scheduler
codesentinel schedule stop                    # Stop maintenance scheduler
codesentinel clean --all                      # Clean everything (cache, temp, logs)
codesentinel clean --root                     # Clean root directory violations
codesentinel clean --emojis --dry-run         # Preview emoji removal
codesentinel update docs                      # Update repository documentation
codesentinel update changelog --version 1.2.3 # Update CHANGELOG.md
codesentinel integrate --new                  # Integrate new CLI commands
codesentinel integrate --all --dry-run        # Preview integration opportunities
codesentinel dev-audit                        # Run interactive development audit
codesentinel dev-audit --agent                # Run with AI-assisted remediation
```

---

## Benefits

- **Clarity:** Removes confusing variations
- **Discovery:** Users find details in subcommand `--help`
- **Agent Showcase:** Highlights `--agent` integration feature
- **Maintenance:** Easier to keep examples in sync
- **Learning:** Cleaner focus on main use cases

---

## Implementation

Update lines 806-828 in `codesentinel/cli/__init__.py`

Regenerate help files: `codesentinel update help-files`
