# Agent Integration Status System

**Date:** November 11, 2025  
**Purpose:** Standardized way to identify and mark agent-integration capabilities in help files and CLI output

---

## Overview

This system provides clear, consistent marking of which CLI commands support agent integration (`--agent` flag), what status that integration is in, and where users can learn more.

---

## Status Levels

| Status | Icon | Meaning | Use Case |
|--------|------|---------|----------|
| `ready` | 🤖 | Fully implemented agent integration | `scan`, `integrate`, `dev-audit` |
| `planned` | 📋 | Scheduled for agent integration | `update-changelog`, `update-dependencies` |
| `experimental` | 🧪 | Agent integration in testing/beta | `clean`, `schedule` |
| `not-applicable` | ✅ | Command doesn't benefit from agent | `alert`, `status` |

---

## Implementation Methods

### Method 1: Help File Headers (Recommended)

Each command's help documentation should include an agent status badge at the top:

```markdown
# Scan Command

🤖 **Agent Integration Status: READY**

```

Generated help files in `docs/cli/` should follow this pattern:

```markdown
# scan

**Agent Integration:** 🤖 Ready | **Last Updated:** 2025-11-11

## Description
Run security scan on codebase...

## Usage
codesentinel scan [OPTIONS]

## Agent Integration
This command supports `--agent` flag for AI-assisted vulnerability triage.
...
```

---

### Method 2: Inline CLI Help Status

When a user runs `codesentinel scan --help`, status appears in output:

```
usage: codesentinel scan [OPTIONS]

Run security scan

options:
  --agent          [🤖 AGENT-READY] Export scan context for AI remediation
  --output, -o     Export results to file
  ...
```

---

### Method 3: Command Status Directory

Create `docs/COMMAND_STATUS.md` as a quick reference:

```markdown
# Command Agent Integration Status

| Command | Status | Flag | Notes |
|---------|--------|------|-------|
| scan | 🤖 Ready | --agent | Vulnerability triage |
| dev-audit | 🤖 Ready | --agent | Already implemented |
| integrate | 🤖 Ready | --agent | In progress |
| update-changelog | 📋 Planned | --agent | Q4 2025 |
| update-dependencies | 📋 Planned | --agent | Q4 2025 |
| schedule | 🧪 Experimental | --agent | Testing phase |
| clean | 🧪 Experimental | --agent | Risk assessment mode |
| maintenance | ✅ Not-Applicable | - | Optimization only |
| alert | ✅ Not-Applicable | - | User-triggered |
| status | ✅ Not-Applicable | - | Informational |
| setup | ✅ Not-Applicable | - | Interactive |
```

---

## Implementation Details

### 1. Code Changes

**File:** `codesentinel/cli/update_utils.py`

Add agent status mapping:

```python
AGENT_COMMAND_STATUS = {
    # Tier 1: Ready
    'scan': {'status': 'ready', 'icon': '🤖', 'use_case': 'vulnerability-triage'},
    'integrate': {'status': 'ready', 'icon': '🤖', 'use_case': 'workflow-optimization'},
    'dev-audit': {'status': 'ready', 'icon': '🤖', 'use_case': 'code-quality-audit'},
    
    # Tier 2: Planned
    'update-changelog': {'status': 'planned', 'icon': '📋', 'quarter': 'Q4-2025'},
    'update-dependencies': {'status': 'planned', 'icon': '📋', 'quarter': 'Q4-2025'},
    'schedule': {'status': 'experimental', 'icon': '🧪', 'phase': 'beta'},
    
    # Tier 3: Not applicable
    'maintenance': {'status': 'not-applicable', 'icon': '✅', 'reason': 'optimization-only'},
    'alert': {'status': 'not-applicable', 'icon': '✅', 'reason': 'user-triggered'},
    'status': {'status': 'not-applicable', 'icon': '✅', 'reason': 'informational'},
    'setup': {'status': 'not-applicable', 'icon': '✅', 'reason': 'interactive'},
}

def get_agent_status_badge(command: str) -> str:
    """Get agent status badge for a command."""
    cmd_status = AGENT_COMMAND_STATUS.get(command, {})
    status = cmd_status.get('status', 'unknown')
    icon = cmd_status.get('icon', '❓')
    return f"{icon} {status.upper()}"

def inject_agent_status_in_help(command: str, help_text: str) -> str:
    """Inject agent status information into help text."""
    if command not in AGENT_COMMAND_STATUS:
        return help_text
    
    status_info = AGENT_COMMAND_STATUS[command]
    status = status_info['status']
    icon = status_info['icon']
    
    if status == 'ready':
        agent_note = (
            f"\n**Agent Integration:** {icon} READY\n"
            f"This command supports the `--agent` flag for AI-assisted analysis and remediation.\n"
            f"Use `{command} --agent` to enable agent-assisted mode."
        )
    elif status == 'planned':
        quarter = status_info.get('quarter', 'TBD')
        agent_note = (
            f"\n**Agent Integration:** {icon} PLANNED (Target: {quarter})\n"
            f"Agent integration for this command is scheduled.\n"
            f"Follow releases for updates."
        )
    elif status == 'experimental':
        phase = status_info.get('phase', 'beta')
        agent_note = (
            f"\n**Agent Integration:** {icon} EXPERIMENTAL ({phase})\n"
            f"Agent integration is in {phase} testing. Use with caution."
        )
    else:
        agent_note = (
            f"\n**Agent Integration:** {icon} NOT-APPLICABLE\n"
            f"This command doesn't support agent integration.\n"
        )
    
    # Inject before usage section or at end
    if '## Usage' in help_text:
        parts = help_text.split('## Usage')
        return parts[0] + agent_note + '\n\n## Usage' + parts[1]
    else:
        return help_text + agent_note
```

---

### 2. Help File Generation

**File:** `codesentinel/cli/update_utils.py` - `export_help_files` function

When generating help files, include agent status:

```python
def export_help_files(args):
    """Export CLI help text files for documentation."""
    from .agent_utils import inject_agent_status_in_help
    
    # ... existing code ...
    
    for cmd in commands:
        help_output = run_command(['codesentinel', cmd, '--help'])
        
        # Inject agent status
        help_with_status = inject_agent_status_in_help(cmd, help_output)
        
        # Export as both txt and markdown
        if format in ['txt', 'both']:
            txt_file = export_dir / f'{cmd}_help.txt'
            with open(txt_file, 'w', errors='replace') as f:
                f.write(help_with_status)
        
        if format in ['md', 'both']:
            md_file = export_dir / f'{cmd}_help.md'
            with open(md_file, 'w', errors='replace') as f:
                f.write(f"# {cmd.title()}\n\n{help_with_status}")
```

---

### 3. Status Command

Add new `codesentinel status --agent-ready` flag:

```python
elif args.command == 'status':
    if hasattr(args, 'agent_ready') and args.agent_ready:
        # Show only agent-ready commands
        from .agent_utils import AGENT_COMMAND_STATUS
        ready = {
            cmd: info for cmd, info in AGENT_COMMAND_STATUS.items()
            if info['status'] == 'ready'
        }
        print("Agent-Ready Commands:")
        for cmd in ready:
            print(f"  {ready[cmd]['icon']} {cmd}")
    else:
        # Standard status output
        print_standard_status()
```

---

## Display Examples

### In Generated Help Files

```
# Scan Command

🤖 **Agent Integration: READY** | Last Updated: 2025-11-11

## Description
Run security scan on codebase.

## Agent Integration
This command supports the `--agent` flag for AI-assisted vulnerability triage.

Usage:
  codesentinel scan --agent              # Export findings for agent analysis
  codesentinel scan --agent --export f.json  # Save to file
  codesentinel scan --force              # Apply agent recommendations (experimental)

...
```

### In Main Help Output

```
...
Examples:
  codesentinel dev-audit                # Run interactive development audit
  codesentinel dev-audit --agent        # Run with AI-assisted remediation (🤖 READY)
  ...
```

### In Command-Specific Help

```bash
$ codesentinel scan --help

usage: codesentinel scan [OPTIONS]

Run security scan

Agent Integration: 🤖 READY
This command supports --agent flag for AI-assisted vulnerability triage.

options:
  --agent                   Export scan context for AI remediation
  --output, -o FILE         Export results to file
  --dry-run                 Preview without applying changes
  ...
```

---

## Status Page: `docs/AGENT_INTEGRATION_STATUS.md`

Quick reference showing overall progress:

```markdown
# Agent Integration Status

Last Updated: November 11, 2025

## Overview

Agent integration enables AI-assisted analysis and remediation across CodeSentinel commands.

## Status by Command

### 🤖 Ready for Production (3 commands)

| Command | Feature | Status |
|---------|---------|--------|
| `dev-audit` | Code quality audit with auto-fixes | ✅ Implemented |
| `scan` | Vulnerability triage and remediation | ✅ Implemented |
| `integrate` | Workflow optimization | ✅ Implemented |

### 📋 Planned (4 commands) - Target Q4 2025

| Command | Feature | Status |
|---------|---------|--------|
| `update changelog` | Intelligent changelog generation | 🔄 Development |
| `update dependencies` | Safe dependency upgrades | 🔄 Development |
| `schedule` | Maintenance scheduling optimization | 🔄 Development |
| `integrity verify` | Anomaly detection | 🔄 Development |

### 🧪 Experimental (2 commands) - Beta Testing

| Command | Feature | Status |
|---------|---------|--------|
| `clean` | Risk-aware cleanup | ⚠️ Beta |
| `maintenance` | Task optimization | ⚠️ Beta |

### ✅ Not Applicable (5 commands)

| Command | Reason |
|---------|--------|
| `status` | Informational only |
| `alert` | User-triggered |
| `setup` | Interactive configuration |
| Others | Single-purpose operations |

## Getting Started with Agent Integration

```bash
# Enable agent-assisted mode for any ready command
codesentinel <command> --agent

# Export findings for review
codesentinel <command> --agent --export findings.json

# Apply agent recommendations (experimental)
codesentinel <command> --agent --force
```

## Quick Links

- Implementation: `tools/codesentinel/AGENT_INTEGRATION_IMPLEMENTATION_GUIDE.md`
- Architecture: `docs/CLI_AGENT_INTEGRATION_ANALYSIS.md`

```

---

## Integration Points

### 1. Main README

Add Agent Integration section showing ready commands and quick start.

### 2. CLI `--help` Output

- List ready agent commands in examples
- Mark agent-capable examples with 🤖 icon

### 3. Documentation Website

- Create Agent Integration guide page
- Show status table and quick reference
- Link to command-specific agent docs

### 4. Release Notes

For each release, update agent status section:
```

## Agent Integration Updates

- 🤖 Newly Ready: `schedule` command
- 📋 In Development: `update-dependencies` (targeting Q4)
- 🧪 Beta: `clean` command (improved risk assessment)

```

---

## Maintenance

### Status Update Workflow

1. When implementing agent integration for a command:
   - Update `AGENT_COMMAND_STATUS` mapping in `update_utils.py`
   - Update status from `planned` → `experimental` → `ready`
   - Regenerate help files: `codesentinel update help-files`
   - Update `docs/AGENT_INTEGRATION_STATUS.md`

2. When releasing new version:
   - Review agent status changes
   - Update release notes
   - Update main README if tier changed

---

## Benefits

1. **User Clarity:** Users instantly know which commands support agent integration
2. **Progress Visibility:** Clear roadmap shows implementation progress
3. **Discoverability:** Badges and icons make features easy to find
4. **Consistency:** Standardized format across all documentation
5. **Maintenance:** Single source of truth in `AGENT_COMMAND_STATUS`

---

## File Changes Summary

| File | Changes |
|------|---------|
| `codesentinel/cli/update_utils.py` | Add `AGENT_COMMAND_STATUS`, `get_agent_status_badge()`, `inject_agent_status_in_help()` |
| `codesentinel/cli/__init__.py` | Mark agent-ready examples with 🤖 icon in help |
| `docs/AGENT_INTEGRATION_STATUS.md` | Create new status reference page |
| `docs/cli/*.md` | Auto-inject agent status when regenerating help files |
| Help file generation | Include agent status metadata in exported files |

---

## Next Steps

1. Implement `AGENT_COMMAND_STATUS` mapping in `update_utils.py`
2. Add `inject_agent_status_in_help()` function
3. Update help file export logic to include agent status
4. Create `docs/AGENT_INTEGRATION_STATUS.md`
5. Update main README with agent integration section
6. Regenerate all help files: `codesentinel update help-files`
7. Test help output shows agent status correctly

