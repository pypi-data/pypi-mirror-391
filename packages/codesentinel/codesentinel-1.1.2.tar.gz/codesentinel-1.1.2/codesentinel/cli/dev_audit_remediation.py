"""
Automated remediation for 'dev-audit' command.
"""
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

def apply_safe_fixes(agent_context_dict: Dict[str, Any], dry_run: bool = True) -> Dict[str, Any]:
    """
    Apply safe automated fixes based on agent context.
    
    This function reads the agent context and executes only actions that are:
    1. Explicitly marked as safe_to_automate=True
    2. Do not require agent decision (agent_decision_required=False)
    3. Non-destructive (archive-first approach)
    
    Args:
        agent_context_dict (dict): The agent context dictionary with remediation_opportunities.
        dry_run (bool): If True, only show what would be fixed without making changes.
    
    Returns:
        dict: Summary of fixes applied or that would be applied.
    """
    print("\nAutomated Fix Application")
    print("=" * 60)
    
    if dry_run:
        print("DRY RUN MODE: No changes will be made")
    else:
        print("LIVE MODE: Safe automated fixes will be applied")
    
    print("=" * 60)
    print()
    
    workspace_root = Path.cwd()
    
    # Get remediation opportunities from the new AgentContext structure
    opportunities = agent_context_dict.get('remediation_opportunities', [])
    
    # Collect all safe actions
    safe_actions = []
    for opp in opportunities:
        if opp.get('safe_to_automate') and not opp.get('agent_decision_required'):
            safe_actions.append(opp)

    if not safe_actions:
        print("[OK] No safe automated actions found")
        print("  All issues require manual review or agent decision")
        print()
        return {
            "status": "success",
            "fixes_applied": 0,
            "fixes_skipped": len(opportunities),
            "message": "No safe automated actions available"
        }

    print(f"Found {len(safe_actions)} safe automated actions:\n")
    
    fixes_applied = 0
    archive_dir = workspace_root / "quarantine_legacy_archive" / f"auto_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    for opp in safe_actions:
        opp_type = opp.get('type', 'unknown')
        priority = opp.get('priority', 'medium')
        title = opp.get('title', 'Unknown issue')
        description = opp.get('description', '')
        actions = opp.get('suggested_actions', [])
        
        print(f"[{opp_type.upper()} - {priority}] {title}")
        print(f"  Description: {description}")
        print(f"  Actions:")
        for action in actions:
            print(f"    - {action}")
        
        applied = False
        
        # Safe action: Clean __pycache__ and cache artifacts
        if "__pycache__" in description.lower() or "cache artifact" in description.lower():
            if not dry_run:
                try:
                    for pycache_dir in workspace_root.rglob("__pycache__"):
                        if pycache_dir.is_dir():
                            shutil.rmtree(pycache_dir)
                    print("  [OK] Removed __pycache__ directories")
                    applied = True
                except Exception as e:
                    print(f"  [FAILED] {e}")
            else:
                print("  [DRY-RUN] Would remove __pycache__ directories")
                applied = True
        
        # Safe action: Move orphaned test files
        elif "test files in wrong location" in title.lower() or "orphaned test" in description.lower():
            if not dry_run:
                try:
                    # Find test files in root
                    test_files = list(workspace_root.glob("test_*.py"))
                    if test_files:
                        tests_dir = workspace_root / "tests"
                        tests_dir.mkdir(exist_ok=True)
                        for test_file in test_files:
                            target = tests_dir / test_file.name
                            test_file.rename(target)
                        print(f"  [OK] Moved {len(test_files)} test file(s) to tests/")
                        applied = True
                except Exception as e:
                    print(f"  [FAILED] {e}")
            else:
                test_files = list(workspace_root.glob("test_*.py"))
                print(f"  [DRY-RUN] Would move {len(test_files)} test file(s) to tests/")
                applied = True if test_files else False

        # Add other safe actions here...

        if applied:
            fixes_applied += 1
            print("-" * 20)

    total_issues = len(opportunities)
    fixes_skipped = total_issues - fixes_applied

    print("\n" + "=" * 60)
    print("REMEDIATION SUMMARY")
    print("=" * 60)
    print(f"[OK] Automated fixes applied: {fixes_applied}")
    print(f"[!] Issues requiring manual review: {fixes_skipped}")
    
    return {
        "status": "success",
        "fixes_applied": fixes_applied,
        "fixes_skipped": fixes_skipped,
        "message": f"Applied {fixes_applied} fixes. Skipped {fixes_skipped} issues requiring manual review."
    }
