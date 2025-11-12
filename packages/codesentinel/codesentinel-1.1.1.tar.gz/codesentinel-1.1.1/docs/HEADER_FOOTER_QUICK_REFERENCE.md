# Header/Footer Quick Reference

## One-Liner Commands

### View Templates

```bash
codesentinel update headers templates    # Show all header templates
codesentinel update footers templates    # Show all footer templates
```

### Apply to Single File

```bash
codesentinel update headers set --file README.md                          # Auto-detect template
codesentinel update footers set --file README.md --template with_project  # Specific template
```

### Batch Apply

```bash
codesentinel update headers edit    # Interactive editor for all docs
codesentinel update footers edit    # Interactive footer editor
```

### Custom Content

```bash
codesentinel update headers set --file README.md --custom "# My Title"
codesentinel update footers set --file README.md --custom "Custom footer"
```

---

## Template Overview

### Headers

- `README.md` - Project name + description ⭐
- `SECURITY.md` - Security policy + project name ⭐
- `CHANGELOG.md` - Standard changelog template
- `CONTRIBUTING.md` - Contributing guidelines ⭐

### Footers

- `standard` - SEAM Protection™ branding
- `with_project` - Includes project name ⭐
- `with_links` - Links to key docs
- `with_version` - Includes version number ⭐
- `minimal` - No separator line

⭐ = Uses detected project values

---

## Smart Detection

Templates automatically extract and use:

- Project name (from `pyproject.toml`)
- Description (from package metadata)
- Version (from config files)
- Repository (from git)

---

## Examples

### Apply All Defaults

```bash
codesentinel update headers set --file README.md
codesentinel update headers set --file SECURITY.md
codesentinel update headers set --file CONTRIBUTING.md
codesentinel update footers set --file README.md --template with_project
```

### Interactive Workflow

```bash
codesentinel update headers edit
codesentinel update footers edit
```

### Verify & Fix All Docs

```bash
codesentinel update docs
```

---

## Project Auto-Detection Output

When you run a template command, CodeSentinel shows:

```text
 Detected Project: codesentinel
   Description: A Polymath Project | Created by joediggidyyy
   Repository: https://github.com/joediggidyyy/CodeSentinel.git
```

This info automatically populates into templates marked with ⭐

---

**For full documentation, see:** [HEADER_FOOTER_GUIDE.md](HEADER_FOOTER_GUIDE.md)
