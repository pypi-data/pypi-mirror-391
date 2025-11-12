# Tool & Environment Management Policy

**Last Updated**: 2025-11-11  
**Policy Tier**: Efficiency (SEAM Protection™)  
**Status**: Active - Mandatory for all developers and agents

## 1. Overview

This policy prevents performance degradation, increased operational costs, and unpredictable behavior in AI agents caused by tool and environment misconfiguration. The primary cause of such issues is the loading of duplicate or unnecessary tools, which increases the agent's cognitive load and token usage.

**Core Principle**: A project's required tools and environment should be explicitly defined and version-controlled within the project itself.

## 2. The Problem: Tool Proliferation

When Visual Studio Code is configured with multiple Model Context Protocol (MCP) servers (e.g., `pylance`, `pylance2`, `gitkraken`, `gitkraken2`), the AI agent may be presented with a redundant and excessive set of tools.

- **Performance Impact**: The agent must evaluate every enabled tool for every request, causing delays.
- **Cost Impact**: Larger context windows are required to manage the toolset, increasing API token costs.
- **Accuracy Impact**: The agent may choose a suboptimal or incorrect tool when multiple similar options are available.
- **Example**: A warning of "151 tools enabled" indicates severe tool proliferation. A healthy number for this project is **40-60**.

## 3. Configuration Hierarchy

Configuration settings are applied in the following order of precedence (highest wins):

1. **Workspace Settings (`.vscode/settings.json`)**: **HIGHEST PRIORITY**. These settings are project-specific, version-controlled, and shared with all contributors. **This is the required location for project tool configuration.**
2. **User Settings (`settings.json`)**: Global settings that apply to all of the user's projects. These should be used for personal preferences, not project-specific toolsets.
3. **Default Settings**: The default VS Code and extension settings.

## 4. Workspace-First Policy

**MANDATORY**: All project-specific tool configurations **MUST** be defined in the `.vscode/settings.json` file.

### Benefits

- **Consistency**: Every developer and agent uses the same toolset.
- **Version Control**: Changes to the toolset are tracked in Git.
- **Isolation**: Prevents a user's global settings from interfering with the project.
- **Automation**: Allows for automated auditing and enforcement.

### Example: `.vscode/settings.json`

```json
{
  "github.copilot.chat.mcp.enabled": true,
  
  // Define the exact MCP servers needed for this project
  "mcp.servers": {
    "pylance": { "enabled": true },
    "github-pull-request": { "enabled": true },
    
    // Explicitly disable servers not needed for this project
    "gitkraken": { "enabled": false },
    "container-management": { "enabled": false }
  },

  // Ensure no duplicate servers (e.g., pylance2, gitkraken2) are listed
}
```

## 5. Auditing and Enforcement

To ensure compliance, an automated audit has been integrated into CodeSentinel.

### Automated Tool Audit

The `dev-audit` command now includes a tool audit that:

1. Reads both User and Workspace `settings.json`.
2. Detects duplicate MCP server definitions.
3. Identifies servers enabled in User settings that are disabled or not defined in Workspace settings.
4. Provides actionable recommendations to move configurations to the workspace file.

**Usage**:

```bash
# Run a comprehensive development audit, including tool configuration
codesentinel dev-audit --tools

# Quick alias
codesentinel !!!! --tools
```

## 6. Developer Workflow

1. **Initial Setup**: When cloning the repository, immediately run the tool audit.

    ```bash
    codesentinel dev-audit --tools
    ```

2. **Apply Recommendations**: Modify your global User `settings.json` as recommended by the audit to remove project-specific overrides.
3. **Verification**: Run the audit again to confirm compliance. The audit should pass with no warnings.
4. **Ongoing**: If you install a new VS Code extension that provides an MCP server, run the audit to ensure it is configured correctly in `.vscode/settings.json`.

## 7. Governance

- **Violation**: A failed `dev-audit --tools` check is considered a policy violation.
- **Pre-Commit Hook (Recommended)**: Developers should add this audit to a local pre-commit hook to prevent committing code from a misconfigured environment.
- **CI/CD**: Future CI/CD pipelines may include this check as a blocking step.
