"""
Utilities for the 'dev-audit' command.

This module contains the logic for running development audits, including
interactive sessions, generating context for AI agent remediation, and
auditing the development environment itself.
"""
import json
import os
import platform
import sys
from pathlib import Path

def get_user_settings_path():
    """Gets the path to the user's VS Code settings.json."""
    system = platform.system()
    if system == "Windows":
        # Correct path for Windows non-portable mode
        return Path(os.getenv("APPDATA")) / "Code" / "User" / "settings.json"
    elif system == "Darwin":  # macOS
        return Path.home() / "Library" / "Application Support" / "Code" / "User" / "settings.json"
    else:  # Linux
        return Path.home() / ".config" / "Code" / "User" / "settings.json"

def read_settings_json(path):
    """Reads and parses a settings.json file, returning a dictionary."""
    if not path.exists():
        return {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            # A simple way to handle comments is to filter them out before parsing
            lines = f.readlines()
            valid_json_lines = [line for line in lines if not line.strip().startswith('//')]
            return json.loads(''.join(valid_json_lines))
    except (json.JSONDecodeError, FileNotFoundError):
        # Return empty dict if file is malformed or not found
        return {}

def configure_workspace_tools():
    """
    Interactive configuration wizard for workspace tool settings.
    Creates or updates .vscode/settings.json with MCP server configuration.
    """
    print("Workspace Tool Configuration Wizard")
    print("=" * 60)
    
    workspace_root = Path.cwd()
    vscode_dir = workspace_root / ".vscode"
    settings_path = vscode_dir / "settings.json"
    
    # Ensure .vscode directory exists
    vscode_dir.mkdir(exist_ok=True)
    
    # Read existing settings if they exist
    existing_settings = read_settings_json(settings_path) if settings_path.exists() else {}
    
    print(f"\nWorkspace: {workspace_root.name}")
    print(f"Settings file: {settings_path}")
    print()
    
    # Check user settings to see what's available
    user_settings_path = get_user_settings_path()
    user_settings = read_settings_json(user_settings_path)
    user_mcp = user_settings.get("mcp.servers", {})
    
    if user_mcp:
        print(f"Found {len(user_mcp)} MCP servers in your User settings:")
        for server in user_mcp.keys():
            print(f"  - {server}")
        print()
    
    # Recommended minimal configuration for CodeSentinel
    print("Recommended MCP servers for CodeSentinel development:")
    print("  - pylance (Python language server)")
    print("  - github-pull-request (Git/GitHub integration)")
    print()
    
    response = input("Create recommended configuration? (y/N): ").strip().lower()
    
    if response == 'y':
        # Create minimal configuration
        mcp_config = existing_settings.get("mcp.servers", {})
        
        # Add recommended servers
        mcp_config["pylance"] = {"enabled": True}
        mcp_config["github-pull-request"] = {"enabled": True}
        
        # Disable common duplicates if they exist in user settings
        duplicates_to_disable = ["pylance2", "pylance3", "gitkraken", "gitkraken2", "gitkraken3"]
        for dup in duplicates_to_disable:
            if dup in user_mcp:
                mcp_config[dup] = {"enabled": False}
        
        existing_settings["mcp.servers"] = mcp_config
        existing_settings["github.copilot.chat.mcp.enabled"] = True
        
        # Write settings
        import json
        with open(settings_path, 'w', encoding='utf-8') as f:
            json.dump(existing_settings, f, indent=2)
        
        print()
        print("✓ Workspace configuration created successfully!")
        print(f"✓ File: {settings_path.relative_to(workspace_root)}")
        print()
        print("Configuration applied:")
        print("  - Enabled: pylance, github-pull-request")
        if any(dup in user_mcp for dup in duplicates_to_disable):
            print(f"  - Disabled duplicates: {', '.join(d for d in duplicates_to_disable if d in user_mcp)}")
        print()
        print("Run 'codesentinel dev-audit --tools' to verify the configuration.")
    else:
        print("Configuration wizard cancelled.")
    
    print("=" * 60)

def run_tool_audit():
    """
    Audits the VS Code tool configuration against the workspace-first policy
    defined in docs/TOOL_MANAGEMENT_POLICY.md.
    """
    print("Running Tool & Environment Audit...")
    print("-" * 35)

    user_settings_path = get_user_settings_path()
    workspace_settings_path = Path.cwd() / ".vscode" / "settings.json"

    if not workspace_settings_path.exists():
        print("ERROR: Workspace configuration file '.vscode/settings.json' not found.")
        print("Please create it according to 'docs/TOOL_MANAGEMENT_POLICY.md'.")
        print("-" * 35)
        return

    user_settings = read_settings_json(user_settings_path)
    workspace_settings = read_settings_json(workspace_settings_path)

    user_mcp = user_settings.get("mcp.servers", {})
    workspace_mcp = workspace_settings.get("mcp.servers", {})

    if not workspace_mcp:
        print("WARNING: No 'mcp.servers' configuration found in workspace '.vscode/settings.json'.")
        print("         This project should have an explicit tool configuration.")
        if user_mcp:
            print("         User settings contain MCP configurations that should be moved to the workspace.")
        print("-" * 35)
        return

    issues_found = False
    print("Auditing MCP server configurations...")

    for server, user_config in user_mcp.items():
        user_enabled = user_config.get("enabled", False)
        if not user_enabled:
            continue # Only check servers explicitly enabled in user settings

        workspace_config = workspace_mcp.get(server)
        if workspace_config is None:
            issues_found = True
            print(f"\n[!] Policy Violation: Server '{server}' is enabled in User settings but not defined in Workspace settings.")
            print(f"    - Recommendation: Add '\"{server}\": {{ \"enabled\": true/false }}' to '.vscode/settings.json'.")
        elif workspace_config.get("enabled", False) != user_enabled and workspace_config.get("enabled") is not None:
            issues_found = True
            workspace_enabled_status = workspace_config.get("enabled")
            print(f"\n[!] Policy Conflict: Server '{server}' enabled status differs between User and Workspace.")
            print(f"    - User setting:      enabled: {user_enabled}")
            print(f"    - Workspace setting: enabled: {workspace_enabled_status}")
            print(f"    - Recommendation: Remove the '{server}' configuration from your global User settings to allow the workspace setting to take precedence.")

    total_enabled_servers = sum(1 for s in workspace_mcp.values() if s.get("enabled"))
    print(f"\nWorkspace enables {total_enabled_servers} MCP servers.")
    if total_enabled_servers > 80:
        print(f"[!] Warning: High number of enabled tools ({total_enabled_servers}). Review for redundancy.")
        issues_found = True

    print("-" * 35)
    if not issues_found:
        print("✓ Tool configuration audit passed. No issues found.")
    else:
        print("✗ Tool configuration audit failed. Please address the issues above.")
        print("  Refer to 'docs/TOOL_MANAGEMENT_POLICY.md' for guidance.")

def perform_dev_audit(args, codesentinel):
    """
    Handles the dev-audit command logic.

    Args:
        args: The parsed command-line arguments.
        codesentinel: An instance of the CodeSentinel core class.
    """
    # Check for tools configuration wizard
    if getattr(args, 'configure', False):
        configure_workspace_tools()
        return
    
    # Check for tool audit
    if getattr(args, 'tools', False):
        run_tool_audit()
        return

    interactive = not getattr(args, 'silent', False)
    agent_mode = getattr(args, 'agent', False)
    export_path = getattr(args, 'export', None)
    focus_area = getattr(args, 'focus', None)

    if agent_mode:
        # Export comprehensive context for AI agent
        print("Generating audit context for AI agent...")
        if focus_area:
            print(f"Focus area: {focus_area}")
        agent_context = codesentinel.dev_audit.get_agent_context()

        # ORACL™ Integration: Enrich agent context with historical intelligence
        try:
            from codesentinel.utils.archive_decision_provider import get_decision_context_provider
            
            provider = get_decision_context_provider()
            
            # Query ORACL™ for relevant historical patterns
            # Focus on policy violations (most common in dev audits)
            oracl_context = provider.get_decision_context(
                decision_type="policy_violation_handling",
                current_state={
                    "context": "dev_audit",
                    "severity": "medium",
                    "source": "automated_audit"
                },
                search_radius_days=90
            )
            
            if oracl_context and oracl_context.confidence_score >= 0.5:
                # Add ORACL™ insights to agent context
                agent_context['oracl_intelligence'] = {
                    'available': True,
                    'confidence': oracl_context.confidence_score,
                    'recommendations': oracl_context.recommended_actions,
                    'success_rate': oracl_context.success_rate,
                    'similar_cases': len(oracl_context.similar_past_cases),
                    'guidance': f"ORACL has {len(oracl_context.similar_past_cases)} similar cases with {oracl_context.success_rate:.0%} success rate (confidence: {oracl_context.confidence_score:.0%})"
                }
                print(f"[OK] ORACL intelligence: {len(oracl_context.similar_past_cases)} similar cases found (confidence: {oracl_context.confidence_score:.0%})")
            else:
                agent_context['oracl_intelligence'] = {'available': False, 'reason': 'insufficient_historical_data'}
        except Exception as e:
            # ORACL™ optional - fail gracefully
            agent_context['oracl_intelligence'] = {'available': False, 'reason': str(e)}

        # Add focus area to agent context if specified
        if focus_area:
            agent_context['focus_area'] = focus_area
            agent_context['agent_guidance'] = f"""
FOCUSED AUDIT ANALYSIS

Focus Area: {focus_area}

You have been requested to perform a targeted analysis on: "{focus_area}"

While the full audit context is provided below, you should:
1. Prioritize issues and opportunities related to {focus_area}
2. Consider how changes in this area affect the broader system
3. Ensure all remediation respects SEAM Protection (Security, Efficiency, And Minimalism)
4. Maintain non-destructive, feature-preserving principles

{agent_context.get('agent_guidance', '')}
"""
        if export_path:
            with open(export_path, 'w') as f:
                json.dump(agent_context, f, indent=2)
            print(f"Agent context exported to: {export_path}")
        else:
            # Print guidance for agent
            print("\\n" + "=" * 60)
            print(agent_context['agent_guidance'])
            print("\\n" + "=" * 60)
            print("\\nAudit Results Summary:")
            print(json.dumps(agent_context['remediation_context']['summary'], indent=2))

            print("\\n" + "=" * 60)
            print("AGENT REMEDIATION MODE")
            if focus_area:
                print(f"FOCUS: {focus_area}")
            print("=" * 60)
            print("\\nThis audit has detected issues that require intelligent remediation.")
            print("An AI agent (GitHub Copilot) can now analyze these findings and build")
            print("a remediation pipeline while respecting all persistent policies.\\n")

            if focus_area:
                print(f"\\n Analysis will prioritize: {focus_area}")
                print("   (while maintaining awareness of system-wide impact)\\n")

            # Output structured data for agent to consume
            print("\\n@agent Here is the comprehensive audit context:")
            print(json.dumps(agent_context, indent=2))

            print("\\n\\nPlease analyze the audit findings and propose a remediation plan.")
            if focus_area:
                print(f"Focus your analysis on: {focus_area}")
            print("Remember: All actions must be non-destructive and preserve features.")
        return

    # Non-agent mode with focus
    if focus_area:
        print(f"\\n Focus Area: {focus_area}")
        print("Note: Focus parameter is most effective with --agent mode for Copilot integration.\\n")

    results = codesentinel.run_dev_audit(interactive=interactive)
    if interactive:
        # Check if there are issues and offer agent mode
        total_issues = results.get('summary', {}).get('total_issues', 0)
        if total_issues > 0:
            print("\\n" + "=" * 60)
            print(f"🤖 AGENT REMEDIATION AVAILABLE")
            print("=" * 60)
            print(f"\\nThe audit detected {total_issues} issues.")
            print("\\nIf you have GitHub Copilot integrated, you can run:")
            print("  codesentinel !!!! --agent")
            if focus_area:
                print(f"  codesentinel !!!! {focus_area} --agent  (focused analysis)")
            else:
                print("  codesentinel !!!! scheduler --agent       (focus on specific area)")
            print("\\nThis will provide comprehensive context for the AI agent to")
            print("intelligently build a remediation pipeline while maintaining")
            print("SEAM Protection (Security, Efficiency, And Minimalism).")

        print("\\nInteractive dev audit completed.")
        print("A brief audit is running in the background; results will arrive via alerts.")
    else:
        print(json.dumps(results.get('summary', {}), indent=2))
    return

def apply_automated_fixes(codesentinel, dry_run=True):
    """
    Apply safe automated fixes based on audit findings.
    
    This function reads the agent-readable audit report and executes
    only actions that are:
    1. Explicitly marked as safe-to-automate
    2. Do not require agent decision (agent_decision_required=False)
    3. Priority is 'low' or 'medium' (not 'critical' which may need review)
    4. Non-destructive (archive-first approach)
    
    Args:
        codesentinel: An instance of the CodeSentinel core class
        dry_run (bool): If True, only show what would be fixed without making changes
    
    Returns:
        dict: Summary of fixes applied or that would be applied
    """
    import shutil
    from datetime import datetime
    
    print("\\nAutomated Fix Application")
    print("=" * 60)
    
    if dry_run:
        print("DRY RUN MODE: No changes will be made")
    else:
        print("LIVE MODE: Safe automated fixes will be applied")
    
    print("=" * 60)
    print()
    
    # Get agent context from audit
    try:
        agent_context = codesentinel.dev_audit.get_agent_context()
    except Exception as e:
        print(f"❌ Failed to get agent context: {e}")
        return {"status": "error", "message": str(e)}
    
    remediation = agent_context.get('remediation_context', {})
    workspace_root = Path.cwd()
    
    # Collect all safe actions
    safe_actions = []
    
    # Process security issues (only very safe ones)
    for hint in remediation.get('security_issues', []):
        if hint.get('agent_decision_required', True):
            continue  # Skip if requires decision
        if hint.get('priority') == 'critical':
            continue  # Critical security issues need manual review
        safe_actions.append(('security', hint))
    
    # Process efficiency issues
    for hint in remediation.get('efficiency_issues', []):
        if hint.get('agent_decision_required', True):
            continue
        safe_actions.append(('efficiency', hint))
    
    # Process minimalism issues (most safe automated actions here)
    for hint in remediation.get('minimalism_issues', []):
        if hint.get('agent_decision_required', True):
            continue
        safe_actions.append(('minimalism', hint))
    
    if not safe_actions:
        print("✓ No safe automated actions found")
        print("  All issues require manual review or agent decision")
        print()
        return {"status": "success", "fixes_applied": 0, "message": "No safe automated actions available"}
    
    print(f"Found {len(safe_actions)} safe automated actions:\\n")
    
    fixes_applied = 0
    fixes_skipped = 0
    archive_dir = workspace_root / "quarantine_legacy_archive" / f"auto_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    for category, hint in safe_actions:
        issue = hint.get('issue', 'Unknown issue')
        violation = hint.get('violation', '')
        actions = hint.get('suggested_actions', [])
        priority = hint.get('priority', 'medium')
        
        print(f"[{category.upper()} - {priority}] {issue}")
        print(f"  Violation: {violation}")
        print(f"  Actions:")
        for action in actions:
            print(f"    - {action}")
        
        # Determine what to do based on issue type
        applied = False
        
        # Safe action: Clean __pycache__ and cache artifacts
        if "pycache" in violation.lower() or "cache artifact" in violation.lower():
            if not dry_run:
                try:
                    # Find and remove __pycache__ directories
                    for pycache_dir in workspace_root.rglob("__pycache__"):
                        if pycache_dir.is_dir():
                            shutil.rmtree(pycache_dir)
                    print("  ✓ Removed __pycache__ directories")
                    applied = True
                except Exception as e:
                    print(f"  ❌ Failed: {e}")
            else:
                print("  [DRY-RUN] Would remove __pycache__ directories")
                applied = True
        
        # Safe action: Add to .gitignore
        elif "gitignore" in " ".join(actions).lower():
            gitignore_path = workspace_root / ".gitignore"
            patterns_to_add = []
            
            if "__pycache__" in violation:
                patterns_to_add.append("__pycache__/")
            if ".pyc" in violation or ".pyo" in violation:
                patterns_to_add.extend(["*.pyc", "*.pyo"])
            if ".pytest_cache" in violation:
                patterns_to_add.append(".pytest_cache/")
            
            if patterns_to_add and not dry_run:
                try:
                    existing = gitignore_path.read_text() if gitignore_path.exists() else ""
                    new_entries = [p for p in patterns_to_add if p not in existing]
                    
                    if new_entries:
                        with open(gitignore_path, 'a', encoding='utf-8') as f:
                            f.write("\\n# Auto-added by dev-audit --fix\\n")
                            for pattern in new_entries:
                                f.write(f"{pattern}\\n")
                        print(f"  ✓ Added {len(new_entries)} patterns to .gitignore")
                        applied = True
                    else:
                        print("  ✓ Patterns already in .gitignore")
                        applied = True
                except Exception as e:
                    print(f"  ❌ Failed: {e}")
            elif patterns_to_add:
                print(f"  [DRY-RUN] Would add {len(patterns_to_add)} patterns to .gitignore")
                applied = True
        
        # Safe action: Archive orphaned test files
        elif "orphaned test file" in violation.lower():
            # This requires agent decision to identify which files
            print("  ⚠  Orphaned test files require manual review")
            fixes_skipped += 1
        
        # Other actions require review
        else:
            print("  ⚠  This action requires manual review or agent decision")
            fixes_skipped += 1
        
        if applied:
            fixes_applied += 1
        
        print()
    
    print("=" * 60)
    print(f"Summary: {fixes_applied} fixes applied, {fixes_skipped} skipped")
    if dry_run:
        print("Run with --fix (without --agent first showing context) to apply changes")
    print("=" * 60)
    
    return {
        "status": "success",
        "fixes_applied": fixes_applied,
        "fixes_skipped": fixes_skipped,
        "dry_run": dry_run
    }

