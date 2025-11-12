# -*- coding: utf-8 -*-
"""
Instruction Defragmentation Utility for CodeSentinel

This script reorganizes the .github/copilot-instructions.md file to improve
clarity, logical flow, and agent comprehension. It parses the markdown file,
reorders sections based on a defined "ideal" structure, and writes the
organized content back to the file.

This helps to "defrag" the instructions as they grow and evolve over time.

Author: GitHub Copilot
Date: November 11, 2025
"""

import logging
from pathlib import Path
from collections import OrderedDict
from datetime import datetime
import argparse
import json
import shutil

logger = logging.getLogger(__name__)

# --- Configuration ---
# Configuration is now loaded from an external schema file.

def parse_instructions(content: str) -> "OrderedDict[str, str]":
    """
    Parses the markdown content into a dictionary of sections.
    
    Args:
        content: The string content of the markdown file.
        
    Returns:
        An ordered dictionary where keys are section titles (H2) and
        values are the full markdown content of that section.
    """
    sections = OrderedDict()
    lines = content.splitlines()
    current_section_title = "Header" # For content before the first H2
    current_section_content = []

    for line in lines:
        if line.startswith("## ") and not line.startswith("###"):
            # Save the previous section
            if current_section_title:
                sections[current_section_title] = "\n".join(current_section_content).strip()
            
            # Start a new section
            current_section_title = line[3:].strip()
            current_section_content = [line]
        else:
            current_section_content.append(line)
    
    # Save the last section
    if current_section_title:
        sections[current_section_title] = "\n".join(current_section_content).strip()
        
    return sections


def defrag_instructions_content(content: str, schema: dict) -> str:
    """
    Reorganizes the markdown content based on the provided schema.
    
    Args:
        content: The original markdown content.
        schema: The loaded JSON schema defining the structure.
        
    Returns:
        The reorganized markdown content as a string.
    """
    parsed_sections = parse_instructions(content)
    
    # --- Merging Step ---
    merge_rules = schema.get("merge_sections", {})
    for parent, children in merge_rules.items():
        new_content_lines = [f"## {parent}\n"]
        for child_title in children:
            if child_title in parsed_sections:
                child_content = parsed_sections[child_title]
                # Extract content, skipping the old H2 title
                child_lines = child_content.splitlines()[1:]
                new_content_lines.append("\n".join(child_lines).strip())
                del parsed_sections[child_title]
        
        # Only create the merged section if it has content
        if len(new_content_lines) > 1:
            parsed_sections[parent] = "\n\n".join(new_content_lines)

    # --- Ordering Step ---
    defragged_content = []
    ideal_order = schema.get("section_order", [])
    
    # Add the header first if it exists
    if "Header" in parsed_sections:
        defragged_content.append(parsed_sections.pop("Header"))
        
    # Add sections in the ideal order
    for section_title in ideal_order:
        if section_title in parsed_sections:
            defragged_content.append(parsed_sections.pop(section_title))
            
    # Append any remaining sections
    for section_title, section_content in parsed_sections.items():
        defragged_content.append(section_content)
        
    return "\n\n---\n\n".join(defragged_content)


def run_defrag(target_file: Path, schema_file: Path, dry_run: bool, no_backup: bool) -> bool:
    """
    Reads, defragments, and writes back an instructions file based on a schema.
    
    Args:
        target_file: The path to the markdown file to defragment.
        schema_file: The path to the JSON schema file.
        dry_run: If True, prints changes instead of writing them.
        no_backup: If True, disables automatic backup.
        
    Returns:
        True if successful, False otherwise.
    """
    if not target_file.exists():
        logger.error(f"Target file not found at: {target_file}")
        return False
    if not schema_file.exists():
        logger.error(f"Schema file not found at: {schema_file}")
        return False
        
    try:
        logger.info(f"Reading target file: {target_file}")
        original_content = target_file.read_text(encoding="utf-8")
        
        logger.info(f"Loading schema: {schema_file}")
        with open(schema_file, 'r') as f:
            schema = json.load(f)
            
        logger.info("Defragmenting instructions content...")
        defragged_content = defrag_instructions_content(original_content, schema)
        
        header = f"""<!-- 
This file is auto-organized by the instruction defragmentation utility.
Last organized: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
-->\n\n"""
        
        final_content = header + defragged_content
        
        if dry_run:
            print("--- DRY RUN: Proposed changes ---")
            # A simple diff-like output
            import difflib
            diff = difflib.unified_diff(
                original_content.splitlines(keepends=True),
                final_content.splitlines(keepends=True),
                fromfile='original',
                tofile='defragmented'
            )
            print("".join(diff))
            print("--- End of DRY RUN ---")
            return True

        if not no_backup:
            backup_path = target_file.with_suffix(f"{target_file.suffix}.bak")
            logger.info(f"Creating backup at: {backup_path}")
            shutil.copy2(target_file, backup_path)
            
        logger.info(f"Writing reorganized instructions back to: {target_file}")
        target_file.write_text(final_content, encoding="utf-8")
        
        logger.info("Instructions successfully defragmented.")
        return True
        
    except Exception as e:
        logger.error(f"An error occurred during instruction defragmentation: {e}", exc_info=True)
        return False

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Defragment and organize markdown instruction files.")
    parser.add_argument(
        "--target-file",
        type=Path,
        required=True,
        help="Path to the markdown instruction file to process."
    )
    parser.add_argument(
        "--schema",
        type=Path,
        required=True,
        help="Path to the JSON schema file defining the structure."
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply the changes to the file. Default is to do a dry run."
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Disable the creation of a .bak backup file."
    )
    
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # The --apply flag controls the 'dry_run' parameter inversion.
    if not run_defrag(args.target_file, args.schema, not args.apply, args.no_backup):
        exit(1)
