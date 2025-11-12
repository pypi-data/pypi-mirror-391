#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ASCII Cleanup Script for Satellite Instructions

Removes all Unicode characters from satellite instruction files,
replacing them with ASCII-safe equivalents.
"""

import sys
from pathlib import Path

# Files to clean
FILES = [
    'codesentinel/AGENT_INSTRUCTIONS.md',
    'tests/AGENT_INSTRUCTIONS.md',
    'docs/AGENT_INSTRUCTIONS.md',
    'tools/codesentinel/AGENT_INSTRUCTIONS.md'
]

# Unicode to ASCII replacements
REPLACEMENTS = {
    '\ufeff': '',    # BOM (Byte Order Mark) - remove entirely
    '\u2192': '->',  # Right arrow →
    '\u2190': '<-',  # Left arrow ←
    '\u2022': '*',   # Bullet •
    '\u2013': '-',   # En dash –
    '\u2014': '--',  # Em dash —
    '\u2018': "'",   # Left single quote '
    '\u2019': "'",   # Right single quote '
    '\u201c': '"',   # Left double quote "
    '\u201d': '"',   # Right double quote "
    '\u2026': '...', # Ellipsis …
    '\u2713': '[OK]',   # Check mark ✓
    '\u2717': '[FAIL]', # Cross mark ✗
    '\u2794': '->',  # Heavy arrow ➔
}

def clean_file(filepath: Path) -> int:
    """Clean a single file of Unicode characters."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        for unicode_char, ascii_replacement in REPLACEMENTS.items():
            content = content.replace(unicode_char, ascii_replacement)
        
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[OK] Cleaned {filepath}")
            return 1
        else:
            print(f"[OK] No changes needed for {filepath}")
            return 0
    except Exception as e:
        print(f"[FAIL] Error cleaning {filepath}: {e}")
        return -1

def main():
    workspace_root = Path.cwd()
    cleaned_count = 0
    
    for file_path in FILES:
        full_path = workspace_root / file_path
        if full_path.exists():
            result = clean_file(full_path)
            if result > 0:
                cleaned_count += result
        else:
            print(f"[WARN] File not found: {full_path}")
    
    print(f"\n[OK] Cleaned {cleaned_count} files")
    return 0

if __name__ == '__main__':
    sys.exit(main())
