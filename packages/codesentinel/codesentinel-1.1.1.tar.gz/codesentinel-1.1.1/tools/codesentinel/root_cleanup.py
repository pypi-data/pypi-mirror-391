"""
Root Directory Cleanup Automation
==================================

Automated task for validating and cleaning up the repository root directory.
Ensures only essential files and folders remain in the root, in compliance with
CodeSentinel's file organization policy (SECURITY > EFFICIENCY > MINIMALISM).

This module is executed as part of daily maintenance workflows and pre-commit hooks.
"""

import os
import sys
import json
import logging
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Any
from datetime import datetime

# Add parent directory to path to import from codesentinel package
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from codesentinel.utils.root_policy import (
    ALLOWED_ROOT_FILES,
    ALLOWED_ROOT_DIRS,
    FILE_MAPPINGS
)


class RootDirectoryValidator:
    """Validates and cleans up repository root directory."""

    def __init__(self, repo_root: str, dry_run: bool = False, logger: logging.Logger = None):
        """
        Initialize root directory validator.

        Args:
            repo_root: Path to repository root.
            dry_run: If True, only report issues without making changes.
            logger: Logger instance. Creates new if not provided.
        """
        self.repo_root = Path(repo_root)
        self.dry_run = dry_run
        self.logger = logger or logging.getLogger('RootDirectoryValidator')
        
        self.issues_found = []
        self.files_moved = []
        self.files_deleted = []
        self.cleanup_summary = {}

    def validate(self) -> Dict[str, Any]:
        """
        Validate root directory structure.

        Returns:
            Dict containing validation results.
        """
        self.logger.info(f"Starting root directory validation (dry_run={self.dry_run})")
        
        self.issues_found = []
        self.files_moved = []
        self.files_deleted = []

        # Check all items in root
        for item in self.repo_root.iterdir():
            if item.name.startswith('.') and item.is_dir():
                # Allow dot directories like .git, .github
                if item.name not in {'.git', '.github', '.gitignore'}:
                    if not item.is_file() or item.name not in ALLOWED_ROOT_FILES:
                        if item.name not in ALLOWED_ROOT_DIRS:
                            self.issues_found.append({
                                'type': 'unauthorized_dot_dir',
                                'path': str(item),
                                'action': 'should_delete'
                            })
                continue

            if item.is_dir():
                # Check if directory is allowed
                if item.name not in ALLOWED_ROOT_DIRS:
                    self.issues_found.append({
                        'type': 'unauthorized_directory',
                        'path': str(item),
                        'action': 'should_delete'
                    })
            else:
                # Check if file is allowed
                self._validate_file(item)

        self.cleanup_summary = {
            'total_issues': len(self.issues_found),
            'files_moved': len(self.files_moved),
            'files_deleted': len(self.files_deleted),
            'issues': self.issues_found
        }

        return {
            'status': 'success',
            'dry_run': self.dry_run,
            'root_directory': str(self.repo_root),
            'validation_timestamp': datetime.now().isoformat(),
            'summary': self.cleanup_summary,
            'files_moved': self.files_moved,
            'files_deleted': self.files_deleted
        }

    def _validate_file(self, file_path: Path):
        """
        Validate a file in the root directory.

        Args:
            file_path: Path to the file.
        """
        filename = file_path.name

        # Check if file is in allowed list
        if filename in ALLOWED_ROOT_FILES:
            return

        # Check if file should be moved
        target_dir = self._find_target_directory(filename)
        if target_dir:
            action = 'move' if not self._check_duplicate_exists(filename, target_dir) else 'delete'
            self.issues_found.append({
                'type': 'misplaced_file',
                'path': str(file_path),
                'target': target_dir,
                'action': action
            })
        else:
            # Unknown file - flag as potential duplicate or outdated
            self.issues_found.append({
                'type': 'unknown_file',
                'path': str(file_path),
                'action': 'review_required'
            })

    def _find_target_directory(self, filename: str) -> str:
        """
        Find target directory for a misplaced file.

        Args:
            filename: Name of the file.

        Returns:
            Target directory path or empty string if not found.
        """
        for prefix, target_dir in FILE_MAPPINGS.items():
            if prefix in filename:
                return target_dir
        return ""

    def _check_duplicate_exists(self, filename: str, target_dir: str) -> bool:
        """
        Check if file already exists in target directory.

        Args:
            filename: Name of the file.
            target_dir: Target directory path.

        Returns:
            True if duplicate exists, False otherwise.
        """
        target_path = self.repo_root / target_dir / filename
        return target_path.exists()

    def cleanup(self) -> Dict[str, Any]:
        """
        Execute cleanup operations based on validation results.

        Returns:
            Dict containing cleanup results.
        """
        if not self.issues_found:
            self.logger.info("Root directory is clean - no cleanup needed")
            return {
                'status': 'success',
                'message': 'Root directory is clean',
                'files_moved': [],
                'files_deleted': []
            }

        self.logger.info(f"Found {len(self.issues_found)} issues to address")

        for issue in self.issues_found:
            try:
                if issue['action'] == 'move':
                    self._move_file(issue)
                elif issue['action'] == 'delete':
                    self._delete_file(issue)
                elif issue['action'] == 'review_required':
                    self.logger.warning(f"Manual review required for: {issue['path']}")
            except Exception as e:
                self.logger.error(f"Failed to process {issue['path']}: {e}")

        result = {
            'status': 'success',
            'dry_run': self.dry_run,
            'files_moved': self.files_moved,
            'files_deleted': self.files_deleted,
            'total_processed': len(self.files_moved) + len(self.files_deleted)
        }

        return result

    def _move_file(self, issue: Dict[str, str]):
        """
        Move a misplaced file to its target directory.

        Args:
            issue: Issue dictionary with file information.
        """
        source = Path(issue['path'])
        target_dir = self.repo_root / issue['target']
        target_path = target_dir / source.name

        self.logger.info(f"Moving {source.name} to {issue['target']}")

        if not self.dry_run:
            target_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source), str(target_path))
            self.files_moved.append({
                'file': source.name,
                'from': str(source),
                'to': str(target_path),
                'timestamp': datetime.now().isoformat()
            })
        else:
            self.files_moved.append({
                'file': source.name,
                'from': str(source),
                'to': str(target_path),
                'timestamp': datetime.now().isoformat(),
                'dry_run': True
            })

    def _delete_file(self, issue: Dict[str, str]):
        """
        Delete a duplicate file from root.

        Args:
            issue: Issue dictionary with file information.
        """
        file_path = Path(issue['path'])
        target = issue.get('target', 'unknown')

        self.logger.info(f"Deleting duplicate {file_path.name} (exists in {target})")

        if not self.dry_run:
            file_path.unlink()
            self.files_deleted.append({
                'file': file_path.name,
                'path': str(file_path),
                'reason': 'duplicate_in_target_directory',
                'timestamp': datetime.now().isoformat()
            })
        else:
            self.files_deleted.append({
                'file': file_path.name,
                'path': str(file_path),
                'reason': 'duplicate_in_target_directory',
                'timestamp': datetime.now().isoformat(),
                'dry_run': True
            })

    def get_summary(self) -> Dict[str, Any]:
        """Get cleanup summary."""
        return self.cleanup_summary


def main():
    """Main entry point for root directory cleanup."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description='CodeSentinel Root Directory Cleanup'
    )
    parser.add_argument(
        'repo_root',
        nargs='?',
        default='.',
        help='Repository root directory (default: current directory)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without making changes'
    )
    parser.add_argument(
        '--validate-only',
        action='store_true',
        help='Only validate, do not cleanup'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger('RootCleanup')

    # Create validator
    validator = RootDirectoryValidator(
        args.repo_root,
        dry_run=args.dry_run,
        logger=logger
    )

    # Validate
    validation_result = validator.validate()
    print(json.dumps(validation_result, indent=2))

    if validation_result['summary']['total_issues'] == 0:
        logger.info("✓ Root directory is clean")
        return 0

    if args.validate_only:
        logger.info(f"Validation found {validation_result['summary']['total_issues']} issues")
        return 1

    # Cleanup
    cleanup_result = validator.cleanup()
    print(json.dumps(cleanup_result, indent=2))

    if cleanup_result['total_processed'] > 0:
        logger.info(f"✓ Cleanup complete: {cleanup_result['total_processed']} files processed")
        if args.dry_run:
            logger.info("(Dry run - no actual changes made)")
        return 0
    else:
        logger.warning(" No files could be processed")
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(main())
