# Scan → Clean Workflow Guide

**Last Updated**: 2025-11-11  
**Version**: 1.1.0-beta.1  
**Audience**: Developers, DevOps Engineers, Repository Maintainers

## Overview

CodeSentinel uses a **two-phase approach** to repository health management:

1. **Scan (Analyze)** - Identify problems without making changes
2. **Clean (Execute)** - Remove bloat and fix issues

This separation ensures you understand what will be removed before any destructive operations occur.

---

## Phase 1: Scan (Analysis)

### Security Scanning

**Purpose**: Identify security vulnerabilities in dependencies and code

```bash
# Run security vulnerability scan
codesentinel scan

# Save results for review
codesentinel scan --output security-report.json

# View formatted results
codesentinel scan
```

**Output includes:**

- Dependency vulnerabilities with severity levels
- Affected packages and versions
- Recommended fixes and patches
- Total vulnerability count

### Bloat Auditing

**Purpose**: Identify repository bloat and inefficiencies

```bash
# Run comprehensive bloat audit
codesentinel scan --bloat-audit

# Save audit results
codesentinel scan --bloat-audit --json > bloat-audit.json
```

**Analysis covers:**

1. **Cache Artifacts**
   - `__pycache__` directories
   - `.pyc`, `.pyo` compiled files
   - `.pytest_cache` test cache
   - `.egg-info` package metadata

2. **Build Artifacts**
   - `dist/` directory (distribution packages)
   - `build/` directory (build intermediates)
   - `.whl` wheel files
   - `.tar.gz` source distributions

3. **Large Files**
   - Files >1MB without clear purpose
   - Binary files that should be in `.gitignore`
   - Media files (images, videos) in repository

4. **Documentation Bloat**
   - Session documentation in root
   - Checkpoint files from development
   - Duplicate documentation
   - Outdated analysis reports

5. **Test Artifacts**
   - Orphaned test files
   - Duplicate test implementations
   - Test output files (`.coverage`, `htmlcov/`)

6. **Archive Organization**
   - `quarantine_legacy_archive/` structure
   - Compressed vs. uncompressed files
   - Archive age and retention policy

7. **Configuration Files**
   - Duplicate `.json`, `.toml`, `.yaml` files
   - Redundant requirements files
   - Conflicting configuration

8. **Dependency Analysis**
   - Duplicate dependency files
   - Conflicting version specifications
   - Unused dependencies

### Combined Scanning

**Purpose**: Run all scans in one command

```bash
# Run security scan + bloat audit
codesentinel scan --all

# Save combined results
codesentinel scan --all --json > full-scan.json
```

---

## Phase 2: Clean (Execution)

### Cache Cleaning

**Purpose**: Remove Python cache artifacts

```bash
# Preview cache cleanup (dry-run)
codesentinel clean --cache --dry-run

# Execute cache cleanup
codesentinel clean --cache --force
```

**Removes:**

- `__pycache__/` directories (all levels)
- `*.pyc` compiled Python files
- `*.pyo` optimized Python files
- `.pytest_cache/` test cache directories

**Safe to clean**: Always safe - Python regenerates these automatically

### Test Artifact Cleaning

**Purpose**: Remove test artifacts and coverage data

```bash
# Preview test cleanup
codesentinel clean --test --dry-run

# Execute test cleanup
codesentinel clean --test --force
```

**Removes:**

- `.pytest_cache/` directories
- `.coverage` coverage data files
- `htmlcov/` coverage HTML reports
- `*.cover` coverage files

**Safe to clean**: Safe - regenerated when tests run

### Build Artifact Cleaning

**Purpose**: Remove build and distribution artifacts

```bash
# Preview build cleanup
codesentinel clean --build --dry-run

# Execute build cleanup
codesentinel clean --build --force
```

**Removes:**

- `dist/` directory (distribution packages)
- `build/` directory (build intermediates)
- `*.egg-info/` package metadata directories
- `*.whl` wheel distribution files

**Safe to clean**: Safe - regenerated during build process

### Root Directory Cleaning

**Purpose**: Enforce root directory policy compliance

```bash
# Preview root cleanup
codesentinel clean --root --dry-run

# Remove root clutter only (safe patterns)
codesentinel clean --root --force

# Full policy enforcement (archive violations)
codesentinel clean --root --full --force
```

**Root cleanup modes:**

1. **Standard (`--root`)**: Removes safe clutter patterns
   - `__pycache__`
   - `*.pyc`, `*.pyo`
   - Temporary files matching safe patterns

2. **Full (`--root --full`)**: Enforces policy compliance
   - Archives unauthorized files to `quarantine_legacy_archive/`
   - Validates against `ALLOWED_ROOT_FILES` and `ALLOWED_ROOT_DIRS`
   - Reports policy violations

**Safe to clean**:

- Standard mode: Always safe
- Full mode: Non-destructive (archives files), but review first

### Combined Cleaning

**Purpose**: Clean multiple artifact types at once

```bash
# Preview comprehensive cleanup
codesentinel clean --cache --test --build --dry-run

# Execute comprehensive cleanup
codesentinel clean --cache --test --build --force

# Clean everything including root
codesentinel clean --cache --test --build --root --force
```

---

## Recommended Workflows

### Daily Development Workflow

```bash
# Morning: Start with clean state
codesentinel scan --bloat-audit
codesentinel clean --cache --test --force

# During development: Run tests
pytest tests/

# End of day: Clean up
codesentinel clean --cache --test --force
```

### Pre-Commit Workflow

```bash
# Step 1: Full analysis
codesentinel scan --all

# Step 2: Clean artifacts
codesentinel clean --cache --test --build --force

# Step 3: Verify tests pass
pytest tests/ -v

# Step 4: Final bloat check
codesentinel scan --bloat-audit

# Step 5: Commit if clean
git add .
git commit -m "Your commit message"
```

### Pre-Release Workflow

```bash
# Step 1: Comprehensive audit
codesentinel scan --all --json > pre-release-audit.json

# Step 2: Review audit results
cat pre-release-audit.json

# Step 3: Clean all artifacts
codesentinel clean --cache --test --build --force

# Step 4: Root directory compliance
codesentinel clean --root --full --dry-run  # Review first
codesentinel clean --root --full --force    # Execute if safe

# Step 5: Verify clean state
codesentinel scan --bloat-audit

# Step 6: Run full test suite
pytest tests/ -v --cov=codesentinel

# Step 7: Build distribution
python -m build

# Step 8: Verify build
twine check dist/*
```

### CI/CD Pipeline Integration

```yaml
# .github/workflows/ci.yml
jobs:
  quality-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Install CodeSentinel
        run: pip install codesentinel
      
      - name: Scan for issues
        run: |
          codesentinel scan --all --json > scan-results.json
          cat scan-results.json
      
      - name: Clean artifacts
        run: codesentinel clean --cache --test --build --force
      
      - name: Run tests
        run: pytest tests/ -v
      
      - name: Upload scan results
        uses: actions/upload-artifact@v3
        with:
          name: scan-results
          path: scan-results.json
```

---

## Command Reference Quick Sheet

| Goal | Command |
|------|---------|
| **Identify security issues** | `codesentinel scan` |
| **Identify bloat** | `codesentinel scan --bloat-audit` |
| **Full analysis** | `codesentinel scan --all` |
| **Preview cache cleanup** | `codesentinel clean --cache --dry-run` |
| **Clean cache** | `codesentinel clean --cache --force` |
| **Clean tests** | `codesentinel clean --test --force` |
| **Clean builds** | `codesentinel clean --build --force` |
| **Clean everything** | `codesentinel clean --cache --test --build --force` |
| **Check root compliance** | `codesentinel clean --root --dry-run` |
| **Enforce root policy** | `codesentinel clean --root --full --force` |

---

## Best Practices

### 1. Always Scan Before Cleaning

```bash
# ✅ CORRECT: Analyze first, then clean
codesentinel scan --bloat-audit
codesentinel clean --cache --test --build --force

# ❌ WRONG: Clean blindly without knowing what's there
codesentinel clean --cache --test --build --force
```

### 2. Use Dry-Run for Unfamiliar Operations

```bash
# ✅ CORRECT: Preview before executing
codesentinel clean --root --full --dry-run
# Review output, then:
codesentinel clean --root --full --force

# ❌ WRONG: Execute without reviewing
codesentinel clean --root --full --force
```

### 3. Save Scan Results for Auditing

```bash
# ✅ CORRECT: Keep audit trail
codesentinel scan --all --json > audit-$(date +%Y%m%d).json

# ❌ WRONG: No record of what was found
codesentinel scan --all
```

### 4. Clean Incrementally, Not All at Once

```bash
# ✅ CORRECT: Clean by category
codesentinel clean --cache --force    # Test this works
codesentinel clean --test --force     # Then this
codesentinel clean --build --force    # Then this

# ⚠️  CAUTION: Cleaning everything at once (harder to diagnose issues)
codesentinel clean --cache --test --build --root --full --force
```

### 5. Integrate into Git Hooks

```bash
# .git/hooks/pre-commit
#!/bin/bash
codesentinel scan --bloat-audit
codesentinel clean --cache --test --force
pytest tests/ -v
```

---

## Troubleshooting

### "Scan shows bloat, but clean doesn't remove it"

**Possible causes:**

1. Bloat is in files not covered by clean flags (e.g., large media files)
2. Files are in `.gitignore` but not matching clean patterns
3. Files are in venv/environment directories (excluded from clean operations)

**Solution:**

```bash
# Review scan output for specific file paths
codesentinel scan --bloat-audit --json > audit.json
cat audit.json | grep -A5 "large_files"

# Manually review and archive/delete as needed
```

### "Clean --root --full archives files I need"

**Possible causes:**

1. Files are not in `ALLOWED_ROOT_FILES` list
2. Files are in unauthorized locations per policy

**Solution:**

```bash
# Check what would be archived (dry-run)
codesentinel clean --root --full --dry-run

# If files are legitimate, add to policy:
# Edit codesentinel/utils/root_policy.py
# Add filename to ALLOWED_ROOT_FILES

# Or: Move file to proper location (docs/, tools/, etc.)
mv unauthorized_file.md docs/
```

### "Scan --all takes too long"

**Possible causes:**

1. Large repository with many files
2. Many virtual environments in tests/ directory

**Solution:**

```bash
# Run scans separately
codesentinel scan              # Security only (faster)
codesentinel scan --bloat-audit  # Bloat only

# Exclude large directories from bloat scan:
# Edit .codesentinel-ignore to add exclusions
```

---

## Advanced Usage

### Automation Scripts

```python
#!/usr/bin/env python3
"""Automated repository health check"""
import subprocess
import json
import sys

def run_scan():
    result = subprocess.run(
        ['codesentinel', 'scan', '--all', '--json'],
        capture_output=True,
        text=True
    )
    return json.loads(result.stdout)

def run_clean():
    subprocess.run(
        ['codesentinel', 'clean', '--cache', '--test', '--build', '--force'],
        check=True
    )

if __name__ == '__main__':
    scan_results = run_scan()
    
    # Check for critical issues
    if scan_results['bloat_audit']['recommendations']:
        print("🚨 Bloat detected - cleaning...")
        run_clean()
        print("✅ Cleanup complete")
    else:
        print("✅ Repository is clean")
```

### Scheduled Maintenance

```bash
# Add to crontab for daily cleanup
0 2 * * * cd /path/to/repo && codesentinel scan --bloat-audit && codesentinel clean --cache --test --force
```

---

## Related Documentation

- [CONTRIBUTING.md](../CONTRIBUTING.md) - Development workflow integration
- [README.md](../README.md) - Full command reference
- [ARCHIVE_ORGANIZATION_POLICY.md](../quarantine_legacy_archive/ARCHIVE_ORGANIZATION_POLICY.md) - Archival policy details
- [Root Directory Policy](../codesentinel/utils/root_policy.py) - Root compliance rules

---

**Questions or Issues?**

Open an issue on [GitHub](https://github.com/joediggidyyy/CodeSentinel/issues) or check existing documentation.
