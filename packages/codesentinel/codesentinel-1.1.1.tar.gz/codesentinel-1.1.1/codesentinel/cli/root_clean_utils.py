"""
Root Directory Cleanup Utilities
=================================

Enhanced interactive cleanup for root directory policy compliance.
Provides intelligent file assessment and user-friendly interactive remediation.

Following SEAM Protection™: Security, Efficiency, And Minimalism
"""

from pathlib import Path
from typing import Dict, List, Tuple
import shutil
from datetime import datetime


def suggest_action_for_file(item: Path) -> Tuple[str, str, str]:
    """
    Intelligently suggest action for unauthorized file.
    
    Uses ORACL (historical intelligence) when available for enhanced accuracy.
    
    Returns:
        (action, target_dir, reason)
        action: 'archive', 'move', or 'review'
        target_dir: suggested destination directory
        reason: human-readable explanation
    """
    from codesentinel.utils.root_policy import FILE_MAPPINGS
    
    name = item.name
    
    # ORACL Integration: Check for historical handling patterns
    oracl_recommendation = None
    try:
        from codesentinel.utils.archive_decision_provider import get_decision_context_provider
        
        provider = get_decision_context_provider()
        context = provider.get_decision_context(
            decision_type="policy_violation_handling",
            current_state={
                "violation_type": "unauthorized_file_in_root",
                "file_name": name,
                "file_pattern": f"*.{name.split('.')[-1]}" if '.' in name else "no_extension",
                "severity": "medium"
            },
            search_radius_days=30
        )
        
        # Use ORACL recommendation if high confidence
        if context and context.confidence_score >= 0.7:
            oracl_recommendation = (
                context.recommended_actions[0] if context.recommended_actions else None,
                context.confidence_score
            )
    except Exception:
        # ORACL optional - fail gracefully
        pass
    
    # Check if file matches known patterns for relocation
    for pattern, target_dir in FILE_MAPPINGS.items():
        if pattern in name.upper():
            reason = f"matches pattern '{pattern}'"
            if oracl_recommendation:
                reason += f" (ORACL: {oracl_recommendation[1]:.0%} confidence)"
            return 'move', target_dir, reason
    
    # Analyze by file extension
    if name.endswith('.md'):
        # Documentation files
        if any(x in name.upper() for x in ['SUMMARY', 'REPORT', 'ANALYSIS', 'AUDIT']):
            return 'move', 'docs/', 'appears to be documentation'
        elif any(x in name.upper() for x in ['INTEGRATION', 'IMPLEMENTATION']):
            return 'move', 'docs/architecture/', 'implementation documentation'
        else:
            return 'review', 'docs/', 'documentation file - needs review'
    
    elif name.endswith('.py'):
        # Python scripts
        if name.startswith('test_') or '_test' in name or name in ['diagnosis.py', 'check_end.py']:
            return 'archive', 'quarantine_legacy_archive/', 'temporary diagnostic script'
        elif any(x in name for x in ['analyze', 'fix', 'remove', 'root_cause']):
            return 'archive', 'quarantine_legacy_archive/', 'temporary utility script'
        else:
            return 'review', 'scripts/', 'Python script - verify purpose'
    
    elif name.endswith('.json'):
        return 'review', 'tools/config/', 'configuration file - verify purpose'
    
    elif name.endswith('.txt') or name.endswith('.log'):
        return 'archive', 'quarantine_legacy_archive/', 'temporary file'
    
    else:
        return 'archive', 'quarantine_legacy_archive/', 'unauthorized file type'


def suggest_action_for_directory(item: Path) -> Tuple[str, str, str]:
    """
    Intelligently suggest action for unauthorized directory.
    
    Returns:
        (action, target_dir, reason)
    """
    name = item.name
    
    # Skip approved directories that might not be in policy yet
    if name in ['.venv', '.vscode', '.codesentinel', '.pytest_cache', '.agent_session']:
        return 'skip', '', 'approved directory'
    
    if name.startswith('.'):
        return 'archive', 'quarantine_legacy_archive/', 'unauthorized dot directory'
    elif name in ['agent_integration_requests', 'temp', 'tmp']:
        return 'archive', 'quarantine_legacy_archive/', 'temporary directory'
    else:
        return 'review', 'review required', 'unauthorized directory'


def display_violations_summary(policy_violations: List[Dict]) -> None:
    """Display categorized summary of policy violations."""
    # Categorize violations by suggested action
    to_archive = [v for v in policy_violations if v['action'] == 'archive']
    to_move = [v for v in policy_violations if v['action'] == 'move']
    to_review = [v for v in policy_violations if v['action'] == 'review']
    
    print(f"⚠️  Found {len(policy_violations)} policy violations:\n")
    
    # Display violations with icons
    for i, violation in enumerate(policy_violations, 1):
        action_icon = {'archive': '📦', 'move': '📁', 'review': '👁️'}.get(violation['action'], '❓')
        print(f"  {i}. {action_icon} [{violation['type'].upper()}] {violation['name']}")
        print(f"      Reason: {violation['reason']}")
        print(f"      Suggested: {violation['suggestion']}")
    
    # Display summary
    print(f"\n📊 Summary:")
    if to_archive:
        print(f"   📦 Archive: {len(to_archive)} items")
    if to_move:
        print(f"   📁 Move: {len(to_move)} items")
    if to_review:
        print(f"   👁️  Review: {len(to_review)} items")


def show_interactive_menu() -> str:
    """Show interactive menu and get user choice."""
    print("\n" + "="*60)
    print("Choose an action:")
    print("  1) Apply all suggested actions automatically")
    print("  2) Interactive mode (review each item)")
    print("  3) Archive all items (safe, non-destructive)")
    print("  4) Ignore all (cancel)")
    print("="*60)
    
    choice = input("\nYour choice (1-4): ").strip()
    return choice


def interactive_item_review(policy_violations: List[Dict]) -> List[Dict]:
    """
    Interactively review each violation and collect actions to take.
    
    Returns:
        List of violations with confirmed actions
    """
    print("\n🔄 Interactive Mode - Review each item:\n")
    actions_to_take = []
    
    for i, violation in enumerate(policy_violations, 1):
        print(f"\n[{i}/{len(policy_violations)}] {violation['name']}")
        print(f"  Type: {violation['type']}")
        print(f"  Reason: {violation['reason']}")
        print(f"  Suggested: {violation['suggestion']}")
        print("\n  Options:")
        print("    a) Apply suggestion")
        print("    m) Move to different location")
        print("    r) Archive to quarantine")
        print("    s) Skip this item")
        print("    q) Quit (cancel remaining)")
        
        item_choice = input("\n  Action (a/m/r/s/q): ").strip().lower()
        
        if item_choice == 'q':
            print("\n  Remaining items skipped.")
            break
        elif item_choice == 's':
            print(f"  ⏭️  Skipped: {violation['name']}")
            continue
        elif item_choice == 'a':
            actions_to_take.append(violation)
            print(f"  ✓ Will {violation['action']}: {violation['name']} → {violation['target']}")
        elif item_choice == 'm':
            custom_target = input("  Enter destination directory: ").strip()
            violation['target'] = custom_target if custom_target else violation['target']
            violation['action'] = 'move'
            actions_to_take.append(violation)
            print(f"  ✓ Will move: {violation['name']} → {violation['target']}")
        elif item_choice == 'r':
            violation['action'] = 'archive'
            violation['target'] = 'quarantine_legacy_archive/'
            actions_to_take.append(violation)
            print(f"  ✓ Will archive: {violation['name']}")
    
    return actions_to_take


def execute_cleanup_actions(
    policy_violations: List[Dict],
    workspace_root: Path,
    verbose: bool = False
) -> Tuple[int, int]:
    """
    Execute cleanup actions for policy violations.
    
    Reports outcomes to ORACL for continuous learning.
    
    Returns:
        (success_count, total_count)
    """
    archive_dir = workspace_root / 'quarantine_legacy_archive'
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    # ORACL Integration: Prepare to report outcomes
    oracl_provider = None
    try:
        from codesentinel.utils.archive_decision_provider import get_decision_context_provider
        oracl_provider = get_decision_context_provider()
    except Exception:
        pass  # ORACL optional
    
    success_count = 0
    print(f"\n🔄 Processing {len(policy_violations)} items...\n")
    
    for violation in policy_violations:
        outcome_success = False
        action_taken = violation['action']
        
        try:
            if violation['action'] == 'archive':
                target_path = archive_dir / violation['path'].name
                
                # Handle existing files with timestamp
                if target_path.exists():
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    base_name = violation['path'].name
                    if '.' in base_name:
                        name_parts = base_name.rsplit('.', 1)
                        target_path = archive_dir / f"{name_parts[0]}_{timestamp}.{name_parts[1]}"
                    else:
                        target_path = archive_dir / f"{base_name}_{timestamp}"
                
                shutil.move(str(violation['path']), str(target_path))
                print(f"  ✓ Archived: {violation['name']} → quarantine_legacy_archive/")
                success_count += 1
                outcome_success = True
            
            elif violation['action'] == 'move':
                target_dir = workspace_root / violation['target']
                target_dir.mkdir(parents=True, exist_ok=True)
                target_path = target_dir / violation['path'].name
                
                # Handle existing files
                if target_path.exists():
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    base_name = violation['path'].name
                    if '.' in base_name:
                        name_parts = base_name.rsplit('.', 1)
                        target_path = target_dir / f"{name_parts[0]}_{timestamp}.{name_parts[1]}"
                    else:
                        target_path = target_dir / f"{base_name}_{timestamp}"
                
                shutil.move(str(violation['path']), str(target_path))
                print(f"  ✓ Moved: {violation['name']} → {violation['target']}")
                success_count += 1
                outcome_success = True
            
            # Report success to ORACL
            if oracl_provider and outcome_success:
                oracl_provider.report_decision_outcome(
                    decision_type="policy_violation_handling",
                    state={
                        "violation_type": "unauthorized_file_in_root",
                        "file_name": violation['name'],
                        "severity": "medium"
                    },
                    action=action_taken,
                    outcome="success",
                    reason=f"{action_taken.capitalize()} completed successfully"
                )
        
        except Exception as e:
            print(f"  ✗ Failed: {violation['name']} - {e}")
            
            # Report failure to ORACL
            if oracl_provider:
                oracl_provider.report_decision_outcome(
                    decision_type="policy_violation_handling",
                    state={
                        "violation_type": "unauthorized_file_in_root",
                        "file_name": violation['name'],
                        "severity": "medium"
                    },
                    action=action_taken,
                    outcome="failure",
                    reason=str(e)
                )
    
    return success_count, len(policy_violations)


def scan_root_for_violations(workspace_root: Path, verbose: bool = False) -> List[Dict]:
    """
    Scan root directory for policy violations.
    
    Returns:
        List of violation dictionaries with action suggestions
    """
    from codesentinel.utils.root_policy import ALLOWED_ROOT_FILES, ALLOWED_ROOT_DIRS
    
    policy_violations = []
    
    # Check all items at root level
    for item in workspace_root.iterdir():
        # Skip git-related items
        if item.name in {'.git', '.gitignore'}:
            continue
        
        if item.is_dir():
            # Check if directory is allowed
            if item.name not in ALLOWED_ROOT_DIRS:
                action, target, reason = suggest_action_for_directory(item)
                
                # Skip approved directories
                if action == 'skip':
                    continue
                
                policy_violations.append({
                    'type': 'directory',
                    'path': item,
                    'name': item.name,
                    'reason': reason,
                    'target': target,
                    'action': action,
                    'suggestion': f"{action.title()} to {target}"
                })
        else:
            # Check if file is allowed
            if item.name not in ALLOWED_ROOT_FILES:
                action, target, reason = suggest_action_for_file(item)
                
                policy_violations.append({
                    'type': 'file',
                    'path': item,
                    'name': item.name,
                    'reason': reason,
                    'target': target,
                    'action': action,
                    'suggestion': f"{action.title()} to {target}"
                })
    
    return policy_violations
