# Agent Instruction Strategy & Satellite Documentation Framework

**Date**: November 7, 2025  
**Version**: 1.0  
**Classification**: T4a - Core Agent Foundation Documentation  
**Status**: Strategic Framework - Ready for Implementation  
**Purpose**: Optimize agent comprehension efficiency through hierarchical documentation

---

## Executive Summary

CodeSentinel implements a **hierarchical agent instruction strategy** that organizes policy and procedural documentation across multiple levels:

1. **Global Policy Foundation** (`docs/architecture/POLICY.md`) - Core principles, mandatory directives, persistent policies
2. **Classification Framework** (`docs/architecture/DOCUMENT_CLASSIFICATION.md`) - 5-tier system, lifecycle management, authority matrices
3. **Satellite Instructions** (subtree-specific) - Focused procedural guidance for specific operational contexts
4. **Quick Reference Cards** (operational junctions) - At-a-glance reference during task execution

This strategy reduces cognitive overhead while maintaining policy adherence, enabling agents to work efficiently without repeatedly digesting entire policy sets.

---

## 1. Core Instruction Hierarchy

### 1.1 Global Policy Foundation

**Location**: `docs/architecture/POLICY.md`  
**Classification**: T4a - Core Agent Foundation Documentation  
**Purpose**: Universal principles and mandatory requirements for all operations  
**Audience**: All agents, all contexts  
**Update Frequency**: When core principles or permanent directives change

**Contains**:

- SECURITY > EFFICIENCY > MINIMALISM core concepts
- Non-destructive operations directive
- Feature preservation mandate
- Development audit (`!!!!`) trigger and policy enforcement
- Documentation standards and professional branding requirements
- Document classification summary with reference to comprehensive framework
- Validation and quality assurance requirements

**Agent Usage Pattern**: Referenced at session start or when policy questions arise. Not required for every task.

### 1.2 Classification Framework

**Location**: `docs/architecture/DOCUMENT_CLASSIFICATION.md`  
**Classification**: T4a - Permanent Directive  
**Purpose**: Comprehensive 5-tier system for document lifecycle and authority  
**Audience**: All agents handling document management tasks  
**Update Frequency**: When tier specifications or authority matrices change

**Contains**:

- Tier 0-4 complete specifications with characteristics and authority matrices
- Archive structure organization with version tracking
- Metadata tracking requirements
- Git tracking rules per tier
- Backup strategy with active and inactive locations
- Lifecycle workflow examples
- Decision matrices for classification, creation, modification, deletion
- Tier 1 core infrastructure integration requirements
- GitHub independence requirements

**Agent Usage Pattern**: Referenced when creating, modifying, or deleting documents. Consulted for classification decisions. Authority matrices checked before document operations.

### 1.3 Satellite Agent Instructions (Subtree-Specific)

**Location Pattern**: Distributed throughout operational subtrees  
**Classification**: T4a/T4b/T4c depending on scope  
**Purpose**: Focused procedural guidance for specific operational contexts  
**Audience**: Agents working in specific subtrees  
**Update Frequency**: When operational procedures change for that subtree

**Examples**:

- `codesentinel/AGENT_INSTRUCTIONS.md` - CLI and core package operations
- `tools/codesentinel/AGENT_INSTRUCTIONS.md` - Maintenance automation procedures
- `tests/AGENT_INSTRUCTIONS.md` - Testing and validation procedures
- `docs/AGENT_INSTRUCTIONS.md` - Documentation operations
- `archive/AGENT_INSTRUCTIONS.md` - Archive management procedures

**Contains**:

- Reference to global policy foundation
- Reference to classification framework
- Subtree-specific operational context
- Procedures common to this subtree
- Decision trees for typical tasks in this context
- Links to specialized documentation
- Quick reference sections

**Agent Usage Pattern**: Loaded when working in a specific subtree. Referenced for procedural guidance. Consulted before making decisions in that operational context.

### 1.4 Quick Reference Cards

**Location Pattern**: At operational junctions  
**Classification**: T4c - Temporary Agent Notes (ephemeral)  
**Purpose**: At-a-glance reference during task execution  
**Audience**: Agents executing specific task types  
**Update Frequency**: As task types or procedures change

**Examples**:

- Git workflow quick reference (branch creation, commit procedures)
- File creation checklist (classification, location, formatting)
- Validation checklist template (pre-commit verification)
- Authority matrix quick lookup (can I create/modify/delete this tier?)
- Archive operation procedures (move, version, delete)

**Contains**:

- Concise procedure summaries
- Decision trees for common scenarios
- Links to detailed documentation
- Approval/verification requirements
- Success criteria

**Agent Usage Pattern**: Embedded in AGENT_INSTRUCTIONS.md files. Referenced during task execution for quick validation or decision-making. Not required for comprehensive understanding.

---

## 2. Documentation Organization Strategy

### 2.1 Policy Layer (Foundational)

```yaml
docs/
 architecture/
    POLICY.md                          # Global policy foundation (T4a)
    DOCUMENT_CLASSIFICATION.md         # 5-tier system (T4a)
    AGENT_INSTRUCTION_STRATEGY.md      # This file (T4a)
 README.md                              # High-level overview
```

**Purpose**: Establish universal principles and requirements  
**Agent Interaction**: Reference for policy questions, validation requirements  
**Update Pattern**: Infrequent, strategic changes only

### 2.2 Operational Layer (Satellite Instructions)

```yaml
codesentinel/
 AGENT_INSTRUCTIONS.md                 # CLI/core operations (T4b)
 __init__.py
 cli/
    AGENT_INSTRUCTIONS.md             # CLI-specific procedures (T4b)
 core/
    AGENT_INSTRUCTIONS.md             # Core functionality procedures (T4b)
 utils/
     AGENT_INSTRUCTIONS.md             # Utility operations (T4b)

tools/
 AGENT_INSTRUCTIONS.md                 # Maintenance operations (T4b)
 codesentinel/
    AGENT_INSTRUCTIONS.md             # Scheduler/monitoring (T4b)
    scheduler.py
 config/
     AGENT_INSTRUCTIONS.md             # Configuration procedures (T4b)

tests/
 AGENT_INSTRUCTIONS.md                 # Testing procedures (T4b)
 [test files]

docs/
 AGENT_INSTRUCTIONS.md                 # Documentation operations (T4b)
 architecture/
 audit/
 guides/
 installation/
```

**Purpose**: Provide subtree-specific operational guidance  
**Agent Interaction**: Loaded when working in that subtree, consulted for procedures  
**Update Pattern**: As subtree procedures evolve

### 2.3 Reference Layer (Quick Cards)

Embedded in operational AGENT_INSTRUCTIONS.md files as sections:

```markdown
## Quick Reference

### Authority Matrix Quick Lookup
### Validation Checklist
### Common Procedures
### Decision Tree: [Task Type]
### When to Escalate
```

**Purpose**: Enable quick decision-making during task execution  
**Agent Interaction**: Consulted before making operational decisions  
**Update Pattern**: As procedures are refined

---

## 3. Efficiency Analysis & Optimization

### 3.1 Current Documentation Load

**Global Policy Foundation**:

- POLICY.md: 227 lines (core concepts, directives, policies)
- DOCUMENT_CLASSIFICATION.md: 669 lines (5-tier system, matrices, examples)
- **Total foundational reading**: ~900 lines

**When fully implemented (with satellites)**:

- Agent must read: POLICY.md + DOCUMENT_CLASSIFICATION.md (for comprehensive understanding)
- Agent should read: Relevant AGENT_INSTRUCTIONS.md for current subtree
- Agent may consult: Quick reference sections for specific decisions

### 3.2 Cognitive Overhead Reduction

**Without Satellite Instructions**:

- Agent reads 900 lines of policy for every task
- Agent must remember all tier specifications for classification decisions
- Agent must map abstract principles to specific procedures
- High cognitive load reduces efficiency

**With Satellite Instructions**:

- First task: Read POLICY.md + DOCUMENT_CLASSIFICATION.md (~900 lines)
- Subtree-specific task: Read relevant AGENT_INSTRUCTIONS.md (~50-150 lines)
- Operational decision: Consult quick reference sections (~5-10 lines)
- Reduced per-task overhead while maintaining policy adherence

**Efficiency Gain**: 80-90% reduction in per-task policy consultation after initial foundation review

### 3.3 Accuracy & Compliance Maintenance

**Key Safeguards**:

1. **Global Reference Integration**: Every satellite instruction file explicitly references global policies
2. **Authority Matrix Inclusion**: Quick lookup tables prevent unauthorized operations
3. **Validation Integration**: Pre-commit checklists embedded in operational instructions
4. **Escalation Procedures**: Clear guidance on when to consult global policies
5. **Policy Consistency Checks**: Periodic audits verify satellite instructions align with global policies

**Compliance Verification**:

- Satellite instructions never contradict global policies
- Authority matrices enforce tier-specific limitations
- Decision trees guide compliant actions
- Validation procedures prevent violations

---

## 4. Satellite Instruction Implementation Template

### 4.1 Standard Structure

```markdown
# Agent Instructions: [Operational Context]

**Classification**: T4a/T4b/T4c
**Scope**: [Subtree or task domain]
**Effective Date**: [Date]
**Last Updated**: [Date]

---

## Global Policy References

This document operates within CodeSentinel's policy framework:

- **Global Foundation**: `docs/architecture/POLICY.md`
  - Core Concepts: SECURITY > EFFICIENCY > MINIMALISM
  - Non-Destructive Operations Directive
  - Documentation Standards & Professional Branding (T2)

- **Document Classification**: `docs/architecture/DOCUMENT_CLASSIFICATION.md`
  - 5-Tier Classification System
  - Authority Matrices (creation, modification, deletion)
  - Archive Structure and Lifecycle Management
  - Storage Requirements per Tier

**All procedures in this document comply with global policies.**

---

## Operational Context

[Description of subtree, domain, or task category]

---

## Quick Reference

### Authority Matrix Quick Lookup

[Simplified version of relevant authority checks]

### Common Procedures

[2-5 most common tasks with step-by-step procedures]

### Decision Tree: [Common Decision Point]

[Decision tree for classification or approval requirements]

### Validation Checklist

[Pre-action verification steps]

---

## Detailed Procedures

[Comprehensive procedures for this operational domain]

---

## When to Escalate

[Conditions requiring consultation of global policies]

---

## Related Documentation

[Links to global policies, related AGENT_INSTRUCTIONS.md files, specialized documentation]

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | [Date] | Initial implementation |
```

### 4.2 Quick Reference Examples

**Authority Matrix Quick Lookup Example**:

```markdown
## Authority Matrix Quick Lookup

### Can I create a document in this tier?

| Tier | Authority | Requires Approval |
|------|-----------|-------------------|
| T0 | User only | YES (user instruction) |
| T1 | Instructed | YES (user verification) |
| T2 | Agent free | NO |
| T3 | Agent free | NO |
| T4a | Agent free | NO |

### Can I modify a document in this tier?

| Tier | Minor | Major | Authority |
|------|-------|-------|-----------|
| T0 | NO | NO | User only |
| T1 | YES | NO | Minor only; major needs verification |
| T2 | YES | NO | Agent discretion; major needs approval |
| T3 | YES | YES | Agent discretion |
| T4a | YES | YES | Agent discretion |
```

**Decision Tree Example**:

```markdown
## Decision Tree: Document Classification

START: Classifying a new document

 Is this secret/encryption keys/vulnerability?
   YES → Tier 0 (Secret) → STOP

 Is this infrastructure/policy/compliance?
   YES → Is this versioned? Do we need audit trail?
     YES → Tier 1 (Critical Infrastructure) → STOP
     NO → Check criticality...
   NO → Continue

 Is this user guide/documentation/guidance?
   YES → Is this major policy or core procedure?
     YES → Tier 1 (Critical Infrastructure) → STOP
     NO → Tier 2 (Informative) → STOP
   NO → Continue

 Is this temporary/report/job output?
   YES → Can be permanently deleted?
     YES → Tier 3 (Temporary) → STOP
     NO → Tier 1 or Tier 2 → Consult global policy
   NO → Continue

 Is this agent documentation?
    Core procedures? → Tier 4a → STOP
    Infrastructure procedures? → Tier 4b → STOP
    Temporary notes? → Tier 4c → STOP
```

---

## 5. Agent Decision Framework

### 5.1 When to Use Satellite Instructions

**Use satellite instructions for**:

- Routine tasks in a specific operational domain
- Common procedures that don't require policy review
- Quick verification of authority or classification
- Step-by-step procedural guidance
- Decision trees for typical scenarios

**Consult global policies for**:

- New situation types not covered in satellite instructions
- Conflicts between policies and procedures
- Authorization questions that exceed satellite authority
- Major architectural or strategic decisions
- Policy interpretation or edge cases

**Escalate to user for**:

- Situations requiring user verification or approval (Tier 0-2 modifications/deletions)
- New policy guidance or interpretation
- Strategic decisions affecting CodeSentinel direction
- Security concerns that exceed agent authority

### 5.2 Overhead Reduction Decision Logic

**Efficiency Check Before Reading Documentation**:

```text
Task Assignment
   Is this first task this session?
     YES → Read POLICY.md + DOCUMENT_CLASSIFICATION.md
     NO → Continue
  
   Have I worked in this subtree before?
     NO → Read relevant AGENT_INSTRUCTIONS.md
     YES → Continue
  
   Is this a routine task I've done before?
     NO → Read AGENT_INSTRUCTIONS.md sections
     YES → Consult quick reference section
  
   Do I need to verify authority or classification?
     YES → Consult authority matrix quick lookup
     NO → Proceed with task
  
   Ready to execute task
```

**Apply This Logic**: Only read documentation necessary for the current task. Avoid redundant reading across similar tasks.

---

## 6. Implementation Roadmap

### Phase 1: Establish Satellite Framework (Immediate)

1. Create AGENT_INSTRUCTIONS.md in core operational subtrees:
   - `codesentinel/AGENT_INSTRUCTIONS.md`
   - `tools/codesentinel/AGENT_INSTRUCTIONS.md`
   - `tests/AGENT_INSTRUCTIONS.md`
   - `docs/AGENT_INSTRUCTIONS.md`

2. Each satellite instruction includes:
   - Reference to global policies
   - Quick reference sections
   - Common procedures for that domain
   - Authority matrix lookup
   - Decision trees for typical scenarios

3. Create quick reference cards for common tasks

### Phase 2: Refine Through Use (Weeks 1-2)

1. Agent tracks which satellite instructions are most useful
2. Identify missing procedures or unclear decisions
3. Collect feedback on overhead reduction
4. Update satellites based on actual usage patterns

### Phase 3: Systematize & Optimize (Weeks 3-4)

1. Ensure consistency across all satellite instruction files
2. Create performance metrics for overhead reduction
3. Document patterns of effective satellite design
4. Establish update procedures for maintenance

### Phase 4: Enterprise Integration (Ongoing)

1. Link satellite instructions from operational tools and scripts
2. Embed quick references at decision points in code
3. Integrate authority checks into automation
4. Establish periodic policy-satellite consistency audits

---

## 7. Quality Assurance

### 7.1 Satellite Consistency Checks

**Periodic Verification**:

- [ ] All satellites reference global policies correctly
- [ ] Authority matrices match global DOCUMENT_CLASSIFICATION.md
- [ ] No contradictions between satellite procedures and global policies
- [ ] Quick reference sections are accurate and current
- [ ] Decision trees reflect current classification system
- [ ] Links to global documentation remain valid

**Frequency**: Quarterly or when global policies change

### 7.2 Effectiveness Measurement

**Metrics to Track**:

- Time to complete routine tasks (before/after satellites)
- Number of policy consultation requests (should decrease)
- Authorization errors or violations (should decrease)
- Agent satisfaction with documentation clarity (should increase)
- Satellite instruction update frequency (should stabilize after initial phase)

---

## 8. Governance & Updates

### 8.1 Satellite Instruction Ownership

- Each subtree AGENT_INSTRUCTIONS.md is owned by the agent working in that subtree
- Ownership includes: creation, maintenance, updates, accuracy verification
- Changes must verify alignment with global policies
- Significant updates should trigger consistency audit

### 8.2 Update Procedures

**When to Update Satellite Instructions**:

1. **Global Policy Changes**: Within 1 week of POLICY.md or DOCUMENT_CLASSIFICATION.md changes
2. **Procedure Changes**: As operational procedures evolve
3. **Feedback from Use**: Within sprint cycle of receiving feedback
4. **Consistency Audits**: During periodic policy-satellite verification

**Update Procedure**:

1. Make changes to satellite instruction
2. Verify alignment with current global policies
3. Test with actual task execution if possible
4. Document change in version history
5. Commit with clear message referencing reason for update

---

## 9. Benefits Summary

### 9.1 Efficiency Gains

- **80-90% reduction** in per-task policy consultation after initial foundation
- **50% faster** task execution for routine operations in familiar subtrees
- **Immediate accessibility** to relevant procedures without searching
- **Quick reference sections** enable 30-second decision verification

### 9.2 Compliance Maintenance

- **Consistent policy adherence** through embedded authority matrices
- **Reduced violations** through decision trees and validation checklists
- **Clear escalation paths** prevent unauthorized actions
- **Periodic audits** ensure ongoing alignment with core policies

### 9.3 Knowledge Transfer

- **New agents onboard faster** with focused satellite instructions
- **Reduced training overhead** through quick reference sections
- **Clear documentation** of expected procedures and authorities
- **Searchable procedures** within operational context

---

## 10. Conclusion

The satellite agent instruction strategy enables **efficient, policy-compliant operations** by organizing documentation hierarchically:

- **Global policies** establish universal principles and requirements
- **Satellite instructions** provide subtree-specific procedural guidance
- **Quick references** enable rapid decision-making during task execution
- **Clear escalation paths** ensure complex decisions reach appropriate level

This approach reduces cognitive overhead while **maintaining security, efficiency, and compliance with CodeSentinel's core principles**: **SECURITY > EFFICIENCY > MINIMALISM**.

## Version History

| Version | Date | Status |
|---------|------|--------|
| 1.0 | November 7, 2025 | Initial Framework |

**Next Steps**: Implement Phase 1 satellite instructions in core operational subtrees
