"""
Documentation utilities for verification and fixing.

This module contains shared functions for documentation branding,
header/footer management, and integrity verification.
"""
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any
import re


def _normalize_markdown_whitespace(content: str) -> str:
    """
    Normalizes whitespace in markdown content.
    - Replaces multiple blank lines with a single blank line.
    - Removes trailing whitespace from lines (except intentional Markdown line breaks).
    - Ensures content ends with a single newline.
    
    Note: Preserves intentional Markdown line breaks (exactly two spaces at end of line)
    but removes all other trailing whitespace.
    """
    lines = content.split('\n')
    normalized_lines = []
    
    for line in lines:
        # Check if line ends with exactly 2 spaces (Markdown line break)
        # Must check for exactly 2, not 2+
        if len(line) >= 2 and line[-2:] == '  ' and (len(line) == 2 or line[-3] != ' '):
            # Keep exactly 2 trailing spaces (intentional line break)
            normalized_lines.append(line)
        else:
            # Strip all trailing whitespace
            normalized_lines.append(line.rstrip())
    
    # Rejoin lines
    content = '\n'.join(normalized_lines)
    
    # Replace 3 or more newlines with just two (one blank line)
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    # Ensure the file ends with a single newline
    content = content.strip() + '\n'
    
    return content


def verify_documentation_branding(file_path: Path) -> Tuple[bool, List[str]]:
    """
    Verify that documentation files follow SEAM Protection branding policy.
    
    CodeSentinel Policy: All public documentation must have consistent branding:
    - Primary locations: Use "SEAM Protected™" with trademark
    - Secondary locations: Use "SEAM Protection" or "SEAM-tight"
    - No excessive repetition or misuse
    
    Args:
        file_path: Path to documentation file to verify
        
    Returns:
        Tuple of (is_compliant, issues_found)
    """
    if not file_path.exists():
        return True, []
    
    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception as e:
        return False, [f"Could not read file: {e}"]
    
    issues = []
    file_name = file_path.name
    
    # Check for old policy references that should be updated
    old_patterns = [
        ('SECURITY > EFFICIENCY > MINIMALISM', 'should use SEAM Protection™ instead'),
        ('SECURITY.*EFFICIENCY.*MINIMALISM', 'should use SEAM Protection™ instead'),
    ]
    
    for pattern, reason in old_patterns:
        if re.search(pattern, content):
            issues.append(f"{file_name}: Found old policy terminology - {reason}")
    
    # Check for specific files that MUST have branding
    required_branding = {
        'README.md': ['SEAM Protected™', 'SEAM-Tight'],
        'SECURITY.md': ['SEAM Protected™'],
        '__init__.py': ['SEAM Protected™'],
        'copilot-instructions.md': ['SEAM Protection™'],
        '.github': ['SEAM Protection™'],
    }
    
    for req_file, required_terms in required_branding.items():
        if req_file in file_name or req_file in str(file_path):
            found_any = any(term in content for term in required_terms)
            if not found_any:
                issues.append(
                    f"{file_name}: Missing required SEAM Protection branding. "
                    f"Should contain one of: {', '.join(required_terms)}"
                )
    
    is_compliant = len(issues) == 0
    return is_compliant, issues


def verify_documentation_headers_footers(file_path: Path) -> Tuple[bool, List[str], Dict[str, Any]]:
    """
    Verify that documentation files have proper headers and footers.
    
    Requirements:
    - Markdown files (.md) should have clear title headers
    - Documentation should include metadata (version, date when applicable)
    - Key files should have SEAM Protection footer
    - Python files should have proper docstring headers
    
    Args:
        file_path: Path to documentation file to verify
        
    Returns:
        Tuple of (is_compliant, issues_found, metadata)
    """
    if not file_path.exists():
        return True, [], {}
    
    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception as e:
        return False, [f"Could not read file: {e}"], {}
    
    issues = []
    file_name = file_path.name
    metadata = {
        'has_title': False,
        'has_footer': False,
        'has_metadata': False,
        'file_type': file_path.suffix,
    }
    
    # Check markdown files
    if file_path.suffix == '.md':
        # Check for title (H1 heading)
        if re.search(r'^#\s+\S', content, re.MULTILINE):
            metadata['has_title'] = True
        else:
            issues.append(f"{file_name}: Missing H1 title header (# Title)")
        
        # Check for SEAM Protection footer in key files
        key_docs = {'README.md', 'SECURITY.md', 'CHANGELOG.md', 'CONTRIBUTING.md'}
        if file_name in key_docs:
            if 'SEAM Protected™' in content or 'SEAM Protection' in content:
                metadata['has_footer'] = True
            else:
                issues.append(f"{file_name}: Key documentation missing SEAM Protection footer")
        
        # Check for metadata (version, date, or last updated)
        if re.search(r'(Version|Date|Last Updated|Last Reviewed).*:\s*', content, re.IGNORECASE):
            metadata['has_metadata'] = True
    
    # Check Python files
    elif file_path.suffix == '.py':
        # Check for module docstring
        if content.startswith('"""') or content.startswith("'''"):
            metadata['has_title'] = True
        else:
            # Only warn if file is significant (>50 lines)
            if len(content.split('\n')) > 50:
                issues.append(f"{file_name}: Missing module docstring")
    
    is_compliant = len(issues) == 0
    return is_compliant, issues, metadata


def apply_branding_fixes(file_path: Path, verbose: bool = False) -> Tuple[bool, str]:
    """
    Apply automatic branding fixes to documentation files.
    
    Args:
        file_path: Path to documentation file
        verbose: Print detailed output
        
    Returns:
        Tuple of (success, message)
    """
    if not file_path.exists():
        return True, f"File not found: {file_path}"
    
    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception as e:
        return False, f"Could not read file: {e}"
    
    original_content = content
    modified = False
    
    # Fix 1: Replace old policy terminology with SEAM Protection
    patterns = [
        (r'SECURITY > EFFICIENCY > MINIMALISM', 'SEAM Protected™: Security, Efficiency, And Minimalism'),
        (r'SECURITY.*EFFICIENCY.*MINIMALISM', 'SEAM Protected™: Security, Efficiency, And Minimalism'),
    ]
    
    for old, new in patterns:
        if re.search(old, content):
            content = re.sub(old, new, content)
            modified = True
            if verbose:
                print(f"  Fixed: Replaced old policy terminology with SEAM Protection branding")
    
    # Fix 2: Add branding footer to markdown documentation files
    if file_path.suffix == '.md':
        key_docs = {'README.md', 'SECURITY.md', 'CHANGELOG.md', 'CONTRIBUTING.md'}
        if file_path.name in key_docs:
            footer = "\n\n---\n\nSEAM Protected™ by CodeSentinel"
            if footer not in content:
                # Only add if file is substantial and doesn't already have a similar footer
                if len(content) > 100 and not re.search(r'---\s*$', content, re.MULTILINE):
                    content += footer
                    modified = True
                    if verbose:
                        print(f"  Added: SEAM Protection branding footer")
    
    if modified:
        try:
            file_path.write_text(content, encoding='utf-8')
            return True, f"Applied branding fixes to {file_path.name}"
        except Exception as e:
            return False, f"Could not write file: {e}"
    
    return True, f"No branding fixes needed for {file_path.name}"


def apply_header_footer_fixes(file_path: Path, verbose: bool = False) -> Tuple[bool, str]:
    """
    Apply automatic header and footer fixes to documentation files.
    
    Args:
        file_path: Path to documentation file
        verbose: Print detailed output
        
    Returns:
        Tuple of (success, message)
    """
    if not file_path.exists():
        return True, f"File not found: {file_path}"
    
    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception as e:
        return False, f"Could not read file: {e}"
    
    original_content = content
    modified = False
    
    # Fix for markdown files: ensure proper footer formatting
    if file_path.suffix == '.md':
        key_docs = {'README.md', 'SECURITY.md', 'CHANGELOG.md', 'CONTRIBUTING.md', 
                    'CONTRIBUTING.md', 'QUICK_START.md'}
        
        if file_path.name in key_docs:
            # Ensure footer exists with proper formatting
            if not re.search(r'---\s*$', content, re.MULTILINE):
                # Add separator if missing
                if not content.endswith('\n'):
                    content += '\n'
                content += '\n---\n\nSEAM Protected™ by CodeSentinel\n'
                modified = True
                if verbose:
                    print(f"  Added: Proper footer separator and branding")
    
    if modified:
        try:
            file_path.write_text(content, encoding='utf-8')
            return True, f"Applied header/footer fixes to {file_path.name}"
        except Exception as e:
            return False, f"Could not write file: {e}"
    
    return True, f"No header/footer fixes needed for {file_path.name}"


def verify_and_fix_documentation_pipeline(file_paths: List[Path], dry_run: bool = False,
                                          verbose: bool = False, file_type_label: str = "") -> Dict[str, List[str]]:
    """
    Consolidated documentation verification and fix pipeline.
    
    This unified function maximizes efficiency and minimalism by:
    1. Verifying branding compliance (SEAM Protection™)
    2. Verifying header/footer structure
    3. Checking for encoding corruption
    4. Checking for excessive blank lines
    5. Applying automatic fixes if needed
    
    Security: All file operations use proper encoding validation.
    Efficiency: Single reusable pipeline eliminates duplicate code across all update subcommands.
    Minimalism: Replaces separate verification code in docs, readme, changelog, etc.
    
    Args:
        file_paths: List of Path objects to verify
        dry_run: If True, report issues without fixing
        verbose: Print detailed output
        file_type_label: Label for this verification pass (e.g., "README", "Documentation")
        
    Returns:
        Dictionary with results:
        {
            'verified': [files_that_passed],
            'fixed': [files_that_were_fixed],
            'errors': [files_with_errors],
            'branding_issues': [...],
            'header_footer_issues': [...],
            'encoding_issues': [...],
            'whitespace_issues': [...]
        }
    """
    results: Dict[str, List[str]] = {
        'verified': [],
        'fixed': [],
        'errors': [],
        'branding_issues': [],
        'header_footer_issues': [],
        'encoding_issues': [],
        'whitespace_issues': [],
    }
    
    for doc_file in file_paths:
        if not doc_file.exists():
            continue
        
        file_issues = []
        fixes_applied = False
        
        # 1. Check for encoding corruption
        try:
            content = doc_file.read_text(encoding='utf-8')
            # Verify encoding integrity
            content.encode('utf-8').decode('utf-8')
        except (UnicodeDecodeError, UnicodeEncodeError) as e:
            results['encoding_issues'].append(f"{doc_file.name}: {e}")
            results['errors'].append(doc_file.name)
            if verbose:
                print(f"   Encoding error: {doc_file.name}")
            continue
        except Exception as e:
            results['errors'].append(doc_file.name)
            if verbose:
                print(f"   Error reading: {doc_file.name}")
            continue
        
        # 2. Check for excessive blank lines
        if doc_file.suffix == '.md':
            line_count = len(content.split('\n'))
            # Heuristic: if more than 25% are blank, flag it
            non_empty_lines = len([l for l in content.split('\n') if l.strip()])
            blank_percentage = ((1 - non_empty_lines/line_count)*100) if line_count > 0 else 0
            if blank_percentage > 25:
                results['whitespace_issues'].append(
                    f"{doc_file.name}: {blank_percentage:.1f}% blank lines (threshold: 25%)"
                )
                file_issues.append("excessive_blanks")
                
                # Fix excessive blanks
                if not dry_run:
                    try:
                        normalized = _normalize_markdown_whitespace(content)
                        doc_file.write_text(normalized, encoding='utf-8')
                        fixes_applied = True
                        if verbose:
                            print(f"  ✓ Fixed (whitespace): {doc_file.name}")
                    except Exception as e:
                        results['errors'].append(f"{doc_file.name}: Could not fix whitespace")
                        continue
        
        # 3. Verify branding compliance
        is_branding_compliant, branding_issues_list = verify_documentation_branding(doc_file)
        if not is_branding_compliant:
            results['branding_issues'].extend(branding_issues_list)
            file_issues.append("branding")
            
            # Fix branding
            if not dry_run:
                success, message = apply_branding_fixes(doc_file, verbose)
                if success:
                    fixes_applied = True
                    if verbose:
                        print(f"  ✓ Fixed (branding): {doc_file.name}")
        
        # 4. Verify headers/footers (markdown only)
        is_hf_compliant = True
        hf_issues_list = []
        if doc_file.suffix == '.md':
            is_hf_compliant, hf_issues_list, metadata = verify_documentation_headers_footers(doc_file)
            if not is_hf_compliant:
                results['header_footer_issues'].extend(hf_issues_list)
                file_issues.append("header_footer")
                
                # Fix header/footer
                if not dry_run:
                    success, message = apply_header_footer_fixes(doc_file, verbose)
                    if success:
                        fixes_applied = True
                        if verbose:
                            print(f"  ✓ Fixed (header/footer): {doc_file.name}")
        
        # Summary for this file
        if not file_issues:
            results['verified'].append(doc_file.name)
            if verbose:
                print(f"  ✓ Full compliance: {doc_file.name}")
        elif fixes_applied:
            results['fixed'].append(doc_file.name)
        elif dry_run and file_issues:
            if verbose:
                print(f"  [DRY-RUN] Would fix: {doc_file.name} ({', '.join(file_issues)})")
    
    return results
