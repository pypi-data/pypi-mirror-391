# AI Agent Development Rules

**Permanent behavioral requirements for all AI-assisted development on CodeSentinel.**

## Rule 1: Pre-Edit File State Validation

**Status:** MANDATORY  
**Applies to:** All file editing operations  
**Effective:** Immediately

### Requirement

Before invoking any file editing tool (`replace_string_in_file`, `edit_notebook_file`, etc.):

1. **READ FIRST** - Use `read_file` to inspect current file state
2. **VERIFY CONTEXT** - Confirm the code you're about to edit actually exists
3. **CHECK FOR DUPLICATES** - Ensure imports/blocks aren't already present
4. **ASSESS STRUCTURE** - Understand surrounding code to avoid corruption

### Rationale

- Prevents duplicate imports and code blocks
- Avoids file corruption from mismatched oldString patterns
- Ensures edits are contextually appropriate
- Reduces failed edit attempts and token waste
- Maintains code quality and consistency

### Implementation Pattern

```python
# ❌ WRONG: Edit without reading
replace_string_in_file(path, old, new)  # May fail or duplicate code

#  CORRECT: Read, assess, then edit
read_file(path, start_line, end_line)   # Inspect current state
# Analyze what's present
# Craft precise oldString with 3-5 lines context
replace_string_in_file(path, old, new)  # Clean, targeted edit
```

### Enforcement

- This rule is documented in `.github/copilot-instructions.md`
- Violations result in failed edits, duplicated code, or corrupted files
- Code reviews should flag edits made without prior file inspection

## Rule 2: README Rebuild Root Validation

**Status:** MANDATORY  
**Applies to:** All README rebuild operations  
**Effective:** Immediately

### Requirement

When executing README rebuild operations (`codesentinel update readme --rebuild` or `update docs --rebuild`):

1. **ROOT CLEANUP FIRST** - System automatically validates root directory compliance
2. **OPTIMAL DATA** - Ensure file structure diagram reflects compliant, clean repository state
3. **POLICY ENFORCEMENT** - Root must be assessed against specification before documentation generation

### Implementation

The `update readme --rebuild` and `update docs --rebuild` commands now automatically:

1. Validate root directory against allowed files/directories policy
2. Report any policy violations detected
3. Advise users to run `codesentinel clean --root --full` to fix violations
4. Proceed with rebuild showing current state (including violations if present)

### Allowed Root Items

**Files:**

- `setup.py`, `pyproject.toml`, `MANIFEST.in`, `pytest.ini`
- `requirements.txt`, `requirements-dev.txt`, `run_tests.py`
- `publish_to_pypi.py`, `README.md`, `LICENSE`, `CHANGELOG.md`
- `CONTRIBUTING.md`, `SECURITY.md`, `QUICK_START.md`
- `codesentinel.json`, `codesentinel.log`, `.codesentinel_integrity.json`
- `.test_integrity.json`, `.gitignore`

**Directories:**

- `.git`, `.github`, `archive`, `codesentinel`, `deployment`
- `docs`, `github`, `infrastructure`, `logs`, `requirements`
- `scripts`, `tests`, `tools`, `quarantine_legacy_archive`

### Rationale

- README should reflect ideal repository state, not current violations
- File structure diagrams guide contributors - must show proper organization
- Prevents documenting temporary/unauthorized files as permanent structure
- Aligns documentation with SEAM Protection™ standards
- Encourages maintaining a clean repository root

### Enforcement

- Built into `_handle_update` function in `codesentinel/cli/__init__.py`
- Validation runs automatically before structure analysis
- Violations are reported but don't block rebuild (allows documenting current state)
- Users are advised to fix violations before rebuild for optimal documentation

## Compliance

These rules are:

- **Permanent** - Cannot be overridden or disabled
- **Documented** - In `.github/copilot-instructions.md` and `CONTRIBUTING.md`
- **Enforced** - Through code implementation and review processes
- **SEAM-Aligned** - Support Security, Efficiency, And Minimalism principles

## Version History

- **v1.0.0** (2025-11-10) - Initial rule establishment
  - Rule 1: Pre-Edit File State Validation
  - Rule 2: README Rebuild Root Validation
