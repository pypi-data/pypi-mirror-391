# CodeSentinel Maintenance Automation Instructions

**Scope**: Maintenance scripts and automation tools (`tools/codesentinel/`)

---

## Core Principles

- **Reliability**: Scripts must be robust and handle errors gracefully.
- **Non-Destructive**: Always prefer archiving to deletion. All cleanup operations must follow the `quarantine_legacy_archive/` policy.
- **Idempotency**: Where possible, scripts should be safe to run multiple times without negative side effects.

---

## Key Utilities

- `tools/codesentinel/defrag_instructions.py`: Schema-driven utility for reorganizing instruction files.
- `tools/codesentinel/scheduler.py`: Task scheduler for daily and weekly maintenance jobs.
- `tools/codesentinel/root_cleanup.py`: Policy enforcement for the root directory.

---

## Development Workflow

1. **Define Task**: Clearly specify the goal of the maintenance script.
2. **Check for Existing Tools**: Before creating a new script, verify if existing utilities in `codesentinel/utils/` can be used.
3. **Implement with Safeguards**: Include `--dry-run` and `--force` flags for any operations that modify or move files.
4. **Add Logging**: All scripts must log their operations and outcomes.
