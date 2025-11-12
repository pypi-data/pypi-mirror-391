# Contributing to CodeSentinel

Thank you for your interest in contributing to CodeSentinel! This document provides guidelines and information for contributors.

## Development Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/joediggidyyy/CodeSentinel.git
   cd CodeSentinel
   ```

2. **Set up development environment:**

   ```bash
   # Install development dependencies
   pip install -r requirements.txt
   pip install pytest black mypy build twine

   # Optional: Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Run tests:**

   ```bash
   python run_tests.py
   ```

## Development Workflow

1. **Create a feature branch:**

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes:**
   - Follow the existing code style
   - Add tests for new functionality
   - Update documentation as needed

3. **Run quality checks:**

   ```bash
   # Format code
   black codesentinel tests

   # Type check
   mypy codesentinel --ignore-missing-imports

   # Run tests
   python run_tests.py
   ```

4. **Commit your changes:**

   ```bash
   git add .
   git commit -m "Add your descriptive commit message"
   ```

5. **Push and create a pull request:**

   ```bash
   git push origin feature/your-feature-name
   ```

## Code Style

- **Formatting:** We use Black for code formatting
- **Type hints:** Use type hints where possible
- **Docstrings:** Use Google-style docstrings
- **Imports:** Group imports (standard library, third-party, local)

## AI Agent Development Rules

**These rules apply to all AI-assisted development (GitHub Copilot, etc.):**

### Pre-Edit File State Validation (MANDATORY)

**ALWAYS check file state before making edits:**

1. **Read First**: Use `read_file` or equivalent to inspect current state
2. **Verify Context**: Ensure code/imports aren't already present
3. **Assess Structure**: Understand surrounding code before modifications
4. **Craft Precise Edits**: Include 3-5 lines of context in find/replace operations

**Why:**

- Prevents duplicate imports and code blocks
- Avoids file corruption from pattern mismatches
- Reduces failed edits and wasted iterations
- Ensures changes are contextually appropriate

**Example Pattern:**

```python
# ❌ WRONG: Edit without reading
replace_in_file(...)  # May duplicate or corrupt

#  CORRECT: Read, assess, then edit
read_file(path, start, end)  # Inspect current state
# Analyze what exists
replace_in_file(...)  # Precise, context-aware edit
```

### README Rebuild Root Validation (MANDATORY)

**ALWAYS validate root directory before README rebuild:**

When running `codesentinel update readme --rebuild` or `update docs --rebuild`:

1. **Root Validation First**: System automatically checks root directory compliance
2. **Policy Enforcement**: Reports unauthorized files/directories before documentation generation
3. **Clean State**: README file structure diagram reflects compliant repository state

**Why:**

- Documentation should reflect ideal/compliant state, not temporary violations
- File structure diagrams guide contributors - must show proper organization
- Prevents documenting unauthorized files as permanent structure
- Aligns with SEAM Protection™ standards

**Implementation:**

- Rebuild operations automatically invoke root validation
- Policy violations are reported but don't block rebuild
- Users advised to run `codesentinel scan --bloat-audit` to identify issues, then `codesentinel clean --root --full` to remediate

## Development Workflow

### Before Starting Work

```bash
# Analyze repository health
codesentinel scan --bloat-audit

# Clean up artifacts
codesentinel clean --cache --test --build --force

# Verify root directory compliance
codesentinel clean --root --full --dry-run
```

### During Development

```bash
# Run tests frequently
pytest tests/

# Check code quality
codesentinel scan

# Monitor session context (for agents)
codesentinel memory show
```

### Before Committing

```bash
# Full bloat audit
codesentinel scan --bloat-audit

# Clean artifacts
codesentinel clean --cache --test --force

# Run full test suite
pytest tests/ -v

# Update documentation if needed
codesentinel update readme --validate
```

## Testing

- Write unit tests for new functionality
- Aim for good test coverage
- Run the full test suite before submitting PRs

## Documentation

- Update README.md for significant changes
- Add docstrings to new functions/classes
- Update this CONTRIBUTING.md if development processes change

## Pull Request Process

1. Ensure all tests pass
2. Update documentation if needed
3. Request review from maintainers
4. Address review feedback
5. Merge when approved

## Reporting Issues

- Use GitHub Issues to report bugs
- Provide detailed reproduction steps
- Include relevant system information
- Suggest fixes if possible

## License

By contributing to CodeSentinel, you agree that your contributions will be licensed under the MIT License.
