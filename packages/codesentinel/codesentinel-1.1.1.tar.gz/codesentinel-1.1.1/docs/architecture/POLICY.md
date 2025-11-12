# CodeSentinel Non-Destructive Policy and `!!!!` Trigger

## Fundamental Policy Hierarchy

**Priority Distribution (Descending Importance):**

1. **CORE CONCEPTS** (Absolute Priority)
   - SECURITY > EFFICIENCY > MINIMALISM
   - These three principles guide ALL decisions
   - Higher priority concept always overrides lower priority

2. **PERMANENT DIRECTIVES**
   - Non-negotiable security rules (credential management, audit logging)
   - Cannot be violated under any circumstances
   - Always in effect

3. **PERSISTENT POLICIES**
   - Non-destructive operations, feature preservation, style preservation
   - Can be overridden ONLY when they explicitly violate Core Concepts or Permanent Directives

**This hierarchy is fundamental to CodeSentinel's operating policy.**

## Development Audit Execution

The `!!!!` trigger is a development-audit accelerator that:

- **Executes thoroughly and comprehensively** - Always complete analysis
- **Focuses heavily on the three core concepts** - Security, Efficiency, Minimalism
- **Complies with all directives and policies** - EXCEPT where they would explicitly violate a core concept
- **Never removes features or reduces capability** - Unless security demands it
- **Resolves conflicts and duplications safely** - Following the hierarchy
- **Operates in non-destructive, feature-preserving mode by default**

Implementation details:

- Config carries a persistent `policy` section with:
  - `non_destructive: true`
  - `feature_preservation: true`
  - `conflict_resolution: "merge-prefer-existing"`
  - `principles: ["SECURITY", "EFFICIENCY", "MINIMALISM"]`
  - `hierarchy: ["CORE_CONCEPTS", "PERMANENT_DIRECTIVES", "PERSISTENT_POLICIES"]`
- Config also carries `dev_audit.trigger_tokens` including `!!!!` and `dev_audit.enforce_policy: true`.
- DevAudit reads and reports policy, and does not perform any destructive operations.
- Future automation invoked by `!!!!` MUST respect this policy hierarchy

This policy is persistent and loaded on every run, guaranteeing that `!!!!` never results in feature loss unless absolutely required by security concerns.

---

## Documentation Standards & Professional Branding (T2-Permanent Directive)

**Classification**: T2 - Permanent Directive  
**Effective Date**: November 2025  
**Scope**: All CodeSentinel documentation, comments, and public-facing content  
**Authority**: Core Principle - Elegant Professionalism

### Professional Standards Directive

**All documentation will maintain professional elegance through consistent styling:**

1. **Emoji Usage Policy**
   - Use checkmarks and X marks only when they add clarity to conditions or acceptance criteria
   - Use other emojis ONLY when they meaningfully help visualize conditions or states
   - Avoid decorative emoji that does not serve functional purpose
   - Never use emoji that adds visual clutter or reduces professional presentation
   - All emoji must pass the "elegant professionalism" test: Does this enhance understanding or detract from it?

2. **Formatting Standards**
   - All documentation formatted cleanly and uniformly
   - Projects competence, clarity, and attention to detail
   - Consistent heading hierarchy throughout
   - Proper spacing and visual separation of concepts
   - No excessive decoration or unnecessary embellishment

3. **Professional Branding**
   - Subtle branding that reflects CodeSentinel's security-first, professional identity
   - Language that demonstrates expertise and reliability
   - Consistent tone across all documentation
   - Architecture and structure that shows careful thought and planning

4. **Character Encoding Requirements**
   - All documentation in UTF-8 encoding (no BOM)
   - No corrupted or garbled characters
   - Tree structures rendered as clean ASCII (, , ) not Unicode box-drawing
   - All non-ASCII characters must be intentional and serve a purpose

### Standards Enforcement

- Code reviews will verify documentation meets these standards
- CI/CD pipeline will validate UTF-8 encoding and character integrity
- Policy applies to README files, architectural documents, code comments, and API documentation
- Violations identified during `!!!!` audits will be flagged for correction

### Professional Standards Rationale

Professional documentation builds trust with enterprise users and demonstrates security-first competence. Elegant simplicity in presentation reflects the same care applied to code security and reliability. This directive reinforces CodeSentinel's commitment to professionalism alongside its security principles.

---

## Document Classification & Lifecycle Management (T4a-Permanent Directive)

**Classification**: T4a - Core Agent Foundation Documentation  
**Effective Date**: November 7, 2025  
**Reference**: `docs/architecture/DOCUMENT_CLASSIFICATION.md`

### Summary

CodeSentinel implements a 5-tier document classification system determining document lifecycle, archival strategy, user interaction requirements, and branding standards:

- **Tier 0 (Secret)**: Encryption capable, user-only deletion, maximum protection
- **Tier 1 (Critical Infrastructure)**: Version-tracked, never deleted without user instruction, minimal branding
- **Tier 2 (Informative)**: Agent can create freely, major changes need approval, moderate branding
- **Tier 3 (Temporary/Job Reports)**: Agent full discretion, consolidate iterations, can be permanently deleted
- **Tier 4 (Agent Documentation)**: Agent-governed with 4a/4b/4c subdivisions based on scope

### Key Principles

1. **Tier determines authority**: Classification tier explicitly defines who can create, modify, and delete documents
2. **Archive organization**: Documents organized by tier and type; versions tracked; inactive copies preserved
3. **User verification**: Deletion requires verification for Tiers 0, 1, 2, and user-requested Tier 4
4. **Backup strategy**: Active documents backed up daily; inactive archives preserved indefinitely
5. **Git tracking**: Tier-specific tracking rules; archive directories excluded from version control
6. **Branding compliance**: Branding applied per tier classification and professional standards

### Archive Structure

```yaml
archive/
 active/
    tier0_secret/
    tier1_critical/
    tier2_informative/
    tier3_temporary/
    tier4_agent/
 inactive/
    [archived inactive documents]
 metadata/
     archive_index.json
     classification_audit.log
     backup_manifest.json
```

### Backup Locations

- **Active Backup**: `{repository_parent_directory}/archive_backup/`
- **Inactive Archive**: `{repository}/archive/inactive/`
- **Git Tracking**: Per-tier rules; archive directories not tracked

### Implementation

All new documents must be classified at creation. Existing documents will be classified through audit process. Classification determines complete document lifecycle from creation through archival or deletion.

**Storage Requirements**:

- All documents must be stored in proper location according to tier classification
- All documents must adhere to all CodeSentinel policies and procedures
- Tier classification determines storage location, backup strategy, and lifecycle management
- Violations of classification requirements or storage policies flagged during audits

See `docs/architecture/DOCUMENT_CLASSIFICATION.md` for comprehensive policy details, lifecycle workflows, decision matrices, and implementation procedures.

---

## Agent Instruction Optimization Strategy (T4a-Permanent Directive)

**Classification**: T4a - Core Agent Foundation Documentation  
**Effective Date**: November 7, 2025  
**Reference**: `docs/architecture/AGENT_INSTRUCTION_STRATEGY.md`

### Strategy Summary

CodeSentinel implements a hierarchical agent instruction strategy to optimize comprehension efficiency while maintaining policy adherence:

- **Global Foundation**: Universal principles and mandatory requirements
- **Satellite Instructions**: Subtree-specific procedural guidance
- **Quick References**: At-a-glance decision support during task execution

### Strategic Rationale

**Reduce Cognitive Overhead**:

- Global policies read once per session: ~900 lines
- Satellite instructions read per subtree: ~50-150 lines each
- Quick references consulted for decisions: ~5-10 lines
- 80-90% reduction in per-task policy consultation

**Maintain Compliance**:

- Satellite instructions explicitly reference global policies
- Authority matrices embedded prevent unauthorized operations
- Decision trees guide compliant actions
- Periodic consistency audits ensure alignment

### Satellite Architecture

Satellite AGENT_INSTRUCTIONS.md files distributed throughout operational subtrees:

- `codesentinel/AGENT_INSTRUCTIONS.md` - CLI/core operations
- `tools/codesentinel/AGENT_INSTRUCTIONS.md` - Maintenance automation
- `tests/AGENT_INSTRUCTIONS.md` - Testing procedures
- `docs/AGENT_INSTRUCTIONS.md` - Documentation operations
- Additional satellites per operational domain as needed

**Usage Pattern**: Load satellite when working in specific subtree. Consult quick reference for operational decisions. Escalate to global policies for new situations or conflicts.

See `docs/architecture/AGENT_INSTRUCTION_STRATEGY.md` for comprehensive strategy details, implementation templates, and satellite design patterns.

---

**Classification**: T4a - Core Agent Foundation Documentation  
**Effective Date**: November 7, 2025  
**Authority**: Core Principle - SECURITY > EFFICIENCY > MINIMALISM

### Directive Statement

**All work must pass final validation before commits or task closure.**

### Validation Requirements

1. **Pre-Commit Validation**
   - All changes reviewed for correctness and completeness
   - Files checked for syntax errors and formatting compliance
   - Policy adherence verified for document classification
   - Storage locations confirmed correct per tier classification
   - No broken references or incomplete implementations

2. **Test Coverage**
   - Code changes validated with unit tests when applicable
   - Documentation tested for broken links and correct formatting
   - Configuration files validated for proper syntax
   - Archive structure verified if modified

3. **Policy Compliance Check**
   - All files stored in correct locations per classification tier
   - Branding applied correctly per tier requirements
   - Version tracking implemented if applicable
   - Git tracking rules followed
   - Agent authority limits respected

4. **Documentation Completeness**
   - Changes documented in commit messages
   - Related policies updated if affected
   - Examples provided where needed
   - Decision rationale recorded

5. **Task Closure Validation**
   - All objectives met and verified
   - No outstanding issues or TODOs
   - Related documentation updated
   - Changes committed successfully
   - Validation steps documented

### Validation Checklist Template

Before suggesting commits or closing tasks:

- [ ] All syntax errors resolved (markdown, code, config)
- [ ] File locations correct per classification tier
- [ ] Branding compliance verified
- [ ] Policy requirements met
- [ ] Broken links or references fixed
- [ ] Documentation updated
- [ ] Commit message comprehensive
- [ ] Related policies reviewed and updated
- [ ] No outstanding blockers or TODOs
- [ ] Final review passed

### Validation Rationale

Validation before closure ensures high quality, prevents regressions, maintains policy compliance, and demonstrates professional execution. This directive reinforces CodeSentinel's commitment to security and reliability through careful verification practices.

---

## Permanent Global Policy Amendment: Duplication Mitigation

**Constitutional (Irreversible) Tier**

- All domains, satellites, and workflows must enforce intelligent duplication mitigation.
- Duplicates are to be merged or deleted if and only if:
  - Data preservation is guaranteed (no unique content lost).
  - Minimalism is enforced (no unnecessary files or redundancy).
- Intelligent analysis (automated or manual) must be performed before any merger or deletion.
- Legacy or ambiguous versions are archived if needed, but redundant files are removed to maintain a clean, minimal, and secure codebase.
- This amendment is permanent and global, superseding previous non-destructive-only rules where duplication is present.

**Integration:**

- Applies to all domains, satellites, compliance audits, and agent-driven workflows.
- All future policy changes must cascade through this mechanism.
- The system remains whole, secure, and improved, with minimalism as a core principle.
