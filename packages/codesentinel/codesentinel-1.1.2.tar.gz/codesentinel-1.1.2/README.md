# CodeSentinel

**SEAM Protected™ by CodeSentinel**  
*(Security, Efficiency, And Minimalism)*

> **A Polymath Project** | Created by joediggidyyy

CodeSentinel is a cross-platform automated maintenance and security monitoring system that integrates seamlessly with development workflows. It provides intelligent repository maintenance, security scanning, and multi-channel alerting to keep your codebase healthy, secure, and SEAM-tight.

**Powered by ORACL™** - An intelligent decision support system that learns from your repository's history to provide context-aware recommendations and automated remediation guidance.

[![Python](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-1.1.2-green.svg)](https://github.com/joediggidyyy/CodeSentinel)

---

## Features

### Security

- **Automated vulnerability scanning** - Daily security audits of dependencies
- **Secret detection** - Prevents credential leakage with pattern matching
- **File integrity monitoring** - SHA-256 baseline verification
- **Audit logging** - Comprehensive operation tracking with timestamps

### Efficiency  

- **Automated maintenance** - Daily, weekly, and monthly scheduled tasks
- **Smart cleanup** - Intelligent cache, temp, and build artifact removal
- **Code duplication detection** - Identifies redundant implementations
- **Root directory management** - Policy-based organization enforcement

### Minimalism

- **Non-destructive operations** - Archive-first approach for all deletions
- **Focused codebase** - Single source of truth for each feature
- **Dependency optimization** - Minimal, essential dependencies only
- **Clean repository structure** - Automated policy enforcement

### Intelligence & Learning

- **ORACL™ Intelligence Ecosystem** - *Omniscient Recommendation Archive & Curation Ledger*
  - **Historical decision context** - Learn from past operations and remediation patterns
  - **3-Tier memory architecture** - Short-term session cache, mid-term weekly summaries, long-term strategic patterns
  - **Confidence-based recommendations** - AI-powered suggestions with success rate tracking
  - **Pattern discovery** - Automatic identification of recurring issues and optimal solutions
  - **Intelligent remediation** - Context-aware guidance for policy violations and code quality issues

### Developer Experience

- **Multi-channel alerts** - Email, Slack, console, and file notifications
- **CLI-first design** - Comprehensive command-line interface
- **GUI setup wizard** - User-friendly configuration assistant
- **IDE integration** - VS Code and GitHub Copilot support
- **Development audits** - Interactive `!!!!` command with ORACL™-powered insights

---

## Quick Start

### Installation

```bash
# Install from PyPI
pip install codesentinel

# Or install from source
git clone https://github.com/joediggidyyy/CodeSentinel.git
cd CodeSentinel
pip install -e .
```

### Initial Setup

```bash
# Run interactive setup wizard
codesentinel setup

# Or use GUI setup (optional)
codesentinel setup --gui
```

### Basic Usage

```bash
# Check system status
codesentinel status

# Run security scan
codesentinel scan

# Start automated scheduler
codesentinel schedule start

# Clean repository artifacts
codesentinel clean

# Run development audit
codesentinel !!!!
```

---

## Command Reference

### Core Commands

| Command | Description |
|---------|-------------|
| `codesentinel status` | Display current system status and configuration |
| `codesentinel scan` | Run comprehensive security vulnerability scan |
| `codesentinel scan --bloat-audit` | Analyze repository bloat and identify cleanup opportunities |
| `codesentinel scan --all` | Run both security scan and bloat audit |
| `codesentinel scan --json` | Output results in JSON format for automation |
| `codesentinel --version` | Show version information |

### Maintenance Commands

| Command | Description |
|---------|-------------|
| `codesentinel maintenance daily` | Execute daily maintenance tasks |
| `codesentinel maintenance weekly` | Execute weekly maintenance tasks |
| `codesentinel maintenance monthly` | Execute monthly maintenance tasks |
| `codesentinel clean` | Clean cache, temp files, and logs |
| `codesentinel clean --cache` | Clean Python cache artifacts (**pycache**, .pyc files) |
| `codesentinel clean --test` | Clean test artifacts (.pytest_cache, coverage data) |
| `codesentinel clean --build` | Clean build artifacts (dist/, build/, .egg-info) |
| `codesentinel clean --cache --test --build` | Clean all artifact types |
| `codesentinel clean --root` | Clean root directory clutter |
| `codesentinel clean --root --full` | Full root policy compliance check |
| `codesentinel clean --emojis` | Remove policy-violating emojis |

**Scan → Clean Workflow**: Use `scan --bloat-audit` to identify bloat, then `clean` to remove it.

```bash
# Step 1: Analyze repository bloat
codesentinel scan --bloat-audit

# Step 2: Review recommendations and clean specific artifacts
codesentinel clean --cache --test --build --force

# Or: Run both in sequence
codesentinel scan --bloat-audit && codesentinel clean --cache --test --build --force
```

### Scheduler Commands

| Command | Description |
|---------|-------------|
| `codesentinel schedule start` | Start the maintenance scheduler daemon |
| `codesentinel schedule stop` | Stop the maintenance scheduler daemon |
| `codesentinel schedule status` | Check scheduler status |

### Documentation Commands

| Command | Description |
|---------|-------------|
| `codesentinel update docs` | Update repository documentation |
| `codesentinel update changelog` | Update CHANGELOG.md with recent commits |
| `codesentinel update readme` | Rebuild README.md with current features |
| `codesentinel update readme --validate` | Validate README compliance and quality |
| `codesentinel update version <major\|minor\|patch>` | Bump version numbers |
| `codesentinel update headers` | Manage documentation headers |
| `codesentinel update footers` | Manage documentation footers |

### Integration Commands

| Command | Description |
|---------|-------------|
| `codesentinel integrate --new` | Integrate new CLI commands into workflows |
| `codesentinel integrate --all` | Integrate all commands into workflows |
| `codesentinel integrate --workflow ci-cd` | Target CI/CD workflows |

### Development Audit

| Command | Description |
|---------|-------------|
| `codesentinel dev-audit` | Run interactive development audit |
| `codesentinel !!!!` | Quick trigger for dev-audit |
| `codesentinel !!!! --agent` | AI-assisted remediation with ORACL™-powered context and GitHub Copilot |
| `codesentinel !!!! <focus>` | Focused audit on specific area |

### Alert Commands

| Command | Description |
|---------|-------------|
| `codesentinel alert "message"` | Send alert through configured channels |
| `codesentinel alert "message" --severity critical` | Send critical alert |

### File Integrity

| Command | Description |
|---------|-------------|
| `codesentinel integrity status` | Show integrity monitoring status |
| `codesentinel integrity start` | Enable integrity monitoring |
| `codesentinel integrity verify` | Verify files against baseline |
| `codesentinel integrity config baseline` | Generate integrity baseline |

---

## Configuration

CodeSentinel uses a central `codesentinel.json` configuration file:

```json
{
  "project_name": "MyProject",
  "alert_channels": ["console", "file"],
  "scheduler": {
    "enabled": true,
    "daily_time": "02:00",
    "weekly_day": "sunday",
    "weekly_time": "03:00"
  },
  "maintenance": {
    "auto_cleanup": true,
    "archive_retention_days": 30
  }
}
```

### Environment Variables

For sensitive configuration (email, Slack tokens):

```bash
# Email alerts
export EMAIL_HOST="smtp.gmail.com"
export EMAIL_PORT="587"
export EMAIL_USER="your-email@gmail.com"
export EMAIL_PASSWORD="your-app-password"

# Slack alerts
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

---

## Workflows

### Repository Health: Scan → Clean

CodeSentinel uses a two-phase approach for repository maintenance:

**Phase 1: Analyze (Scan)**

```bash
# Identify bloat and inefficiencies
codesentinel scan --bloat-audit
```

This performs comprehensive analysis:

- Cache artifacts (\*\*pycache\*\*, .pytest_cache, .pyc files)
- Build artifacts (dist/, build/, .egg-info)
- Large files (>1MB without clear purpose)
- Documentation bloat (session/checkpoint docs)
- Test artifact organization
- Archive structure
- Configuration file duplication
- Dependency file issues

**Phase 2: Execute (Clean)**

```bash
# Remove identified bloat
codesentinel clean --cache --test --build --force
```

Clean command options:

- `--cache` - Python cache artifacts
- `--test` - Test artifacts and coverage data
- `--build` - Build/distribution artifacts
- `--root` - Root directory clutter
- `--force` - Skip confirmation prompts
- `--dry-run` - Preview actions without executing

**Example Workflow:**

```bash
# Step 1: Full analysis
codesentinel scan --bloat-audit --json > bloat-report.json

# Step 2: Review recommendations
cat bloat-report.json

# Step 3: Clean specific categories
codesentinel clean --cache --test --force

# Step 4: Verify cleanup
codesentinel scan --bloat-audit
```

### Security Monitoring

```bash
# Run security scan
codesentinel scan

# Run both security and bloat analysis
codesentinel scan --all

# Schedule automated scans
codesentinel schedule start
```

---

## Architecture

### Project Structure

```
CodeSentinel/
 codesentinel/          # Core Python package
    cli/              # Command-line interface
    core/             # Core business logic
    gui/              # GUI components
    utils/            # Shared utilities (including ORACL™)
 tools/                # Automation scripts
    codesentinel/     # Maintenance automation
    config/           # Configuration templates
 tests/                # Test suite
 docs/                 # Documentation
 scripts/              # Helper scripts
```

### Dual Architecture

CodeSentinel follows a dual-architecture pattern:

- **`codesentinel/`** - Main Python package with CLI (`codesentinel`, `codesentinel-setup`)
- **`tools/codesentinel/`** - Comprehensive maintenance automation scripts
- **`tools/config/`** - JSON configuration files for alerts, scheduling, and policies

### ORACL™ Intelligence Ecosystem

**ORACL™** (Omniscient Recommendation Archive & Curation Ledger) provides intelligent decision support through a 3-tier memory architecture:

#### Tier 1: Session Memory (0-60 minutes)

- High-speed ephemeral cache for current task context
- Prevents redundant file reads and re-analysis within active sessions
- Automatic invalidation after 60 minutes

#### Tier 2: Context Memory (7-day rolling window)

- Curated summaries from recently completed sessions
- Aggregated insights on successful operations and key decisions
- Provides recent historical context for related work

#### Tier 3: Intelligence Archive (Permanent)

- Long-term strategic patterns and historical wisdom
- Pattern discovery engine for recurring issues
- Confidence-scored recommendations based on success rates
- Tamper-proof verification with SHA-256 checksums

**Key Benefits:**

- **20-50% reduction** in redundant agent operations
- **Historical learning** from past remediation attempts
- **Confidence scoring** for automated decision-making
- **Pattern recognition** for proactive issue resolution

Learn more: See `docs/ORACL_MEMORY_ARCHITECTURE.md` for technical details.

---

## Security Best Practices

CodeSentinel is **SEAM Protected™** with security as the highest priority:

1. **No Hardcoded Credentials** - All sensitive data in environment variables
2. **Audit Logging** - All operations logged with timestamps
3. **Configuration Validation** - Secure defaults with auto-validation
4. **Dependency Scanning** - Automated vulnerability detection
5. **Non-Destructive Operations** - Archive-first approach for all deletions

See [SECURITY.md](SECURITY.md) for detailed security policies and vulnerability reporting.

---

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Clone repository
git clone https://github.com/joediggidyyy/CodeSentinel.git
cd CodeSentinel

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python run_tests.py
```

### Code Quality

- **DRY Principle**: Code reuse and modularization is mandatory
- **SEAM Protection™**: Security, Efficiency, And Minimalism guide all decisions
- **Non-Destructive**: Never delete without archiving first
- **Feature Preservation**: All existing functionality must be maintained

---

## Requirements

- **Python**: 3.13 or higher
- **Operating Systems**: Windows, macOS, Linux
- **Dependencies**: See [requirements.txt](requirements.txt)

### Optional Dependencies

- **GUI Support**: tkinter (usually included with Python)
- **Development Tools**: pytest, black, mypy, flake8

---

## Documentation

- **[Quick Start Guide](QUICK_START.md)** - Get up and running quickly
- **[Security Policy](SECURITY.md)** - Security practices and reporting
- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute
- **[Changelog](CHANGELOG.md)** - Version history and changes
- **[Full Documentation](docs/)** - Comprehensive guides and references

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

CodeSentinel is a **Polymath Project** created with a focus on:

- **SEAM Protection™**: Security, Efficiency, And Minimalism
- **Developer Experience**: Making maintenance effortless
- **Code Quality**: DRY principles and best practices
- **Community**: Open-source collaboration

---

## Support

- **Issues**: [GitHub Issues](https://github.com/joediggidyyy/CodeSentinel/issues)
- **Discussions**: [GitHub Discussions](https://github.com/joediggidyyy/CodeSentinel/discussions)
- **Email**: <joediggidy3@gmail.com>

---

**CodeSentinel** - Keeping your code SEAM-tight! 🛡️
