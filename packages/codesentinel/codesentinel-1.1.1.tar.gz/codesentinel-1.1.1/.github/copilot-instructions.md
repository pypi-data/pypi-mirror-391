<!-- 
This file is auto-organized by the instruction defragmentation utility.
Last organized: 2025-11-11 14:15:24
-->

<!-- 
This file is auto-organized by the instruction defragmentation utility.
Last organized: 2025-11-11 13:59:19
-->

CANONICAL_PROJECT_VERSION: "1.1.1.b1"

````instructions
# CodeSentinel AI Agent Instructions

CodeSentinel is a security-first automated maintenance and monitoring system with SEAM Protection™:
**Security, Efficiency, And Minimalism** (with Security taking absolute priority).

---

---

## Core Principles

### SECURITY
- No hardcoded credentials - Environment variables or config files only
- Audit logging - All operations logged with timestamps
- Configuration validation - Auto-creation of missing configs with secure defaults
- Dependency scanning - Automated vulnerability detection

### EFFICIENCY
- **DRY (Don't Repeat Yourself)**: Code reuse and modularization is MANDATORY
  - Always consolidate duplicate implementations into shared utilities
  - Extract common patterns into reusable functions/modules
  - Create centralized configuration files (never duplicate constants)
  - Reference single source of truth across all implementations
- Avoid redundant code and duplicate implementations
- Consolidate multiple versions of similar functionality
- Clean up orphaned test files and unused scripts
- Optimize import structures and module organization

### MINIMALISM
- Remove unnecessary dependencies
- Archive deprecated code to quarantine_legacy_archive/
- Maintain single source of truth for each feature
- Keep codebase focused and maintainable
- **Code Reuse Over Duplication**: Always prefer importing shared code over copying

### PLATFORM INDEPENDENCE (CRITICAL)
- **ASCII-Only Console Output**: NEVER use Unicode symbols (✓✗→←•) in `print()` or `logger.*()` statements
- **Why**: Windows console encoding (cp1252) cannot display Unicode, causing `UnicodeEncodeError` crashes
- **Approved Symbols**: Use `[OK]` `[FAIL]` `[WARN]` `->` `*` instead of Unicode equivalents
- **Exception**: Markdown files (`.md`) and file content can safely use UTF-8/Unicode
- **Policy Document**: See `docs/architecture/CROSS_PLATFORM_OUTPUT_POLICY.md` for complete guidelines
- **Testing Required**: All console output must be tested on Windows, Linux, and macOS

### QUARANTINE_LEGACY_ARCHIVE POLICY
- **Mandatory Reference Directory**: `quarantine_legacy_archive/` is essential for agent remediation and code archaeology
- **Purpose**: Preserve archived code, configurations, and artifacts for reference, analysis, and potential recovery
- **Compression Policy**: Compress to `.tar.gz` after 30 days of inactivity, but retain in repository
- **Security Scanning**: ALWAYS thoroughly check archive for:
  - Malicious file insertion or tampering
  - Credential leakage in archived code
  - Dependencies with known vulnerabilities
  - Integrity of archived content
- **Exclusion from Most Checks**: Archive directory is excluded from:
  - Minimalism violation reports (not considered "clutter")
  - Routine cleanup operations
  - Code style enforcement
  - Import optimization scans
- **Integrity Verification Required**: When archive is accessed or modified:
  - Verify file hashes match original
  - Scan for new/modified files
  - Check for external tampering
  - Log all access and modifications

---

---

## CRITICAL: Foundational Policies


**THESE ARE NON-NEGOTIABLE - Any implementation violating these is INCORRECT:**

### 1. NON-DESTRUCTIVE OPERATIONS - Policy Priority #1

**RULE: Never implement direct file/directory deletion without first implementing archival**

- ❌ WRONG: `path.unlink()` or `shutil.rmtree()` as default behavior
- ✅ RIGHT: `shutil.move(item, archive_path)` to `quarantine_legacy_archive/`

When implementing cleanup/remediation features:
1. **ALWAYS archive first** - Move to quarantine_legacy_archive/
2. **Ask user permission** - Even with --force, document what will be archived
3. **Provide recovery option** - Items must be accessible in archive
4. **LOG all operations** - Track what was moved and why

**Example Pattern:**
```python
# CORRECT: Archive-first pattern
archive_dir = Path("quarantine_legacy_archive")
archive_dir.mkdir(exist_ok=True)
target = archive_dir / item.name
shutil.move(str(item), str(target))

# WRONG: Direct deletion pattern (DO NOT USE)
item.unlink()  # ❌ FORBIDDEN
shutil.rmtree(item)  # ❌ FORBIDDEN
```

### 2. POLICY ALIGNMENT CHECK

Before implementing ANY file operation feature:

1. **Read the Persistent Policies section** above
2. **Ask yourself:**
   - Does this violate NON-DESTRUCTIVE? 
   - Does this remove functionality?
   - Does this compromise security?
3. **If ANY answer is yes: REDESIGN**

Recent violation example:
- Task: Add --full flag to clean --root
- Initial implementation: Deleted unauthorized files directly
- Violation: Broke NON-DESTRUCTIVE policy - Policy #1
- Fix: Changed to archive all violations instead

### 3. FILE OPERATION SAFEGUARDS

For any feature adding file operations:

```python
# TEMPLATE: Safe file operation pattern

# ✅ DO THIS:
def safe_file_operation(items_to_process):
    archive_path = workspace_root / "quarantine_legacy_archive"
    archive_path.mkdir(exist_ok=True)
    
    for item in items_to_process:
        # Step 1: Assessment
        reason = assess_file_necessity(item)
        target = determine_target_location(item)
        
        # Step 2: User confirmation (non-dry-run)
        if not dry_run and not force:
            response = input(f"Archive {item.name} ({reason})? (y/N): ")
            if response != 'y':
                continue
        
        # Step 3: Archive (never delete)
        try:
            shutil.move(str(item), str(archive_path / item.name))
            log(f"Archived: {item}")
        except Exception as e:
            log_error(f"Failed to archive: {e}")

# ❌ DON'T DO THIS:
def unsafe_file_operation(items_to_delete):
    for item in items_to_delete:
        item.unlink()  # DIRECT DELETION - VIOLATES POLICY!
        # No assessment, no archival, no recovery option
```

### 4. VALIDATION BEFORE IMPLEMENTATION

When implementing new --flag or feature:

1. **Trace all code paths** - What happens in each condition?
2. **Find delete operations** - Search for `.unlink()`, `rmtree()`, `remove()`
3. **Ask: Is there an archive alternative?** - If yes, use it
4. **Check for user confirmation** - Is there a prompt before destructive action?
5. **Test with dry-run** - Does --dry-run show what WOULD happen without doing it?

### 5. CODE REVIEW CHECKLIST

Before committing file operation features:

- [ ] No direct `.unlink()` or `rmtree()` calls (unless approved for specific cases)
- [ ] Default behavior is archival, not deletion
- [ ] User sees what will happen before it happens (--dry-run support)
- [ ] User can approve/reject before action (confirmation prompt)
- [ ] All operations are logged
- [ ] Archived items are in quarantine_legacy_archive/ or similar approved archive
- [ ] Recovery is possible (items not permanently deleted)
- [ ] Policy compliance is documented in code comments

---

---

## ORACL™ Intelligence Ecosystem

**ORACL™** (Omniscient Recommendation Archive & Curation Ledger) — *Intelligent Decision Support*

---

---

## Agent-Driven Remediation

When `codesentinel !!!! --agent` is run, you will receive comprehensive audit context with:

- Detected issues (security, efficiency, minimalism)
- Remediation hints with priority levels
- Safe-to-automate vs. requires-review flags
- Step-by-step suggested actions

### Root Directory Assessment Methodology

**CRITICAL**: When encountering conflicts between different validation systems (e.g., `clean --root` vs `root_cleanup.py` validation), follow this assessment flow **BEFORE** making any changes:

1. **MANUAL STATE ASSESSMENT**
   - List all files/directories at root: `ls -la` or equivalent
   - For each item, determine its purpose and status (authorized vs unauthorized)
   - Compare against `tools/codesentinel/root_cleanup.py`: ALLOWED_ROOT_FILES and ALLOWED_ROOT_DIRS constants
   - Document the actual vs expected state

2. **DISTINGUISH OPERATION SCOPES**
   - `codesentinel clean --root`: Removes clutter patterns only (`__pycache__`, `*.pyc`, `*.pyo`, `*.tmp`)
   - `root_cleanup.py` validation: Enforces policy compliance (checks all items against allowed lists)
   - **These are DIFFERENT operations with DIFFERENT purposes** - both can be "correct" simultaneously

3. **IDENTIFY CONTRADICTIONS**
   - If operations report different results, note what each operation's SCOPE actually covers
   - Example: clean found "0 items" ✓ (no Python clutter) while validation found "3 issues" ✓ (policy violations)
   - This is NOT contradictory - they're checking different things

4. **DETERMINE ACTION REQUIRED**
   - Is the issue about accumulated clutter? → Use clean operations
   - Is the issue about policy non-compliance? → Use validation/remediation operations
   - Is there an unauthorized file? → **ALWAYS** determine WHY it exists before deletion
   - Is there a test/debug file from development? → Archive to quarantine_legacy_archive/ rather than delete

5. **DOCUMENT FINDINGS BEFORE ACTING**
   - Write down what was found, why each item is present, what operation should address it
   - Distinguish between:
     - Development artifacts (test_integrity.py) → archive during cleanup phase
     - Unauthorized system directories (.codesentinel/) → remove per policy
     - Legitimate but misplaced files → move to correct location or archive

Your role is to:

1. **ANALYZE**: Review each issue with full context
2. **PRIORITIZE**: Focus on critical/high priority items first  
3. **DECIDE**: Determine safe vs. requires-review actions
4. **PLAN**: Build step-by-step remediation plan
5. **EXECUTE**: Only perform safe, non-destructive operations
6. **REPORT**: Document all actions and decisions

---

---

## Persistent Policies

When working with this codebase:

1. **NON-DESTRUCTIVE**: Never delete code without archiving first
2. **FEATURE PRESERVATION**: All existing functionality must be maintained
3. **STYLE PRESERVATION**: Respect existing code style and patterns
4. **SECURITY FIRST**: Security concerns always take priority
5. **MODULARIZATION & REUSE**: Always optimize code structure through code reuse and modularization. This is default behavior.
6. **REPOSITORY-RELATIVE PATHS**: All user-facing output must display paths relative to repository root (e.g., `RepoName/path/to/file`), never absolute system paths. This is a permanent, cross-project policy.
7. **PERMANENT POLICY (T0-5)**: Framework compliance review required with every package release
   - Every pre-release and production release must include comprehensive framework compliance review
   - Review must verify SEAM Protected™: Security, Efficiency, And Minimalism alignment
   - Review must validate all persistent policies (non-destructive, feature preservation, security-first)
   - Compliance review is a release-blocking requirement, cannot be deferred
   - Classified as Constitutional (Irreversible) tier in governance system
   - Review must assess technical debt impact and long-term sustainability
   - Report must be part of release package and documentation
   - Failure to include compliance review blocks release approval

---

---

## Architecture Overview

The codebase follows a dual-architecture pattern:

- **`codesentinel/`** - Core Python package with CLI interface (`codesentinel`, `codesentinel-setup`)
- **`tools/codesentinel/`** - Comprehensive maintenance automation scripts
- **`tools/config/`** - JSON configuration files for alerts, scheduling, and policies
- **`tests/`** - Test suite using pytest with unittest fallback

---

---

## Key Commands

### Development Audit
```bash
# Run interactive audit
codesentinel !!!!

# Get agent-friendly context for remediation
codesentinel !!!! --agent
```

### Maintenance Operations
```bash
# Daily maintenance workflow
python tools/codesentinel/scheduler.py --schedule daily

# Weekly maintenance (security, dependencies, performance)
python tools/codesentinel/scheduler.py --schedule weekly
```

---

---

## Integration Points

### GitHub Integration
- Repository-aware configuration detection
- Copilot instructions generation (this file)
- PR review automation capabilities

### Multi-Platform Support  
- Python 3.13/3.14 requirement with backward compatibility
- Cross-platform paths using `pathlib.Path` consistently
- PowerShell/Python dual execution support for Windows/Unix

---

---

## When Modifying This Codebase

1. **Understand the dual architecture** - Core package vs. tools scripts serve different purposes
2. **Maintain execution order** - Change detection dependency is critical
3. **Preserve configuration structure** - JSON configs have specific schemas
4. **Test both execution paths** - pytest and unittest must both work
5. **Follow security-first principle** - Never compromise security for convenience
6. **Update timeout values carefully** - Task timeouts affect workflow reliability

---

---

## Safe Actions (can automate)

- Moving test files to proper directories
- Adding entries to .gitignore
- Removing __pycache__ directories
- Archiving confirmed-redundant files to quarantine_legacy_archive/

---

---

## Requires Review (agent decision needed)

- Deleting or archiving potentially-used code
- Consolidating multiple implementations
- Removing packaging configurations
- Modifying imports or entry points

---

---

## Forbidden Actions

- Deleting files without archiving
- Forcing code style changes
- Removing features without verification
- Modifying core functionality without explicit approval
- Excessive use of emojis in documentation or code comments

---

## Agent Operating Rules (MANDATORY)

### DRY Principle Enforcement (CRITICAL)

**MANDATORY: Eliminate code duplication - Code reuse is a core SEAM Protection™ requirement**

Before implementing ANY new functionality:

1. **SEARCH FOR EXISTING IMPLEMENTATIONS**: 
   - Use `grep_search` or `semantic_search` to find similar code
   - Check for existing utilities, helpers, or shared modules
   - Verify no duplicate constants, configurations, or data structures exist

2. **CONSOLIDATE BEFORE CREATING**:
   - If similar code exists in 2+ places, create a shared utility FIRST
   - Extract duplicated logic into centralized modules
   - Create configuration files for repeated constants/data
   - Import and reuse rather than copy-paste

3. **SHARED CODE LOCATIONS**:
   - `codesentinel/utils/` - Shared utility functions
   - `codesentinel/core/` - Core business logic
   - `codesentinel/utils/root_policy.py` - Root directory policy (example of DRY)
   - Configuration files - Centralized data (JSON, TOML, constants)

**Recent DRY Success Examples**:
- ✅ Created `codesentinel/utils/root_policy.py` to eliminate duplicate ALLOWED_ROOT_FILES/DIRS
- ✅ Modularized CLI commands into `*_utils.py` to eliminate duplication in `__init__.py`
- ✅ Created `doc_utils.py` to share documentation verification functions

**DRY Violations are Efficiency Violations**:
- Multiple implementations of the same logic = Technical debt
- Duplicate constants = Maintenance nightmare
- Copy-paste code = Bug multiplication
- **Action**: Always refactor duplicates into shared modules

### User-Facing Path Display Policy (PERMANENT)

**MANDATORY: Display repository-relative paths in all user-facing output**

When displaying file paths, directory paths, or any filesystem locations to users:

1. **NEVER show absolute paths** beyond the repository root
2. **ALWAYS show paths relative to repository root** with the repository name as prefix
3. **Use forward slashes** for cross-platform consistency
4. **Prefix with repository name** (e.g., `CodeSentinel/`)

**Implementation Requirements**:
- Create helper function to convert absolute paths to relative paths
- Pattern: `repo_name/relative/path/to/file.ext`
- Apply to ALL user-visible output: logs, reports, terminal messages, UI displays

**Examples**:

✅ **CORRECT:**
```
✓ Report generated: CodeSentinel/tests/beta_testing/v1.1.0-beta.1/iterations/iteration_1.md
✓ Environment: CodeSentinel/tests/beta_testing/v1.1.0-beta.1/environment/venv_abc123
✓ Removed: CodeSentinel/dist/old_build.whl
```

❌ **INCORRECT:**
```
✓ Report generated: C:\Users\joedi\Documents\CodeSentinel\tests\beta_testing\v1.1.0-beta.1\iterations\iteration_1.md
✓ Environment: /home/user/projects/CodeSentinel/tests/beta_testing/v1.1.0-beta.1/environment/venv_abc123
✓ Removed: C:\Users\joedi\Documents\CodeSentinel\dist\old_build.whl
```

**Why This Matters**:
- **Security**: Prevents exposure of system user paths and directory structures
- **Privacy**: Doesn't leak username or home directory locations
- **Portability**: Paths work across Windows, macOS, Linux
- **Clarity**: Users see workspace-relative locations that are meaningful in project context
- **Consistency**: All output has uniform path representation

**Helper Function Pattern**:
```python
def _get_relative_path(absolute_path):
    """Convert absolute path to repository-relative path."""
    try:
        abs_path = Path(absolute_path)
        repo_root = Path.cwd()  # Or detect via .git directory
        rel_path = abs_path.relative_to(repo_root)
        return f"RepoName/{rel_path}".replace("\\", "/")
    except ValueError:
        # Fallback for paths outside repo
        return f"RepoName/.../{abs_path.name}"
```

**Application Scope**:
- Terminal/console output
- Log messages
- Error messages
- Report generation
- Status updates
- File operation confirmations
- Any user-visible path reference

**Exceptions** (use absolute paths ONLY for):
- Internal logging to debug files (not shown to user)
- System calls that require absolute paths
- Configuration files that explicitly store absolute paths

This is a **PERMANENT, CONSTITUTIONAL-TIER** policy that applies to ALL current and future projects.

### Pre-Edit File State Validation

**CRITICAL: Always check file state before making ANY edits**

Before invoking `replace_string_in_file`, `edit_notebook_file`, or similar editing tools:

1. **READ FIRST**: Use `read_file` to inspect current file state
2. **VERIFY CONTEXT**: Ensure the code you're about to edit actually exists
3. **CHECK FOR DUPLICATES**: Confirm imports/blocks aren't already present
4. **ASSESS STRUCTURE**: Understand surrounding code to avoid corruption

**Why this is mandatory:**
- Prevents duplicate imports and code blocks
- Avoids file corruption from mismatched oldString patterns
- Ensures edits are contextually appropriate
- Reduces failed edit attempts and token waste

**Pattern to follow:**
```python
# ❌ WRONG: Edit without reading
replace_string_in_file(...)  # May fail or duplicate code

# ✅ CORRECT: Read, assess, then edit
read_file(path, start, end)  # Inspect current state
# Analyze what's present
# Craft precise oldString with context
replace_string_in_file(...)  # Clean, targeted edit
```

### ORACL™ Integration

**Lightweight Intelligent Decision Support - Use for high-impact decisions only**

ORACL™ is an intelligent archive-based decision support system that provides historically-aware context. Use ORACL™ to improve decision accuracy and compliance WITHOUT adding overhead to simple operations.

#### When to Query ORACL™ (High-Impact Decisions Only)

**[OK] DO query ORACL™ for:**
- Policy violation handling (root cleanup, unauthorized files)
- Cleanup strategy decisions (archive vs. move vs. delete)
- Dependency update decisions (breaking changes, security patches)
- Large-scale refactoring (pattern selection, migration strategy)
- Recurring issues (pattern analysis, historical success rates)

**[FAIL] DON'T query ORACL™ for:**
- Simple file reads/writes
- Standard CLI operations
- Trivial decisions with no historical pattern
- Operations < 5 seconds execution time
- Read-only queries with no side effects

#### Lightweight Integration Pattern

```python
# ONLY for high-impact decisions:
from codesentinel.utils.archive_decision_provider import get_decision_context_provider

# Query historical context
provider = get_decision_context_provider()
context = provider.get_decision_context(
    decision_type="policy_violation_handling",  # or "cleanup_strategy", "dependency_update"
    current_state={
        "violation_type": "unauthorized_file_in_root",
        "severity": "medium",
        "file_pattern": "*.tmp"
    },
    search_radius_days=30  # How far back to search
)

# Use context to inform decision
if context and context.confidence_score > 0.7:
    # High confidence - use ORACL™ recommendation
    recommended_action = context.recommended_actions[0]
    print(f"ORACL™ suggests: {recommended_action} (confidence: {context.confidence_score:.0%})")
    # Execute with high confidence
else:
    # Low/no confidence - use default logic or ask user
    # Fall back to standard decision-making

# ALWAYS report outcome (builds intelligence)
provider.report_decision_outcome(
    decision_type="policy_violation_handling",
    state={"violation_type": "unauthorized_file_in_root"},
    action="archive",  # What you actually did
    outcome="success",  # or "failure"
    reason="File successfully moved to quarantine_legacy_archive/"
)
```

#### ORACL™ Decision Types

- `policy_violation_handling` - Root policy, security violations
- `cleanup_strategy` - File/directory cleanup decisions
- `dependency_update` - Package update decisions
- `archive_operation` - Archival strategy decisions

#### Performance Guidelines

- **Target latency**: < 100ms for cached queries, < 500ms for cold queries
- **Cache TTL**: 30 minutes for decision context (auto-managed)
- **Minimal overhead**: Decision context queries are O(1) to O(log n)
- **Fail gracefully**: If ORACL™ unavailable, fall back to default logic

#### Confidence Score Interpretation

- **≥ 0.90**: Very high confidence - auto-execute recommended action
- **0.70-0.89**: Good confidence - execute with logging
- **0.50-0.69**: Moderate confidence - consider alternatives or ask user
- **< 0.50**: Low confidence - use default logic, don't rely on ORACL™

#### Current ORACL™ Integrations

**[OK] Active Integrations** (lightweight, high-impact only):

1. **Dev Audit Agent Mode** (`codesentinel !!!! --agent`)
   - Queries ORACL™ for policy violation patterns
   - Enriches agent context with historical success rates
   - Adds confidence scores to remediation recommendations
   - Location: `codesentinel/cli/dev_audit_utils.py`

2. **Root Directory Cleanup** (`codesentinel clean --root`)
   - `suggest_action_for_file()`: Queries ORACL™ before suggesting actions
   - `execute_cleanup_actions()`: Reports outcomes back to ORACL™
   - Builds intelligence on successful/failed cleanup strategies
   - Location: `codesentinel/cli/root_clean_utils.py`

**Additional Integration Opportunities** (future consideration):

- Dependency update decisions (security patch application)
- Large refactoring strategy selection
- Configuration migration planning
- Test coverage optimization
- Performance tuning recommendations

**Integration Philosophy**:
- ORACL™ calls are **optional** - always fail gracefully
- Only query for **high-impact decisions** (not simple operations)
- Always **report outcomes** to build intelligence
- Target < 100ms latency for cached queries

### ORACL™ Memory Ecosystem (3-Tier Architecture)

To enhance agent efficiency and long-term learning, ORACL™ is integrated with a 3-tier memory system. This allows the agent to access context at different levels of granularity, from immediate task details to deep historical wisdom.

#### Tier 1: Session Tier (Short-Term Cache)
- **Component**: `codesentinel/utils/session_memory.py`
- **Purpose**: High-speed, ephemeral cache for the **current, active task**. Prevents re-reading files and re-analyzing decisions within a single work session.
- **Lifetime**: **0-60 minutes**.
- **When to Use**: For immediate context related to the task at hand.
  - *Query*: "What was the summary of the file I just read?"
  - *Action*: Access via `SessionMemory` instance.

#### Tier 2: Context Tier (Mid-Term Aggregates)
- **Component**: `codesentinel/utils/oracl_context_tier.py`
- **Purpose**: Stores curated summaries from **recently completed sessions** (e.g., last few days). Provides context on what was recently accomplished.
- **Lifetime**: **7 days** (rolling window).
- **When to Use**: To understand the context of recent, related work.
  - *Query*: "What were the key files involved in the task I completed yesterday?"
  - *Action*: Use `get_weekly_summaries()` from the context tier module.

#### Tier 3: Intelligence Tier (Long-Term Archive)
- **Component**: The main ORACL™ Archive (`archive_index_manager.py`, `archive_decision_provider.py`).
- **Purpose**: Permanent storage for identifying **significant, historical patterns and strategies**.
- **Lifetime**: **Permanent**.
- **When to Use**: For strategic decisions requiring historical wisdom.
  - *Query*: "What is the historically most successful way to resolve a specific policy violation?"
  - *Action*: Use `get_decision_context_provider()` as per the standard ORACL™ integration pattern.

#### Data Flow (One-Way Promotion)

`Tier 1 (Session)` → `Tier 2 (Context)` → `Tier 3 (Intelligence)`

1.  **Session to Context (Automatic)**: At the end of a successful agent session, a summary is automatically promoted from Tier 1 to Tier 2. This is a non-blocking, background operation.
2.  **Context to Intelligence (Weekly Task)**: A scheduled maintenance task analyzes the weekly summaries in Tier 2. High-confidence patterns are promoted to the permanent Tier 3 archive.

As an agent, you do not need to manage this promotion. Your responsibility is to **query the correct tier** for the information you need. Start with the lowest, fastest tier and move up as required.

### README Rebuild Root Validation

**CRITICAL: Always validate root directory before README rebuild**

When executing README rebuild operations:

1. **ROOT CLEANUP FIRST**: Call root directory validation/cleanup before analyzing repo structure
2. **OPTIMAL DATA**: Ensure file structure diagram reflects compliant, clean repository state
3. **POLICY ENFORCEMENT**: Root must meet specification before documentation generation

**Implementation requirement:**
- `update readme --rebuild` must invoke `clean --root --full --dry-run` or equivalent validation
- Report any policy violations detected during root scan
- Optionally offer to fix violations before proceeding with rebuild
- Document root state in rebuild operation log

**Why this is mandatory:**
- README should reflect ideal repository state, not current violations
- File structure diagrams guide contributors - must show proper organization
- Prevents documenting temporary/unauthorized files as permanent structure
- Aligns documentation with SEAM Protection™ standards

---