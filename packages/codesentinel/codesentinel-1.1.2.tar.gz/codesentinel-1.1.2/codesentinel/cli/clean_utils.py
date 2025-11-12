"""
Utility functions for the 'clean' command in the CodeSentinel CLI.

This module provides the core logic for scanning, collecting, and removing
various types of artifacts from the workspace, such as cache files, logs,
build artifacts, and policy violations. It is designed to be called from
the main CLI dispatcher.
"""

import re
import shutil
from pathlib import Path
from datetime import datetime, timedelta

from ..utils.root_policy import ALLOWED_ROOT_FILES, ALLOWED_ROOT_DIRS

# --- Helper Functions ---

def _get_size(path: Path) -> int:
    """Calculate the total size of a file or directory."""
    if path.is_file():
        try:
            return path.stat().st_size
        except FileNotFoundError:
            return 0
    total = 0
    try:
        for item in path.rglob('*'):
            if item.is_file():
                try:
                    total += item.stat().st_size
                except FileNotFoundError:
                    continue
    except (FileNotFoundError, PermissionError):
        pass
    return total

def _is_older_than(path: Path, days: int) -> bool:
    """Check if a file or directory is older than a specified number of days."""
    if not days:
        return True
    try:
        mtime = datetime.fromtimestamp(path.stat().st_mtime)
        return datetime.now() - mtime > timedelta(days=days)
    except (FileNotFoundError, PermissionError):
        return False

# --- Core Scanning and Collection Logic ---

def _scan_and_collect_artifacts(
    workspace_root: Path,
    patterns: list,
    older_than: int,
    verbose: bool
) -> list:
    """
    Scans for files and directories matching given patterns and collects them.

    Args:
        workspace_root: The root directory to scan from.
        patterns: A list of glob patterns to search for.
        older_than: The age in days for a file to be considered for cleaning.
        verbose: If True, print details of found items.

    Returns:
        A list of tuples, where each tuple contains ('type', path, size).
    """
    collected_items = []
    for pattern in patterns:
        for item in workspace_root.rglob(pattern):
            if _is_older_than(item, older_than):
                item_type = 'dir' if item.is_dir() else 'file'
                size = _get_size(item)
                collected_items.append((item_type, item, size))
                if verbose:
                    print(f"  Found: {item.relative_to(workspace_root)}")
    return collected_items

# --- Specialized Cleanup Handlers ---

def _handle_root_policy_cleanup(
    workspace_root: Path,
    dry_run: bool,
    force: bool,
    verbose: bool
) -> bool:
    """
    Handles the --root --full policy validation and cleanup.
    Archives unauthorized files and directories found in the root.
    This is a non-destructive operation.
    """
    print("🔍 Scanning for policy violations (--full mode)...")
    
    # Use central policy configuration
    policy_violations = []
    for item in workspace_root.iterdir():
        if item.name in {'.git', '.gitignore'}:
            continue
        
        is_allowed = (item.is_dir() and item.name in ALLOWED_ROOT_DIRS) or \
                     (item.is_file() and item.name in ALLOWED_ROOT_FILES)
        
        if not is_allowed:
            reason = 'unauthorized directory' if item.is_dir() else 'unauthorized file'
            if item.name.startswith('test_') or item.name.endswith('_test.py'):
                reason = 'test/diagnostic file'
            
            policy_violations.append({
                'type': 'directory' if item.is_dir() else 'file',
                'path': item,
                'name': item.name,
                'reason': reason,
                'target': 'quarantine_legacy_archive/',
                'action': 'archive'
            })
            if verbose:
                print(f"  Found (policy violation): {item.name} [{reason}]")

    if not policy_violations:
        print("  ✓ No policy violations found in root directory.")
        return True

    print(f"\n⚠️  Found {len(policy_violations)} policy violations:")
    print("All items will be ARCHIVED (not deleted) per NON-DESTRUCTIVE policy\n")
    
    for i, violation in enumerate(policy_violations, 1):
        print(f"  {i}. [{violation['type'].upper()}] {violation['name']}")
        print(f"     Reason: {violation['reason']}")
        print(f"     Action: Archive to {violation['target']}")

    if dry_run:
        print("\n[DRY-RUN] Would archive the items above.")
        return True

    if not force:
        response = input("\nArchive these items to quarantine_legacy_archive/? (y/N): ").strip().lower()
        if response != 'y':
            print("Policy compliance cleanup cancelled.")
            return False

    archive_dir = workspace_root / 'quarantine_legacy_archive'
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    archived_count = 0
    for violation in policy_violations:
        try:
            target_path = archive_dir / violation['path'].name
            if target_path.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                base_name, *ext = violation['path'].name.rsplit('.', 1)
                target_path = archive_dir / f"{base_name}_{timestamp}{'.' + ext[0] if ext else ''}"
            
            shutil.move(str(violation['path']), str(target_path))
            archived_count += 1
            if verbose:
                print(f"  ✓ Archived: {violation['name']} → quarantine_legacy_archive/")
        except Exception as e:
            print(f"   Failed to archive {violation['name']}: {e}")
    
    print(f"\n✓ Successfully archived {archived_count}/{len(policy_violations)} items")
    print("  Items are preserved in quarantine_legacy_archive/ for review")
    return True


def _handle_emoji_cleanup(workspace_root: Path, dry_run: bool, verbose: bool, include_gui: bool) -> list:
    """Scans for and removes policy-violating emojis from files."""
    print("Scanning for policy-violating emoji usage...")
    files_with_changes = []
    
    # A more comprehensive emoji pattern
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "]+",
        flags=re.UNICODE,
    )
    
    # Define allowed emojis
    ALLOWED_EMOJIS = {'✓', '❌', '⚠️', '🔍', '🧹', '✨', '⚙️', '📄', '🔖', '⭐', '➡️'}
    
    # Exclude directories
    exclude_dirs = {'.git', '.github', '__pycache__', 'build', 'dist', 'docs/assets'}
    if not include_gui:
        exclude_dirs.add('codesentinel/gui')

    for item in workspace_root.rglob('*'):
        if item.is_file() and item.suffix in {'.py', '.md', '.txt', '.json'}:
            # Check if file is in an excluded directory
            if any(excluded_dir in str(item.relative_to(workspace_root)) for excluded_dir in exclude_dirs):
                continue

            try:
                original_content = item.read_text(encoding='utf-8')
                
                def replace_emoji(match):
                    emoji = match.group(0)
                    return emoji if emoji in ALLOWED_EMOJIS else ''

                modified_content = emoji_pattern.sub(replace_emoji, original_content)

                if original_content != modified_content:
                    if verbose:
                        print(f"  Found policy-violating emojis in: {item.relative_to(workspace_root)}")
                    
                    if not dry_run:
                        item.write_text(modified_content, encoding='utf-8')
                    
                    files_with_changes.append(item)

            except (UnicodeDecodeError, PermissionError):
                continue # Skip binary files or files with reading issues
    
    return files_with_changes


# --- Main Orchestrator ---

def perform_cleanup(args):
    """
    Orchestrates the entire cleanup process based on parsed arguments.
    """
    workspace_root = Path.cwd()
    dry_run = args.dry_run
    force = args.force
    verbose = args.verbose
    older_than = args.older_than

    clean_targets = {
        'cache': args.cache, 'temp': args.temp, 'logs': args.logs,
        'build': args.build, 'test': args.test, 'root': args.root,
        'emojis': args.emojis
    }

    is_default_run = not any(clean_targets.values())
    if is_default_run or args.all:
        clean_targets.update({'cache': True, 'temp': True, 'logs': True})
        if is_default_run:
            print("🧹 Running clean (default: cache, temp, logs)\n")

    items_to_archive = []
    total_size = 0

    # Define artifact patterns
    PATTERNS = {
        'cache': ['__pycache__', '*.pyc', '*.pyo'],
        'temp': ['*.tmp', '.cache'],
        'logs': ['*.log'],
        'build': ['dist', 'build', '*.egg-info'],
        'test': ['.pytest_cache', '.coverage', 'htmlcov', '.tox'],
        'root': ['__pycache__', '*.pyc', '*.pyo', '*.tmp'] # Basic root clutter
    }

    # --- Scan and Collect ---
    for target, enabled in clean_targets.items():
        if enabled and target in PATTERNS:
            print(f"🔍 Scanning for {target} artifacts...")
            patterns_to_scan = PATTERNS[target]
            # For root, scan only at the top level
            if target == 'root':
                for pattern in patterns_to_scan:
                    for item in workspace_root.glob(pattern):
                        items_to_archive.append(('dir' if item.is_dir() else 'file', item, _get_size(item)))
                        if verbose: print(f"  Found: {item.name}")
            else:
                items_to_archive.extend(
                    _scan_and_collect_artifacts(workspace_root, patterns_to_scan, older_than, verbose)
                )

    # --- Specialized Handlers ---
    if clean_targets.get('root') and getattr(args, 'full', False):
        if not _handle_root_policy_cleanup(workspace_root, dry_run, force, verbose):
            return # User cancelled operation

    if clean_targets.get('emojis'):
        changed_files = _handle_emoji_cleanup(workspace_root, dry_run, verbose, getattr(args, 'include_gui', False))
        if changed_files:
            print(f"\n✨ Removed non-compliant emojis from {len(changed_files)} file(s).")
            if dry_run:
                print("  (Dry-run mode, no files were modified)")

    # --- Process and Archive Collected Items ---
    if not items_to_archive:
        if not any([clean_targets.get('root') and getattr(args, 'full', False), clean_targets.get('emojis')]):
            print("✨ Workspace is already clean. No items found to archive.")
        return

    print(f"\nFound {len(items_to_archive)} items to archive:")
    for _, path, size in items_to_archive:
        total_size += size
        print(f"  - {str(path.relative_to(workspace_root)):<60} ({size / 1024:.2f} KB)")
    
    print(f"\nTotal potential space to be reclaimed: {total_size / (1024*1024):.2f} MB")

    if dry_run:
        print("\n[DRY-RUN] No files or directories will be archived.")
        return

    if not force:
        response = input("\nProceed with archiving these items? (y/N): ").strip().lower()
        if response != 'y':
            print("Cleanup operation cancelled.")
            return

    archive_dir = workspace_root / 'quarantine_legacy_archive'
    archive_dir.mkdir(exist_ok=True)
    archived_count = 0

    for item_type, path, _ in items_to_archive:
        try:
            target_path = archive_dir / path.name
            if target_path.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                base_name, *ext = path.name.rsplit('.', 1)
                target_path = archive_dir / f"{base_name}_{timestamp}{'.' + ext[0] if ext else ''}"

            if item_type == 'dir':
                shutil.move(str(path), str(target_path))
            else: # file
                shutil.move(str(path), str(target_path))
            
            archived_count += 1
            if verbose:
                print(f"  ✓ Archived: {path.name}")
        except Exception as e:
            print(f"   Failed to archive {path.name}: {e}")

    print(f"\n🧹 Successfully archived {archived_count}/{len(items_to_archive)} items.")
    print("   Items are preserved in quarantine_legacy_archive/ for review.")
