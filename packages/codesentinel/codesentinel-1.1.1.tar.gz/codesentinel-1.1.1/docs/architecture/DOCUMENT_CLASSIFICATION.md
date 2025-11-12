# CodeSentinel Document Classification Policy

**Effective Date**: November 7, 2025  
**Version**: 1.0  
**Classification**: T4a - Permanent Directive  
**Authority**: Core Principle - SECURITY > EFFICIENCY > MINIMALISM

---

## Overview

This policy establishes a 5-tier classification system for managing CodeSentinel documentation. Classification determines document lifecycle, archival strategy, user interaction requirements, and branding standards. All CodeSentinel documents must be classified according to this system.

---

## Tier Classification System

### Tier 0: Secret

**Purpose**: Highly sensitive information requiring maximum protection

**Characteristics**:

- Encryption capable and recommended
- Never deleted without explicit user instruction
- Deletion requires verification before execution
- Upon verified deletion: remove from repo, clear all caches and backups
- No branding applied

**Agent Authority**:

- [x] Create when explicitly instructed by user
- [x] Suggest creation with user approval
- [ ] Modify without approval
- [ ] Delete without verification
- [x] Archive and organize

**Lifecycle**:

- Creation: User directive only
- Modification: User approval required
- Deletion: Explicit user instruction -> agent verification request -> user confirmation -> deletion and cache purge
- Archival: Organized by type, encrypted, separately tracked

**Examples**:

- Encryption keys and secrets
- Security vulnerabilities (pre-disclosure)
- Confidential audit findings
- Private authentication tokens

**Storage**:

- Separate encrypted storage (NOT in archive/ directory structure)
- User-controlled encryption and access management
- Not git-tracked; completely outside repository
- Backup location: User-specified encrypted container in parent directory or external storage
- No standard archive structure for Tier 0 documents
- Deletion removes all copies: repo cache, external backups, and encrypted storage

---

### Tier 1: Critical Infrastructure

**Purpose**: Infrastructure policies, compliance documents, and versioned critical records

**Characteristics**:

- Documents in 'reports' directory (critical reports)
- All versions tracked and archived
- Never deleted without explicit user instruction
- Deletion removes from main repo and marks archive as inactive
- No major changes without explicit user verification
- Minimal branding (subtle CodeSentinel identifier only)

**Agent Authority**:

- [x] Create when instructed or required by procedural convention
- [x] Suggest infrastructure policy for user review
- [ ] Modify without approval (major changes require verification)
- [ ] Delete without explicit user instruction
- [x] Archive all versions and track history

**Lifecycle**:

- Creation: User directive or procedural requirement
- Modification: Tracked as new version; major changes require user verification
- Deletion: Explicit user instruction -> archive marked inactive, copy removed from main repo
- Archival: archive/[type]/[doc_name]/ with version subdirectories

**Version Management**:

- All versions retained in same directory
- Numbered or dated subdirectories: v1/, v2/, or 2025-11-07/, 2025-11-14/
- Deletion removes active version, archives all historical versions

**Examples**:

- Infrastructure compliance documents
- Security policies and procedures
- Audit reports and compliance certifications
- Capacity planning and architecture decisions
- Incident response logs

**Storage**:

- Git-tracked: active documents in main repo
- Not git-tracked: archive directory
- Backup location: parent directory/archive_backup/
- Inactive marker: archive/inactive/[type]/[doc_name]/

**Core Infrastructure Integration**:

Tier 1 documents are part of the core CodeSentinel package. Infrastructure and procedures for their operation and maintenance are built into core functionality and persist across versions:

- **Install/Upgrade Generation**: Tier 1 infrastructure files and folders are automatically generated at install time or during upgrade as infrastructure evolves and expands through versions
- **Feature-Based Infrastructure**: Infrastructure installation depends on enabled features during setup; install remains light by including only required infrastructure for selected features
- **Optional Feature Installation**: When users add optional features after initial install, necessary infrastructure is automatically installed
- **Agent Instructions**: Agent instructions at all operational junctions are generated as part of infrastructure setup to ensure consistent repository operation
- **Mandatory Infrastructure**: Intelligently determined mandatory infrastructure works with or without GitHub Copilot integration and GitHub integration
- **Standalone Operation**: Mechanisms exist to build and operate CodeSentinel without GitHub Copilot integration and without GitHub integration
- **Version Persistence**: Tier 1 infrastructure persists and evolves across CodeSentinel versions while maintaining backward compatibility

---

### Tier 2: Informative Documentation

**Purpose**: Non-critical documentation providing guidance and information

**Characteristics**:

- Agent can create without restriction
- Major changes or deletions require explicit user approval
- Moderate, tasteful branding compliant with CodeSentinel professional standards
- Content updates can be made freely; structural or major content changes need approval

**Agent Authority**:

- [x] Create without approval
- [x] Make minor content updates
- [ ] Major modifications without user approval
- [ ] Delete without user approval
- [x] Suggest improvements and branding updates

**Lifecycle**:

- Creation: Agent discretion
- Minor modifications: Agent discretion
- Major modifications: User approval required
- CodeSentinel logo or name where appropriate
- Professional formatting per Documentation Standards policy
- No excessive decoration

**Examples**:

- User guides and tutorials
- Architecture documentation
- Development roadmaps
- Setup and installation guides
- Best practices documentation
- Feature specifications

**Storage**:

- Git-tracked: active documents in main repo
- Not git-tracked: archive directory
- Backup location: parent directory/archive_backup/
- Single version typically (unless major revisions tracked)

---

### Tier 3: Temporary & Routine Job Reports

**Purpose**: Ephemeral operational reports and job outputs

**Characteristics**:

- Agent has full discretion to create and destroy
- Job reports at different stages/iterations consolidated into single summary document
- Reports assessed for future usefulness; retained only when needed
- Complete deletion allowed (not archived to main backup)
- No branding

**Agent Authority**:

- [x] Create without approval
- [x] Modify without approval
- [x] Delete without approval
- [x] Consolidate and summarize
- [x] Assess utility and determine retention

**Lifecycle**:

- Creation: Automatic or agent discretion
- Modification: Agent discretion (iteration, refinement)
- Consolidation: Multiple iterative reports merged into summary
- Deletion: Agent discretion (can be permanent, need not archive)
- Archival: Optional; usually not retained

**Consolidation Pattern**:

- Multiple iteration reports (job_stage1.md, job_stage2.md, job_stage3.md)
- Consolidated into job_summary.md
- Original iteration reports can be deleted
- Summary retained if useful for historical reference

**Retention Assessment**:

- Assess after creation: Will this be useful to reference later?
- Keep: Yes -> retain in archive
- Discard: No -> delete permanently
- Uncertain: Archive in temporary storage, review at intervals

**Examples**:

- Test execution reports
- Build logs and CI/CD outputs
- Iterative prototyping reports
- Temporary analysis documents
- Job status reports
- Maintenance run outputs
- Automated audit results

**Storage**:

- Temporary location during creation
- Optionally archived if useful
- No git tracking required
- Not included in main backup (ephemeral)

---

### Tier 4: Agent Documentation

**Purpose**: Documentation governing agent behavior, procedures, and communication

**Characteristics**:

- Agent has primary authority to create and maintain
- Agent-only documents can be freely modified/deleted by agent
- Documents created by user request require user verification for deletion
- Divided into 4a, 4b, 4c based on scope and authority level
- Serves as source of truth for agent behavior

**Agent Authority**:

- [x] Create (agent-initiated) without approval
- [x] Modify (agent-initiated) without approval
- [x] Delete (agent-initiated) without approval
- [ ] Delete (user-requested) without verification
- [x] Update procedures and documentation

**Lifecycle**:

- Creation: Agent discretion
- Modification: Agent discretion
- Deletion (agent-initiated): Permitted without approval
- Deletion (user-requested): Requires user verification before execution
- Archival: By classification level (4a/4b/4c)

**Branding**: Determined by classification level

---

#### Tier 4a: Core Agent Foundation Documentation

**Purpose**: Foundational directives governing all agent decision-making

**Characteristics**:

- Core principles, permanent directives, persistent policies
- Explicit instructions defining consistent agent behavior
- Acts as source of truth for agent operations
- Changes require understanding of impact on all agent operations
- Should be consulted before any major decision

**Classification**: T4a - Permanent Directives (same classification as this document)

**Authority**: User modifies via explicit instruction; agent suggests improvements

**Examples**:

- POLICY.md - Non-destructive policy, `!!!!` trigger, policy hierarchy
- DOCUMENTATION_STANDARDS.md - Professional formatting and emoji usage rules
- PERMANENT_DIRECTIVES.md - Security-first principles, core operating procedures
- CORE_PRINCIPLES.md - SECURITY > EFFICIENCY > MINIMALISM
- AGENT_BEHAVIOR_RULES.md - Consistent decision-making framework

**Storage**:

- Git-tracked in docs/architecture/
- Version controlled for audit trail
- Backup location: parent directory/archive_backup/
- Never deleted; only versioned and superseded

**Purpose**: Agent procedures for infrastructure management and operational tasks

- Infrastructure maintenance documentation
- Procedural checklists and workflows
- Agent modification permitted; user verification for deletion of user-requested docs

**Examples**:

- Setup and deployment procedures
- Database migration procedures
- Backup and restore procedures
- Release procedures
- Maintenance checklists

- Git-tracked or separate as appropriate
- Organized by procedure type
- Version tracked for historical reference

---

#### Tier 4c: Temporary Agent Operations Documentation

**Purpose**: Agent-to-agent communication and temporary operational notes

**Characteristics**:

- Status updates and progress notes
- Agent-to-agent knowledge transfer
- Temporary operational documentation
- Complete discretion for agent creation/modification/deletion

**Examples**:

- Agent session notes
- Status updates on ongoing tasks
- Temporary workarounds and notes
- Agent-to-agent communication logs
- Operational context and background

**Storage**:

- Not necessarily git-tracked
- Ephemeral storage acceptable
- Can be deleted when no longer needed

---

## Storage Locations

### Tier 0 (Secret) Storage

**NOT stored in standard archive directory**

**Separate Encrypted Storage**:

- Location: Separate encrypted container (not in repository or archive/ directory)
- Access: User-controlled encryption; agent cannot access without user authorization
- Backup: Encrypted backup location specified and controlled by user
- Management: Outside of standard archive structure for maximum security
- Metadata: Minimal metadata; reference stored separately in secure location
- Recovery: User-managed recovery procedures for encrypted storage

**Note**: Tier 0 documents are completely separate from the archive structure below. They are not tracked in archive/tier0_secret/ or any archive directory.

---

## Archive Organization Structure

```
archive/
 active/
    tier1_critical/
       [doc_type]/
          [doc_name]/
              v1/
              v2/
              metadata.json
       ...
    tier2_informative/
       [doc_type]/
          [doc_name]/
              [doc_name].md
              metadata.json
       ...
    tier3_temporary/
       [job_type]/
          job_summary.md
          metadata.json
       ...
    tier4_agent/
        4a_core/
           [core_doc].md
           metadata.json
        4b_infrastructure/
           [procedure].md
           metadata.json
        4c_temporary/
            [operation_note].md
            metadata.json

 inactive/
    tier1_critical/
       [doc_type]/
           [doc_name]/
               archived_versions/
    tier2_informative/

**Note on Tier 0**: Secret documents are NOT included in this archive structure. They are stored in separate encrypted storage managed by the user.

  "tiers": {
    "tier1": {
      "count": 23,
      "count": 34,
      "location": "archive/active/tier3_temporary/"
    },
    "tier4": {
      "count": 25,
      "location": "archive/active/tier4_agent/"
    }
  },
  "retention_policy": "Permanent for Tier 1-2, as-useful for Tier 3-4",
  "last_audit": "2025-11-07T14:30:00Z"
}
```

---

## Directory Structure Assessment & Categorical Division Policy

### Automatic Assessment Trigger

**Rule**: When a directory contains approximately 12 or more files, it will be assessed for categorical division.

1. **Identify Categories**: Analyze the files in the directory for clear categorical classifications
2. **Determine Clarity**: Assess whether a clear categorical grouping exists (e.g., by type, function, tier, date range)
3. **Evaluate Impact**: For each potential division, determine whether separating files into multiple subdirectories would:
   - **Enhance** overall usability and efficiency, OR

### Decision Criteria

- Navigation time is reduced (users can locate needed files faster)
- Maintenance is simplified (related files grouped together)
- Future scalability is improved (room for growth within categories)
**Detract from Usability & Efficiency When**:

- Files are conceptually related despite surface differences
- Navigation adds unnecessary steps for common operations
- File count remains low after division (extra hierarchy not justified)
- Cross-category references are frequent (separation complicates relationships)
- Divisional boundaries are ambiguous or overlapping
- Single unified location serves the primary access pattern

### Implementation Authority

- **User Decision**: Final authority on categorical division decisions
- **Agent Assessment**: Can recommend division based on criteria above
- **Policy Alignment**: All divisions must maintain SECURITY > EFFICIENCY > MINIMALISM compliance

### Documentation Requirement

When a directory undergoes categorical division:

1. Create subdirectories with clear, descriptive names
2. Update documentation explaining the new structure
3. Maintain cross-references if necessary for commonly accessed relationships
4. Update any indices or navigation aids
5. Log the change in archive metadata (if applicable)

---

## Git Tracking Strategy

### Archive Metadata

Each archived document includes `metadata.json`:

```json
{
  "classification_tier": 1,
  "document_name": "Infrastructure Compliance Report",
  "document_id": "compliance_2025_q4",
  "type": "compliance_report",
  "created_date": "2025-11-07T00:00:00Z",
  "last_modified_date": "2025-11-07T00:00:00Z",
  "status": "active",
  "retention_policy": "permanent",
  "versions_tracked": true,
  "branding": "minimal",
  "encryption": false,
  "parent_location": "[repo_path]/docs/reports/compliance_2025_q4.md",
  "archive_location": "archive/active/tier1_critical/compliance_report/compliance_2025_q4/",
  "audit_trail": [
    {
      "timestamp": "2025-11-07T00:00:00Z",
      "action": "created",
      "actor": "user"
    }
  ]
}
```

---

## Git Tracking Strategy

### Git-Tracked Locations

**Tier 0**: Not git-tracked (encrypted separately)  
**Tier 1**: Git-tracked (active copies only); archive marked but not tracked  
**Tier 2**: Git-tracked (active copies); archive marked but not tracked  
**Tier 3**: Optional; typically not tracked  
**Tier 4a**: Git-tracked (critical procedures)  
**Tier 4b**: Git-tracked (important procedures)  
**Tier 4c**: Not tracked (temporary)

### .gitignore Pattern

```
# Archive directories (not tracked)
archive/
archive_backup/
!archive/metadata/

# Temporary agent documentation
docs/agent_temp/
```

---

## Backup Strategy

### Active Backup Location

**Path**: `{repository_parent_directory}/archive_backup/`

**Includes**:

- All active Tier 0 (encrypted)
- All active Tier 1 documents and versions
- All active Tier 2 documents
- Archive metadata and indices

**Excludes**:

- Tier 3 temporary documents
- Tier 4c temporary agent notes
- Inactive archive copies

**Frequency**: Daily or after major document changes

**Verification**: SHA256 checksums maintained in `metadata/backup_manifest.json`

### Inactive Archive Location

**Path**: `{repository}/archive/inactive/`

**Contains**:

- Deleted Tier 1 critical documents (all versions)
- Deleted Tier 2 informative documents
- Superseded Tier 4a core procedures

**Status**: Marked as "inactive"; not referenced by active operations

**Retention**: Kept indefinitely for historical reference and compliance

---

## Lifecycle Workflow Examples

### Tier 0 Secret Creation & Deletion

```
1. User: "Create encrypted secret for API token"
2. Agent: Creates secret, stores encrypted
3. Agent: Confirms creation to user
4. [Later] User: "Delete API token secret"
5. Agent: "Verify deletion - this will purge all copies: [details]"
6. User: Confirms deletion
7. Agent: Deletes from repo, clears caches, purges backups
8. Agent: Confirms deletion complete
```

### Tier 1 Critical Document Versioning

```
1. User: "Create compliance report"
2. Agent: Creates v1/compliance_report_2025q4.md
3. Document active in repo/docs/reports/
4. Agent: Archive scheduled: archive/active/tier1_critical/compliance/v1/
5. [Later] Agent: Updates for v2 (minor changes)
6. Agent: Creates v2/ version directory
7. Both v1/ and v2/ retained in archive
8. [Future] User: "Delete this report"
9. Agent: Removes from main repo
10. Agent: Marks archive/inactive/tier1_critical/compliance/
11. All historical versions preserved in inactive archive
```

### Tier 2 Informative Documentation Update

```
1. Agent: Creates setup_guide.md (Tier 2)
2. Document available in repo with branding
3. Agent: Makes content updates (feature additions)
4. Updates are committed directly
5. [Later] Agent: "Major restructure of setup guide"
6. Agent: "User, major changes needed: [summary]. Approve?"
7. User: Approves
8. Agent: Implements major restructure
9. Changes committed and tracked
```

### Tier 3 Job Report Consolidation

```
1. Agent: Runs test job in stages
2. Creates test_job_stage1.md, test_job_stage2.md, test_job_stage3.md
3. Agent: Consolidates into test_job_summary.md
4. Agent assesses: "Is summary useful for future reference?"
5. If Yes: Archive summary in archive/tier3_temporary/
6. If No: Delete summary; delete stage files
7. If Uncertain: Archive; review in 30 days
```

### Tier 4a Core Procedure Modification

```
1. Agent: Identifies issue in POLICY.md (Tier 4a)
2. Agent: "Suggests improvement: [proposal]"
3. User: Reviews and approves
4. Agent: Implements change; commits with rationale
5. Change tracked in git history
6. Backup updated to reflect new version
```

---

## Decision Matrix: Document Classification

| Characteristic | Tier 0 | Tier 1 | Tier 2 | Tier 3 | Tier 4 |
|---|---|---|---|---|---|
| **Purpose** | Secret | Infrastructure | Information | Temporary | Agent |
| **Agent Create** | User only | Instructed/procedural | Always | Always | Always |
| **Agent Modify** | User only | Major requires verification | Minor free | Always | Always |
| **Agent Delete** | User + verification | User + explicit | User approval | Always | User verification* |
| **Version Tracking** | N/A | All tracked | Latest | Summary | By level |
| **Git Tracked** | No | Yes | Yes | Optional | 4a/4b yes, 4c no |
| **Archival** | Encrypted, separate | All versions | Latest | Optional | By level |
| **Branding** | None | Minimal | Moderate | None | By level |
| **Retention** | Permanent | Permanent | As useful | As useful | By level |

*Tier 4: User verification required only for deletion of documents created by user request; agent-initiated docs can be freely deleted by agent

---

## Implementation Checklist

### For New Documents

- [ ] Classify document according to Tier system
- [ ] Create appropriate directory structure if archive needed
- [ ] Add metadata.json with classification details
- [ ] Apply branding if required by tier
- [ ] Configure git tracking per tier
- [ ] Schedule backup if applicable
- [ ] Document retention policy
- [ ] Create audit trail entry

### For Existing Documents

- [ ] Audit current documents
- [ ] Classify each document
- [ ] Reorganize into archive structure
- [ ] Create metadata for each archived item
- [ ] Update .gitignore as needed
- [ ] Verify backup locations
- [ ] Communicate changes to all users

### For Deletion

- [ ] Verify document classification
- [ ] Follow deletion procedures for tier
- [ ] Get user verification if required
- [ ] Archive inactive copy if tier requires
- [ ] Update metadata and audit logs
- [ ] Clear from caches and backups (Tier 0)
- [ ] Confirm deletion complete

---

## Policy Compliance & Governance

**Authority**: This policy is a T4a - Permanent Directive governing document lifecycle and agent authority

**Oversight**: Document classification decisions subject to SECURITY > EFFICIENCY > MINIMALISM

**Review Cycle**: Quarterly (audit classification scheme; adjust as needed)

**Violations**: Classification errors reported in security audit

**Override Authority**: Explicit user instruction can override any tier classification requirement

---

## Version History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | November 7, 2025 | CodeSentinel Policy Framework | Initial comprehensive classification system |

**Next Review**: December 7, 2025

---

## Permanent Global Policy Amendment: Duplication Mitigation

**Effective Immediately:**

- All document tiers and lifecycle management procedures must enforce intelligent duplication mitigation.
- Duplicates are to be merged or deleted if and only if:
  - Data preservation is guaranteed (no unique content lost).
  - Minimalism is enforced (no unnecessary files or redundancy).
- Intelligent analysis (automated or manual) must be performed before any merger or deletion.
- Legacy or ambiguous versions are archived if needed, but redundant files are removed to maintain a clean, minimal, and secure codebase.
- This amendment is permanent and global, superseding previous non-destructive-only rules where duplication is present.

**Integration:**

- Applies to all document tiers (0-4), classification, archival, and deletion procedures.
- All automation, audits, and agent-driven workflows must implement this policy.
- The system remains whole, secure, and improved, with minimalism as a core principle.
