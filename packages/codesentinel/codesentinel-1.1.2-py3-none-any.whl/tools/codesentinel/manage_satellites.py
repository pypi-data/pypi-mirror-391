#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Satellite Instruction Manager for CodeSentinel

This script manages all satellite AGENT_INSTRUCTIONS.md files across the codebase.
It can validate, defragment, and report on the status of all satellite files.

Author: GitHub Copilot
Date: November 11, 2025
"""

import logging
import argparse
import json
from pathlib import Path
from typing import List, Dict, Tuple
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from defrag_instructions import run_defrag

logger = logging.getLogger(__name__)

# Define all satellite instruction files and their schemas
SATELLITES = [
    {
        "name": "Core Package",
        "instruction_file": "codesentinel/AGENT_INSTRUCTIONS.md",
        "schema_file": "tools/instruction_schemas/codesentinel_schema.json"
    },
    {
        "name": "Maintenance Tools",
        "instruction_file": "tools/codesentinel/AGENT_INSTRUCTIONS.md",
        "schema_file": "tools/instruction_schemas/tools_schema.json"
    },
    {
        "name": "Testing",
        "instruction_file": "tests/AGENT_INSTRUCTIONS.md",
        "schema_file": "tools/instruction_schemas/tests_schema.json"
    },
    {
        "name": "Documentation",
        "instruction_file": "docs/AGENT_INSTRUCTIONS.md",
        "schema_file": "tools/instruction_schemas/docs_schema.json"
    },
    {
        "name": "Main Instructions",
        "instruction_file": ".github/copilot-instructions.md",
        "schema_file": "tools/instruction_schemas/default_schema.json"
    }
]


def get_workspace_root() -> Path:
    """Find the workspace root directory."""
    current = Path.cwd()
    # Look for .git directory or pyproject.toml
    while current != current.parent:
        if (current / ".git").exists() or (current / "pyproject.toml").exists():
            return current
        current = current.parent
    return Path.cwd()


def validate_satellite(satellite: Dict, workspace_root: Path) -> Tuple[bool, str]:
    """
    Validate that a satellite instruction file and its schema exist.
    
    Returns:
        Tuple of (is_valid, message)
    """
    instruction_path = workspace_root / satellite["instruction_file"]
    schema_path = workspace_root / satellite["schema_file"]
    
    if not instruction_path.exists():
        return False, f"Instruction file not found: {instruction_path}"
    if not schema_path.exists():
        return False, f"Schema file not found: {schema_path}"
    
    return True, "Valid"


def defrag_all_satellites(workspace_root: Path, dry_run: bool = True) -> Dict[str, bool]:
    """
    Run defragmentation on all satellite instruction files.
    
    Returns:
        Dictionary mapping satellite names to success status
    """
    results = {}
    
    for satellite in SATELLITES:
        name = satellite["name"]
        instruction_path = workspace_root / satellite["instruction_file"]
        schema_path = workspace_root / satellite["schema_file"]
        
        logger.info(f"Processing: {name}")
        
        # Validate first
        is_valid, message = validate_satellite(satellite, workspace_root)
        if not is_valid:
            logger.error(f"  {message}")
            results[name] = False
            continue
        
        # Run defragmentation
        try:
            success = run_defrag(instruction_path, schema_path, dry_run, no_backup=dry_run)
            results[name] = success
            if success:
                logger.info(f"  [OK] Successfully processed")
            else:
                logger.error(f"  [FAIL] Failed to process")
        except Exception as e:
            logger.error(f"  [FAIL] Error: {e}")
            results[name] = False
    
    return results


def report_satellite_status(workspace_root: Path) -> None:
    """Generate a status report for all satellite instruction files."""
    print("\n=== Satellite Instruction File Status ===\n")
    
    for satellite in SATELLITES:
        name = satellite["name"]
        instruction_path = workspace_root / satellite["instruction_file"]
        schema_path = workspace_root / satellite["schema_file"]
        
        is_valid, message = validate_satellite(satellite, workspace_root)
        
        print(f"{name}:")
        print(f"  Instruction: {instruction_path.relative_to(workspace_root)}")
        print(f"  Schema: {schema_path.relative_to(workspace_root)}")
        
        if is_valid:
            # Get file size
            size_kb = instruction_path.stat().st_size / 1024
            print(f"  Status: [OK] Valid ({size_kb:.1f} KB)")
        else:
            print(f"  Status: [FAIL] {message}")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Manage satellite AGENT_INSTRUCTIONS.md files across the codebase."
    )
    parser.add_argument(
        "action",
        choices=["status", "defrag", "validate"],
        help="Action to perform: status (report), defrag (reorganize), validate (check files exist)"
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply changes when defragmenting (default is dry-run)"
    )
    
    args = parser.parse_args()
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    workspace_root = get_workspace_root()
    logger.info(f"Workspace root: {workspace_root}")
    
    if args.action == "status":
        report_satellite_status(workspace_root)
    
    elif args.action == "validate":
        print("\n=== Validating Satellite Files ===\n")
        all_valid = True
        for satellite in SATELLITES:
            is_valid, message = validate_satellite(satellite, workspace_root)
            status = "[OK]" if is_valid else "[FAIL]"
            print(f"{status} {satellite['name']}: {message}")
            all_valid = all_valid and is_valid
        
        if all_valid:
            print("\n[OK] All satellite files are valid")
            return 0
        else:
            print("\n[FAIL] Some satellite files have issues")
            return 1
    
    elif args.action == "defrag":
        dry_run = not args.apply
        mode = "DRY RUN" if dry_run else "APPLY"
        print(f"\n=== Defragmenting All Satellites ({mode}) ===\n")
        
        results = defrag_all_satellites(workspace_root, dry_run)
        
        print("\n=== Results ===\n")
        success_count = sum(1 for v in results.values() if v)
        total_count = len(results)
        
        for name, success in results.items():
            status = "[OK]" if success else "[FAIL]"
            print(f"{status} {name}")
        
        print(f"\nSuccessful: {success_count}/{total_count}")
        
        if success_count == total_count:
            print("\n[OK] All satellite files processed successfully")
            return 0
        else:
            print("\n[FAIL] Some satellite files failed to process")
            return 1


if __name__ == '__main__':
    exit(main())
