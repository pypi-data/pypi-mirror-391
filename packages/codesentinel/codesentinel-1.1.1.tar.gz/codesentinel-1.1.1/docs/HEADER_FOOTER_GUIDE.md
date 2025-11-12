# Header and Footer Management Guide

## Overview

CodeSentinel now includes intelligent header and footer management for documentation files. The system automatically detects your project information and generates context-aware templates with your project name, description, and version.

## Smart Project Detection

The template system intelligently extracts:

- **Project Name** - from `pyproject.toml` or `setup.py`
- **Description** - from package metadata or docstrings
- **Version** - from project configuration files
- **Repository URL** - from git remote configuration
- **Repository Name** - extracted from git URL

This information is automatically integrated into all template suggestions and examples.

## Available Commands

### View Header Templates

```bash
# Show all available header templates with project-specific content
codesentinel update headers templates

# Show header templates in brief format
codesentinel update headers show
```

### View Footer Templates

```bash
# Show all available footer templates with project-specific content
codesentinel update footers templates

# Show footer templates in brief format
codesentinel update footers show
```

### Apply Templates to Files

#### Apply Header Template

```bash
# Apply default template for a file
codesentinel update headers set --file README.md

# Apply specific template by name
codesentinel update headers set --file SECURITY.md --template SECURITY.md

# Apply custom header text
codesentinel update headers set --file README.md --custom "# My Custom Header"
```

#### Apply Footer Template

```bash
# Apply standard footer (default)
codesentinel update footers set --file README.md

# Apply project-specific footer
codesentinel update footers set --file README.md --template with_project

# Apply footer with version
codesentinel update footers set --file README.md --template with_version

# Apply footer with links
codesentinel update footers set --file README.md --template with_links

# Apply custom footer
codesentinel update footers set --file README.md --custom "Custom footer text"
```

### Interactive Editing

```bash
# Interactively edit headers for all documentation files
codesentinel update headers edit

# Interactively edit footers for all documentation files
codesentinel update footers edit

# Interactively edit headers for specific file
codesentinel update headers edit --file README.md
```

## Available Templates

### Header Templates

| Template | Project-Specific | Description |
|----------|-----------------|-------------|
| **README.md** | ⭐ Yes | Main project README with title and description |
| **SECURITY.md** | ⭐ Yes | Security policy template mentioning project |
| **CHANGELOG.md** | No | Standard changelog template |
| **CONTRIBUTING.md** | ⭐ Yes | Contribution guidelines template |

**Project-specific templates automatically populate with detected project information.**

### Footer Templates

| Template | Project-Specific | Description |
|----------|-----------------|-------------|
| **standard** | No | Basic SEAM Protection™ branding footer |
| **with_project** | ⭐ Yes | Includes project name in footer |
| **with_links** | No | Footer with links to key documents |
| **with_version** | ⭐ Yes | Includes version number in footer |
| **minimal** | No | Minimal footer without separator line |

## Examples

### Example 1: Apply Project-Specific README Header

```bash
codesentinel update headers set --file README.md
```

This will apply:

```markdown
# codesentinel

A Polymath Project | Created by joediggidyyy

---
```

### Example 2: Add Project-Aware Footer

```bash
codesentinel update footers set --file README.md --template with_project
```

This will add:

```markdown
---

codesentinel - SEAM Protected™ by CodeSentinel
```

### Example 3: Apply Version Footer

```bash
codesentinel update footers set --file CHANGELOG.md --template with_version
```

This will add:

```markdown
---

**Version:** 1.0.0

SEAM Protected™ by CodeSentinel
```

### Example 4: Interactive Multi-File Editing

```bash
codesentinel update headers edit
```

The system will prompt you through each documentation file:

- Show the suggested template with project values
- Ask if you want to use the suggestion
- Option to provide custom header text
- Option to skip

## Automatic Integration with Update Docs

The `codesentinel update docs` command now includes header/footer verification:

```bash
# Verify branding AND header/footer compliance
codesentinel update docs

# Preview without making changes
codesentinel update docs --dry-run
```

Both branding and header/footer issues are automatically fixed.

## SEAM Protection™ Branding

All footer templates maintain SEAM Protection™ branding:

- Standard: `SEAM Protected™ by CodeSentinel`
- With project: `{ProjectName} - SEAM Protected™ by CodeSentinel`
- With links: Includes SEAM Protection footer plus resource links
- With version: Includes SEAM Protection footer plus version number

## Tips

1. **Automatic Detection**: Project information is detected automatically - no manual configuration needed
2. **Project-Specific Indicators**: Templates marked with ⭐ use your actual project values
3. **Dry Run**: Always use `--dry-run` with commands to preview changes first
4. **Interactive Mode**: Use interactive editing for best user experience when multiple files need updating
5. **Consistency**: Apply headers to all major documentation files for visual consistency
6. **Version Tracking**: Use the `with_version` footer template to keep version numbers synchronized with package metadata

## Troubleshooting

**Templates show generic values instead of project name?**

- Check that `pyproject.toml` or `setup.py` exists in project root
- Verify git remote is configured: `git config --get remote.origin.url`

**Can't apply templates to custom documentation files?**

- Specify the full file path: `codesentinel update headers set --file docs/custom.md`

**Want to override detected project name?**

- Use the `--custom` option to provide your own template text

---

*SEAM Protected™ by CodeSentinel*
