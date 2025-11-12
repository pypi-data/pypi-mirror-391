# Quick Reference: Infrastructure as Code

**Satellite**: `infrastructure/AGENT_INSTRUCTIONS.md` | **Version**: 1.0 | **Last Updated**: 2025-11-07

---

## Authority Matrix (Condensed)

| Operation | Authority | Approval Required | Key |
| :--- | :--- | :--- | :--- |
| **Plan IaC Change** | L2 (Agent) | L3 (Senior Dev) | 🟢 |
| **Apply Staging IaC** | L2 (Agent) | L3 (Senior Dev) | 🟢 |
| **Apply Production IaC** | L3 (Senior Dev) | L4 (Architect) | 🟡 |
| **Manage Terraform State** | L3 (Senior Dev) | L4 (Architect) |  |
| **Run Security Scans** | L1 (Junior Dev) | None | 🟢 |

*🟢 = Standard Op | 🟡 = Requires Review |  = High-Risk*

---

## Quick Decision Tree

```mermaid
graph TD
    A[Start: IaC Task] --> B{What is the goal?};
    B --> C[Change Existing Infra];
    B --> D[Create Reusable Component];
    B --> E[Manual State Change];
    B --> F[Check for Vulnerabilities];

    C --> C1(Proc 1: Plan & Apply);
    C1 --> C2(1. Branch & Code);
    C2 --> C3(2. `terraform plan`);
    C3 --> C4(3. PR with Plan Output);
    C4 --> C5(4. Apply to Staging -> Prod);

    D --> D1(Proc 2: Create Module);
    D1 --> D2(1. Define Inputs/Outputs);
    D2 --> D3(2. Create Module Files);
    D3 --> D4(3. Add README & Example);
    D4 --> D5(4. Submit for Review);

    E --> E1(Proc 3: Manage State);
    E1 --> E2(1. **EMERGENCY ONLY**);
    E2 --> E3(2. Get Architect Approval);
    E3 --> E4(3. Backup State File);
    E4 --> E5(4. Use `terraform state` cmds);

    F --> F1(Proc 4: Security Scans);
    F1 --> F2(1. Auto-scan on PR);
    F2 --> F3(2. Triage Findings);
    F3 --> F4(3. Fix CRITICAL/HIGH);
    F4 --> F5(4. Ignore False Positives w/ Comment);
```

---

## Essential Procedures (Abbreviated)

### Proc 1: Plan and Apply Infrastructure Changes

1. **Branch & Code**: Create a feature branch. Modify the `.tf` files.
2. **Plan**: Run `terraform fmt`, `terraform validate`, and `terraform plan -out=tfplan`.
3. **Review**: Open a PR. **Include the full `plan` output in the description.** Get approval.
4. **Apply**: Merge to `main` to apply to **staging**. Get **Architect** approval for **production** apply.

### Proc 2: Create a Reusable IaC Module

1. **Contract**: Define inputs (`variables.tf`) and outputs (`outputs.tf`).
2. **Structure**: Create a new directory in `infrastructure/modules/`.
3. **Document**: Create a `README.md` with a description, variables, outputs, and a usage example. This is **mandatory**.
4. **Review**: Get Senior Dev approval for correctness, security, and reusability.

### Proc 3: Manage Terraform State

1. **EMERGENCY ONLY**: Do not use for standard workflows. Get **Architect** approval.
2. **Backup**: Manually back up the remote state file before any operation.
3. **Execute**: Use `terraform state` commands (`mv`, `rm`, `import`). Never edit the state file by hand.
4. **Verify**: Run `terraform plan` after to ensure the state is consistent. Document everything in an issue.

### Proc 4: Handle Infrastructure Security Scans

1. **CI Scans**: `tfsec` or `checkov` runs automatically on all PRs.
2. **Triage**: **CRITICAL/HIGH** findings **must be fixed before merge**. Medium/Low findings should be tracked as issues.
3. **Remediate**: Fix the issue in the IaC code and push the change.
4. **False Positives**: To ignore, add a comment `#tfsec:ignore:<code>` with a justification.

---

##  Emergency / Key Contacts

- **Incident Lead**: On-call DevOps Engineer
- **System Architect**: `@architect`
- **State Corruption**: Restore from backup. Contact Architect immediately.
- **Production Outage**: See `deployment/` Quick Reference Card for rollback.
- **Security Vulnerability Found**: `@security-team`
