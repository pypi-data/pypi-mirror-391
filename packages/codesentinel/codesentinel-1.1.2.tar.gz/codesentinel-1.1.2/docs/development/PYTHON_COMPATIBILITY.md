# Python Version Compatibility Guide

**Document Status:** Canonical Reference  
**Last Updated:** 2025-11-11  
**Applies To:** All CodeSentinel Python code

---

## Python Version Support Policy

CodeSentinel officially supports **Python 3.8+** as declared in:

- `pyproject.toml`: `requires-python = ">=3.8"`
- `setup.py`: `python_requires='>=3.8'`
- GitHub Actions CI: Tests on Python 3.8, 3.9, 3.10, 3.11

**CRITICAL:** All code MUST be compatible with Python 3.8 syntax and standard library.

---

## Type Annotation Compatibility (CRITICAL)

### The Problem: PEP 585 Lowercase Generics

**Python 3.9+ allows:**

```python
def func() -> tuple[bool, list[str]]:
    return True, ["item"]
```

**Python 3.8 DOES NOT support this syntax** - causes `TypeError: 'type' object is not subscriptable`

### The Solution: Use typing Module (Python 3.8 Compatible)

**ALWAYS use capitalized types from `typing` module:**

```python
from typing import Tuple, List, Dict, Set, Optional

def func() -> Tuple[bool, List[str]]:
    return True, ["item"]
```

### Complete Reference Table

| ❌ Python 3.9+ (FORBIDDEN) | ✅ Python 3.8+ (REQUIRED) |
|---------------------------|--------------------------|
| `tuple[...]`              | `Tuple[...]`             |
| `list[...]`               | `List[...]`              |
| `dict[...]`               | `Dict[...]`              |
| `set[...]`                | `Set[...]`               |
| `frozenset[...]`          | `FrozenSet[...]`         |
| `type[...]`               | `Type[...]`              |

### Import Template

**Add to EVERY file using type annotations:**

```python
from typing import Dict, List, Tuple, Set, Optional, Any, Union
```

---

## Historical Incident Report

### v1.1.1 Release - CI Failure (2025-11-11)

**Incident:** Python 3.8 CI tests failed with 6 test collection errors after v1.1.1 PyPI publication.

**Root Cause:** Multiple files used lowercase generic syntax (`tuple[`, `list[`) incompatible with Python 3.8.

**Affected Files:**

- `codesentinel/cli/doc_utils.py` - 4 function signatures
- `codesentinel/cli/update_utils.py` - 4 function signatures  
- `codesentinel/cli/__init__.py` - 6 function signatures

**Error Pattern:**

```
ERROR tests/test_*.py - TypeError: 'type' object is not subscriptable
```

**Resolution:**

- Commit `0af3799`: Fixed doc_utils.py and update_utils.py
- Commit `48b9d28`: Fixed remaining **init**.py signatures
- Added `Tuple`, `List` to typing imports in all affected files

**Prevention Measures:**

1. This documentation created as canonical reference
2. Pre-commit hook recommendation (future enhancement)
3. Added to agent instructions (copilot-instructions.md)

---

## Validation Checklist

Before committing ANY code with type annotations:

- [ ] All type hints use capitalized types from `typing` module
- [ ] No instances of `tuple[`, `list[`, `dict[`, `set[` in function signatures
- [ ] Import statement includes all required typing classes
- [ ] Local tests pass on Python 3.8 (if available) or CI will catch

### Quick Validation Command

Search for incompatible syntax:

```bash
# Find all lowercase generic usage (should return 0 results in codesentinel/)
grep -r "-> tuple\[" codesentinel/
grep -r "-> list\[" codesentinel/
grep -r "-> dict\[" codesentinel/
grep -r "-> set\[" codesentinel/
grep -r ": tuple\[" codesentinel/
grep -r ": list\[" codesentinel/
grep -r ": dict\[" codesentinel/
grep -r ": set\[" codesentinel/
```

---

## CI/CD Integration

GitHub Actions configuration (`.github/workflows/test.yml`) ensures compatibility:

```yaml
strategy:
  matrix:
    python-version: ['3.8', '3.9', '3.10', '3.11']
```

**Python 3.8 is the gatekeeper** - if code passes 3.8, it works on all supported versions.

---

## Future Considerations

### When Can We Drop Python 3.8?

Python 3.8 reached end-of-life: **October 2024**

**Recommendation:** Maintain 3.8 compatibility until user base analysis shows <5% usage.

### Migration to PEP 585 (Future)

When Python 3.8 support is dropped:

1. Update `pyproject.toml` and `setup.py` to `requires-python = ">=3.9"`
2. Run automated migration: `pyupgrade --py39-plus **/*.py`
3. Update this documentation to reflect new policy
4. Remove typing imports where lowercase generics suffice

---

## Agent Instructions Integration

This policy is referenced in `.github/copilot-instructions.md`:

```markdown
### Python 3.8 Type Annotation Compatibility

**MANDATORY:** All type annotations must use Python 3.8-compatible syntax.

- Use `Tuple[...]`, `List[...]`, `Dict[...]` from `typing` module
- Never use lowercase generics (`tuple[`, `list[`, `dict[`)
- See: docs/development/PYTHON_COMPATIBILITY.md
```

---

**SEAM Protected™ by CodeSentinel**
