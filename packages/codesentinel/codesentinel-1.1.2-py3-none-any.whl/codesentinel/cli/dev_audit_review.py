"""
Interactive review mode for dev-audit manual remediation items.
"""
from pathlib import Path
from typing import Any, Dict, List

from codesentinel.cli.agent_utils import AgentContext


def run_interactive_review(context: AgentContext) -> None:
    """
    Run interactive review session for manual-review issues.
    
    This provides a guided walkthrough of issues that require human decision-making,
    presenting context and suggested actions for each.
    
    Args:
        context: AgentContext containing remediation opportunities
    """
    print("\n" + "=" * 70)
    print("INTERACTIVE REVIEW MODE - Manual Remediation Issues")
    print("=" * 70)
    
    # Collect manual-review items from context
    manual_items = [
        opp for opp in context.opportunities
        if opp.agent_decision_required
    ]
    
    if not manual_items:
        print("\n[OK] No manual-review items found!")
        print("All issues have been automatically remediated or require no action.")
        print("=" * 70 + "\n")
        return
    
    print(f"\nFound {len(manual_items)} issue(s) requiring manual review:\n")
    
    workspace_root = Path.cwd()
    
    for idx, item in enumerate(manual_items, 1):
        
        print("=" * 70)
        print(f"Issue {idx} of {len(manual_items)}")
        print("=" * 70)
        print(f"Category: {item.type.upper()}")
        print(f"Priority: {item.priority.upper()}")
        print(f"\nIssue: {item.title}")
        
        if item.description:
            print(f"Details: {item.description}")
        
        print("\nSuggested Actions:")
        for action in item.suggested_actions:
            print(f"  • {action}")
        
        print("\n" + "-" * 70)
        print("What would you like to do?")
        print("  [s] Skip this issue for now")
        print("  [i] Get more information")
        print("  [a] Attempt remediation (guided)")
        print("  [q] Quit review mode")
        print("-" * 70)
        
        while True:
            try:
                choice = input("\nYour choice (s/i/a/q): ").strip().lower()
                
                if choice == 'q':
                    print("\nExiting review mode...")
                    print("=" * 70 + "\n")
                    return
                
                elif choice == 's':
                    print("Skipping to next issue...")
                    break
                
                elif choice == 'i':
                    # Show more detailed information
                    print("\n" + "~" * 70)
                    print("DETAILED INFORMATION")
                    print("~" * 70)
                    
                    # Show the full opportunity details
                    import json
                    print(json.dumps(item.to_dict(), indent=2))
                    print("~" * 70)
                    
                elif choice == 'a':
                    # Guided remediation
                    print("\n" + "~" * 70)
                    print("GUIDED REMEDIATION")
                    print("~" * 70)
                    
                    # Provide category-specific guidance
                    if 'efficiency' in item.type.lower():
                        _guide_efficiency_remediation(item, workspace_root)
                    elif 'minimalism' in item.type.lower():
                        _guide_minimalism_remediation(item, workspace_root)
                    elif 'security' in item.type.lower():
                        _guide_security_remediation(item, workspace_root)
                    
                    print("~" * 70)
                    break
                
                else:
                    print("Invalid choice. Please enter s, i, a, or q.")
            
            except KeyboardInterrupt:
                print("\n\nReview interrupted by user.")
                print("=" * 70 + "\n")
                return
            except EOFError:
                print("\n\nReview terminated.")
                print("=" * 70 + "\n")
                return
    
    print("\n" + "=" * 70)
    print("REVIEW COMPLETE")
    print("=" * 70)
    print(f"\nReviewed {len(manual_items)} issue(s).")
    print("\nTo re-run review mode: codesentinel dev-audit --review")
    print("To see current status: codesentinel dev-audit --agent")
    print("=" * 70 + "\n")


def _guide_efficiency_remediation(item: 'RemediationOpportunity', workspace_root: Path) -> None:
    """Provide guidance for efficiency issues."""
    title = item.title.lower()
    description = item.description.lower()
    
    if 'large' in title or 'repository' in description or 'size' in title:
        print("\nThis issue relates to repository size optimization.")
        print("\nRecommended approach:")
        print("1. Review .gitignore to ensure build artifacts are excluded")
        print("2. Check for large binary files that could use Git LFS")
        print("3. Consider moving test data/fixtures to external storage")
        print("\nCommands to investigate:")
        print("  git ls-files | xargs du -h | sort -h | tail -20  # Find largest tracked files")
        print("  du -sh *  # Check directory sizes")
    else:
        print("\nGeneral efficiency guidance:")
        print("Review the suggested actions above and determine which apply to your project.")


def _guide_minimalism_remediation(item: 'RemediationOpportunity', workspace_root: Path) -> None:
    """Provide guidance for minimalism issues."""
    title = item.title.lower()
    description = item.description.lower()
    
    if 'legacy' in title or 'archive' in description:
        print("\nThis relates to the quarantine_legacy_archive/ directory.")
        print("\nThe archive is important for:")
        print("  • Code archaeology and reference")
        print("  • Rollback capability if needed")
        print("  • Understanding evolution of the codebase")
        print("\nRecommended approach:")
        print("1. Verify all needed features have been ported from archived code")
        print("2. Create a compressed tarball: tar -czf legacy_archive_YYYYMMDD.tar.gz quarantine_legacy_archive/")
        print("3. Store the tarball in docs/ or external backup")
        print("4. Only remove after 30+ days of stable operation")
        print("\nDO NOT remove the archive if you're unsure about feature parity!")
    
    elif 'duplicate' in title or 'duplicate' in description:
        print("\nThis relates to duplicate/redundant code or configurations.")
        print("\nRecommended approach:")
        print("1. Identify which implementation is canonical")
        print("2. Verify the other is truly redundant (not a different use case)")
        print("3. Archive the redundant one to quarantine_legacy_archive/")
        print("4. Update all references to point to the canonical version")
        print("5. Test thoroughly after consolidation")
    
    else:
        print("\nGeneral minimalism guidance:")
        print("Focus on reducing clutter while preserving all functionality.")
        print("Always archive (don't delete) when removing code.")


def _guide_security_remediation(item: 'RemediationOpportunity', workspace_root: Path) -> None:
    """Provide guidance for security issues."""
    print("\nSecurity issue detected.")
    print("\nRecommended approach:")
    print("1. Verify whether this is a real credential or false positive")
    print("2. If real: immediately rotate the credential")
    print("3. Move sensitive data to environment variables or secret vault")
    print("4. Add the file to .gitignore if it contains secrets")
    print("5. Consider using git-secrets or similar tools for prevention")
    print("\nNEVER commit credentials to version control!")
