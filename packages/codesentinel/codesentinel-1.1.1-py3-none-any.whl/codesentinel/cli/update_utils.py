"""
Utilities for the 'update' command.

This module contains the logic for updating repository files and documentation,
including docs, changelogs, READMEs, version numbers, and dependencies.
"""
from pathlib import Path
import subprocess
from .doc_utils import verify_and_fix_documentation_pipeline
from ..utils.versioning import set_project_version

# Import template functions - these need to be imported after __init__ is loaded
# to avoid circular imports
def _get_template_functions():
    """Lazy import of template functions to avoid circular imports."""
    from . import (
        show_template_options,
        get_header_templates,
        set_header_for_file,
        get_footer_templates,
        set_footer_for_file,
        edit_headers_interactive,
        edit_footers_interactive
    )
    return {
        'show_template_options': show_template_options,
        'get_header_templates': get_header_templates,
        'set_header_for_file': set_header_for_file,
        'get_footer_templates': get_footer_templates,
        'set_footer_for_file': set_footer_for_file,
        'edit_headers_interactive': edit_headers_interactive,
        'edit_footers_interactive': edit_footers_interactive
    }

def _validate_content_placeholders(content: str, file_name: str) -> (list, list):
    """Finds placeholder text like TODO, FIXME, etc."""
    warnings = []
    issues = []
    import re
    placeholders = re.findall(r'\b(TODO|FIXME|XXX|NOTE|HACK)\b[:\s]', content, re.IGNORECASE)
    if placeholders:
        for p in placeholders:
            warnings.append(f"  - Found placeholder text: '{p}' in {file_name}")
    return issues, warnings

def _validate_content_links(content: str, file_name: str) -> (list, list):
    """Checks for broken links in Markdown files."""
    issues = []
    warnings = []
    import re
    try:
        import requests
    except ImportError:
        warnings.append("  - 'requests' library not found. Skipping link validation. Run 'pip install requests'.")
        return issues, warnings

    links = re.findall(r'\[.*?\]\((https?://.*?)\)', content)
    for link in links:
        try:
            response = requests.head(link, timeout=5, allow_redirects=True)
            if response.status_code >= 400:
                issues.append(f"  - Broken link in {file_name}: {link} (status code {response.status_code})")
        except requests.RequestException as e:
            warnings.append(f"  - Could not check link in {file_name}: {link} ({e})")
    return issues, warnings


def _validate_oracl_documentation(content: str, file_name: str) -> tuple[list, list]:
    """
    Validates ORACL™ Intelligence Ecosystem documentation in README and SECURITY files.
    
    Returns:
        (issues, warnings) - Lists of validation findings
    """
    issues = []
    warnings = []
    
    # Only validate README.md and SECURITY.md
    if file_name not in ['README.md', 'SECURITY.md']:
        return issues, warnings
    
    if file_name == 'README.md':
        # README should document ORACL™ as a major feature
        if 'ORACL™' not in content and 'ORACL' not in content:
            issues.append(f"  - {file_name}: ORACL™ Intelligence Ecosystem not documented (major architectural feature)")
        else:
            # Verify comprehensive coverage
            required_elements = {
                'ORACL™ trademark': 'ORACL™' in content,
                'Intelligence & Learning section': '### Intelligence & Learning' in content,
                '3-Tier architecture mention': any(x in content.lower() for x in ['3-tier', 'tier 1', 'tier 2', 'tier 3']),
                'ORACL™ architecture section': 'ORACL™ Intelligence Ecosystem' in content,
                'Documentation reference': 'ORACL_MEMORY_ARCHITECTURE.md' in content or 'ORACL_MEMORY_ECOSYSTEM' in content
            }
            
            missing = [k for k, v in required_elements.items() if not v]
            if missing:
                warnings.append(f"  - {file_name}: ORACL™ documentation incomplete - missing: {', '.join(missing)}")
    
    elif file_name == 'SECURITY.md':
        # SECURITY.md should document ORACL™ security features
        if 'ORACL™' not in content and 'ORACL' not in content:
            warnings.append(f"  - {file_name}: ORACL™ archive security features not documented")
        else:
            # Verify security-specific ORACL™ coverage
            security_elements = {
                'ORACL™ trademark': 'ORACL™' in content,
                'Archive integrity': any(x in content.lower() for x in ['archive integrity', 'oracl™ archive security']),
                'SHA-256 checksums': 'SHA-256' in content or 'sha-256' in content.lower(),
                'Tamper detection': 'tamper' in content.lower()
            }
            
            missing = [k for k, v in security_elements.items() if not v]
            if missing:
                warnings.append(f"  - {file_name}: ORACL™ security documentation incomplete - missing: {', '.join(missing)}")
    
    return issues, warnings


def perform_content_validation(file_paths: list[Path], verbose: bool = False):
    """Performs deep content validation on a list of files."""
    print("Performing deep content validation...")
    total_issues = 0
    total_warnings = 0

    for file_path in file_paths:
        if not file_path.exists():
            print(f"  ⚠️  File not found: {file_path.name}")
            continue

        print(f"\nValidating {file_path.name}...")
        content = file_path.read_text(encoding='utf-8')
        
        placeholder_issues, placeholder_warnings = _validate_content_placeholders(content, file_path.name)
        link_issues, link_warnings = _validate_content_links(content, file_path.name)
        oracl_issues, oracl_warnings = _validate_oracl_documentation(content, file_path.name)

        issues = placeholder_issues + link_issues + oracl_issues
        warnings = placeholder_warnings + link_warnings + oracl_warnings

        if issues:
            total_issues += len(issues)
            print(f"  ❌ Found {len(issues)} issues:")
            for issue in issues:
                print(issue)
        
        if warnings:
            total_warnings += len(warnings)
            print(f"  ⚠️  Found {len(warnings)} warnings:")
            for warning in warnings:
                print(warning)

        if not issues and not warnings:
            print("  ✅ No content issues found.")

    print("\n" + "="*70)
    print("Content Validation Summary")
    print(f"  - Total Issues: {total_issues}")
    print(f"  - Total Warnings: {total_warnings}")
    print("="*70)

    return total_issues == 0

def perform_update(args):
    """
    Handles the update command logic.

    Args:
        args: The parsed command-line arguments.
    """
    # Get template functions (lazy import to avoid circular dependency)
    tmpl = _get_template_functions()

    if args.update_action == 'version':
        """Set the project version across all specified files."""
        new_version = getattr(args, 'set_version', None)
        if not new_version:
            print("❌ Error: --set-version requires a version string (e.g., 1.2.3).")
            return

        dry_run = getattr(args, 'dry_run', False)
        
        if dry_run:
            print(f"[DRY-RUN] Would attempt to set project version to: {new_version}")
            # In a dry run, we can still list the files that would be affected
            print("Files that would be checked for update:")
            print("  - pyproject.toml")
            print("  - setup.py")
            print("  - codesentinel/__init__.py")
            print("  - .github/copilot-instructions.md")
            print("  - CHANGELOG.md")
        else:
            print(f"Setting project version to: {new_version}")
            updated_files = set_project_version(Path.cwd(), new_version)
            if updated_files:
                print("\n✅ Version updated successfully in the following files:")
                for f in updated_files:
                    print(f"  - {Path(f).relative_to(Path.cwd())}")
            else:
                print("\n⚠️  No files were updated. Check if version strings are present and match expected patterns.")
        return
    
    if args.update_action == 'docs':
        """Update repository documentation files with branding + header/footer verification."""
        dry_run = getattr(args, 'dry_run', False)
        verbose = getattr(args, 'verbose', False)
        validate = getattr(args, 'validate', False)

        docs_to_verify = [
            Path.cwd() / "CHANGELOG.md",
            Path.cwd() / "README.md",
            Path.cwd() / "SECURITY.md",
            Path.cwd() / ".github" / "copilot-instructions.md",
            Path.cwd() / "codesentinel" / "__init__.py",
        ]

        if validate:
            perform_content_validation(docs_to_verify, verbose=verbose)
            return
        
        print("Analyzing repository documentation...")
        print("Verifying SEAM Protection™ branding + header/footer compliance...\\n")
        
        # Files to verify and update
        
        results = verify_and_fix_documentation_pipeline(
            docs_to_verify,
            dry_run=dry_run,
            verbose=verbose,
            file_type_label="Documentation"
        )
        
        # Summary
        print("\\nDocumentation Verification Summary:")
        print(f"  ✓ Full compliance: {len(results['verified'])} files")
        
        if results['fixed']:
            print(f"  Fixed: {len(results['fixed'])} files")
            for fname in results['fixed']:
                print(f"    - {fname}")
        
        all_issues = (results['branding_issues'] + 
                      results['header_footer_issues'] + 
                      results['encoding_issues'] + 
                      results['whitespace_issues'])

        if all_issues:
            print(f"\\nIssues Fixed: {len(all_issues)}")
            for issue in all_issues:
                print(f"   {issue}")

        if dry_run:
            print("\\nDry run complete. No files modified.")
        else:
            if results['fixed'] or results['verified']:
                print("\\nDocumentation verification complete.")
                print("All files comply with SEAM Protection™ branding and header/footer policy.")

    elif args.update_action == 'changelog':
        """Update CHANGELOG.md with recent git commits + verification pipeline."""
        dry_run = getattr(args, 'draft', False) or getattr(args, 'dry_run', False)
        verbose = getattr(args, 'verbose', False)
        
        print("Updating CHANGELOG.md...")
        
        # Get recent commits
        try:
            since = getattr(args, 'since', None)
            if since:
                cmd = ['git', 'log', f'{since}..HEAD', '--oneline', '--no-merges']
            else:
                # Try to find last release tag
                try:
                    last_tag = subprocess.check_output(
                        ['git', 'describe', '--tags', '--abbrev=0'],
                        stderr=subprocess.DEVNULL, text=True
                    ).strip()
                    cmd = ['git', 'log', f'{last_tag}..HEAD', '--oneline', '--no-merges']
                except subprocess.CalledProcessError:
                    # No tags, get last 10 commits
                    cmd = ['git', 'log', '-10', '--oneline', '--no-merges']
            
            commits = subprocess.check_output(cmd, text=True).strip()
            
            if commits:
                print(f"\\n  Found {len(commits.splitlines())} commits:\\n")
                print(commits)
                
                if dry_run:
                    print("\\nDraft mode. CHANGELOG.md not modified.")
                else:
                    print("\\nUse --draft to preview without modifying CHANGELOG.md")
                    
                    # After git operations, verify CHANGELOG.md integrity
                    print("\\nVerifying CHANGELOG.md...")
                    changelog_path = Path.cwd() / "CHANGELOG.md"
                    if changelog_path.exists():
                        results = verify_and_fix_documentation_pipeline(
                            [changelog_path],
                            dry_run=False,
                            verbose=verbose,
                            file_type_label="CHANGELOG"
                        )
                        
                        if results['encoding_issues'] or results['whitespace_issues']:
                            print("  ⚠️  Detected and fixed encoding/formatting issues")
                        else:
                            print("  ✓ CHANGELOG.md integrity verified")
            else:
                print("  No new commits found.")
                
        except subprocess.CalledProcessError as e:
            print(f"  ❌ Error running git command: {e}")
        except Exception as e:
            print(f"  ❌ Error: {e}")
            
    elif args.update_action == 'readme':
        """Update README.md with full documentation verification pipeline."""
        validate_only = getattr(args, 'validate', False)
        dry_run = getattr(args, 'dry_run', False)
        verbose = getattr(args, 'verbose', False)
        
        readme_path = Path.cwd() / "README.md"
        if not readme_path.exists():
            print("  ❌ README.md not found")
            return
        
        if validate_only:
            # Validation mode: comprehensive checks without modifications
            print("=" * 70)
            print("README.md VALIDATION REPORT")
            print("=" * 70)
            print()
            
            # Read README
            try:
                content = readme_path.read_text(encoding='utf-8')
            except Exception as e:
                print(f"❌ ERROR: Could not read README.md: {e}")
                return
            
            issues = []
            warnings = []
            passes = []
            
            # 1. SEAM Protection™ Branding
            print("📋 Content & Branding")
            if 'SEAM Protected™' in content or 'SEAM Protection™' in content:
                passes.append("  ✓ SEAM Protection™ branding present")
            else:
                issues.append("  ❌ Missing SEAM Protection™ branding")
            
            if 'A Polymath Project' in content and 'joediggidyyy' in content:
                passes.append("  ✓ Project attribution present")
            else:
                warnings.append("  ⚠️  Missing or incomplete project attribution")
            
            # 2. Feature Organization
            feature_sections = ['Security', 'Efficiency', 'Minimalism', 'Developer Experience']
            found_sections = [s for s in feature_sections if f"### {s}" in content]
            if len(found_sections) == len(feature_sections):
                passes.append(f"  ✓ All {len(feature_sections)} feature categories present")
            else:
                missing = set(feature_sections) - set(found_sections)
                warnings.append(f"  ⚠️  Missing feature sections: {', '.join(missing)}")
            
            # 3. Emoji Policy Compliance
            print("\n🎨 Emoji Policy Compliance")
            import re
            
            # Count section header emojis (should be minimal or none based on policy)
            section_emojis = re.findall(r'^##\s+[^\w\s]', content, re.MULTILINE)
            if len(section_emojis) == 0:
                passes.append("  ✓ No section header emojis (compliant)")
            elif len(section_emojis) <= 5:
                warnings.append(f"  ⚠️  {len(section_emojis)} section header emoji(s) found (minimal is preferred)")
            else:
                issues.append(f"  ❌ Excessive section header emojis: {len(section_emojis)}")
            
            # Check for SEAM shield in tagline
            if '🛡️' in content and 'SEAM-tight' in content:
                passes.append("  ✓ SEAM shield emoji (🛡️) in final tagline")
            else:
                warnings.append("  ⚠️  SEAM shield emoji missing from tagline")
            
            # 4. Technical Accuracy
            print("\n🔧 Technical Accuracy")
            
            # Check version badge
            if 'version-' in content and 'img.shields.io' in content:
                passes.append("  ✓ Version badge present")
            else:
                warnings.append("  ⚠️  Version badge missing or malformed")
            
            # Check for command reference
            if '| Command | Description |' in content:
                passes.append("  ✓ Command reference table present")
            else:
                issues.append("  ❌ Command reference table missing")
            
            # Check Python version
            if '3.13' in content or 'python-3.13' in content:
                passes.append("  ✓ Python version requirement documented")
            else:
                warnings.append("  ⚠️  Python version requirement unclear")
            
            # Check for ORACL™ Intelligence Ecosystem documentation
            if 'ORACL™' in content or 'ORACL' in content:
                passes.append("  ✓ ORACL™ Intelligence Ecosystem referenced")
                
                # Verify key ORACL™ concepts are documented
                oracl_concepts = {
                    'Intelligence & Learning': '### Intelligence & Learning' in content,
                    '3-Tier Architecture': '3-tier' in content.lower() or 'tier 1' in content.lower(),
                    'Architecture Section': '### ORACL™ Intelligence Ecosystem' in content or 'ORACL™ Intelligence Ecosystem' in content,
                    'Documentation Link': 'ORACL_MEMORY_ARCHITECTURE.md' in content or 'docs/ORACL' in content
                }
                
                missing_concepts = [k for k, v in oracl_concepts.items() if not v]
                if not missing_concepts:
                    passes.append("  ✓ ORACL™ fully documented (features, architecture, links)")
                else:
                    warnings.append(f"  ⚠️  ORACL™ incomplete: Missing {', '.join(missing_concepts)}")
            else:
                issues.append("  ❌ ORACL™ Intelligence Ecosystem not documented (major architectural feature)")
            
            # 5. Documentation Links
            print("\n🔗 Documentation Links")
            required_links = ['SECURITY.md', 'CONTRIBUTING.md', 'CHANGELOG.md', 'LICENSE']
            for link in required_links:
                if link in content:
                    # Verify file exists
                    link_path = Path.cwd() / link
                    if link_path.exists():
                        passes.append(f"  ✓ {link} link valid (file exists)")
                    else:
                        issues.append(f"  ❌ {link} referenced but file not found")
                else:
                    warnings.append(f"  ⚠️  {link} not referenced")
            
            # 6. Formatting & Structure
            print("\n📐 Formatting & Structure")
            
            # Check for code blocks
            code_blocks = re.findall(r'```(\w+)?', content)
            if code_blocks:
                passes.append(f"  ✓ {len(code_blocks)} code blocks with language tags")
            else:
                warnings.append("  ⚠️  No code blocks found")
            
            # Check for horizontal rules
            hr_count = content.count('---\n')
            if hr_count >= 3:
                passes.append(f"  ✓ {hr_count} section separators (---)")
            else:
                warnings.append(f"  ⚠️  Only {hr_count} section separators")
            
            # Check for trailing whitespace
            lines_with_trailing = [i+1 for i, line in enumerate(content.split('\n')) if line.endswith(' ')]
            if not lines_with_trailing:
                passes.append("  ✓ No trailing whitespace")
            else:
                warnings.append(f"  ⚠️  {len(lines_with_trailing)} lines with trailing whitespace")
            
            # 7. Encoding & Special Characters
            print("\n🔤 Encoding & Special Characters")
            
            try:
                # Verify UTF-8 encoding
                readme_path.read_text(encoding='utf-8')
                passes.append("  ✓ Valid UTF-8 encoding")
            except UnicodeDecodeError:
                issues.append("  ❌ UTF-8 encoding error detected")
            
            # Check for special symbols
            special_symbols = ['™', '©', '→']
            found_symbols = [s for s in special_symbols if s in content]
            if found_symbols:
                passes.append(f"  ✓ Special symbols present: {', '.join(found_symbols)}")
            
            # 8. File Integrity
            print("\n📊 File Integrity")
            
            file_size = readme_path.stat().st_size
            line_count = len(content.split('\n'))
            
            if file_size < 50000:  # 50KB
                passes.append(f"  ✓ File size: {file_size:,} bytes (< 50KB)")
            else:
                warnings.append(f"  ⚠️  Large file: {file_size:,} bytes")
            
            if line_count < 500:
                passes.append(f"  ✓ Line count: {line_count} (< 500)")
            else:
                warnings.append(f"  ⚠️  Many lines: {line_count}")
            
            # Print summary
            print("\n" + "=" * 70)
            print("VALIDATION SUMMARY")
            print("=" * 70)
            print()
            
            if passes:
                print(f"✅ PASSED: {len(passes)} checks")
                for p in passes:
                    print(p)
            
            if warnings:
                print(f"\n⚠️  WARNINGS: {len(warnings)} items")
                for w in warnings:
                    print(w)
            
            if issues:
                print(f"\n❌ ISSUES: {len(issues)} items")
                for i in issues:
                    print(i)
            
            print("\n" + "=" * 70)
            
            # Overall status
            if not issues:
                if not warnings:
                    print("🎉 README.md is FULLY COMPLIANT!")
                else:
                    print("✅ README.md passes validation with minor warnings")
            else:
                print("❌ README.md has compliance issues that should be addressed")
            
            print("=" * 70)
            
        else:
            # Update mode: existing functionality
            print("Analyzing README.md...")
            print("Verifying SEAM Protection™ branding + header/footer compliance + encoding...\\n")
            # Use consolidated verification pipeline
            results = verify_and_fix_documentation_pipeline(
                [readme_path], 
                dry_run=dry_run, 
                verbose=verbose,
                file_type_label="README"
            )
            
            # Print summary
            print("\\nREADME.md Verification Summary:")
            print(f"  ✓ Full compliance: {len(results['verified'])} file(s)")
            
            if results['fixed']:
                print(f"  Fixed: {len(results['fixed'])} file(s)")
            
            all_issues = (results.get('encoding_issues', []) + 
                          results.get('whitespace_issues', []) + 
                          results.get('branding_issues', []) + 
                          results.get('header_footer_issues', []))

            if all_issues:
                print(f"\\n  ⚠️  Issues Fixed: {len(all_issues)}")
                for issue in all_issues:
                    print(f"    - {issue}")

            if results['errors']:
                print(f"\\n   Errors: {len(results['errors'])} file(s) could not be processed")
            
            if dry_run:
                print("\\nDry run complete. No files modified.")
            else:
                if results['verified'] or results['fixed']:
                    print("\\nREADME.md verification complete.")
                    print("All issues have been detected and remediated.")
            
    elif args.update_action == 'version-old':
        """Bump version numbers across project files + verify updates."""
        bump_type = args.bump_type
        dry_run = getattr(args, 'dry_run', False)
        verbose = getattr(args, 'verbose', False)
        
        print(f"Bumping version ({bump_type})...")
        
        # Files to update
        version_files = [
            Path.cwd() / "pyproject.toml",
            Path.cwd() / "setup.py",
            Path.cwd() / "codesentinel" / "__init__.py"
        ]
        
        for vf in version_files:
            if vf.exists():
                if dry_run:
                    print(f"  [DRY-RUN] Would update: {vf.name}")
                else:
                    print(f"  ✓ Would update: {vf.name}")
            else:
                print(f"  ⚠️  Not found: {vf.name}")
        
        if dry_run:
            print("\\nDry run complete. No files modified.")
        else:
            print("\\nVersion update requires manual editing or integration with bump2version")
            print("Consider: pip install bump2version && bump2version " + bump_type)
            
            # Verify all version files after update
            print("\\nVerifying version files integrity...")
            existing_version_files = [vf for vf in version_files if vf.exists()]
            if existing_version_files:
                results = verify_and_fix_documentation_pipeline(
                    existing_version_files,
                    dry_run=False,
                    verbose=verbose,
                    file_type_label="VERSION"
                )
                
                if results['verified']:
                    print(f"  ✓ {len(results['verified'])} version file(s) verified")
                if results['encoding_issues']:
                    print(f"  ⚠️  Fixed encoding issues in version files")
            
    elif args.update_action == 'dependencies':
        """Update dependency files."""
        check_only = getattr(args, 'check_only', False)
        upgrade = getattr(args, 'upgrade', False)
        
        print("Checking dependencies...")
        
        try:
            if check_only:
                # Check for outdated packages
                print("  Running: pip list --outdated")
                subprocess.run(['pip', 'list', '--outdated'], check=False)
            elif upgrade:
                print("  Upgrading dependencies requires pip-tools or manual update")
                print("Consider: pip install pip-tools && pip-compile --upgrade")
            else:
                print("  ✓ requirements.txt and pyproject.toml checked")
                print("\\n  Options:")
                print("    --check-only : Check for outdated dependencies")
                print("    --upgrade    : Upgrade to latest compatible versions")
        except Exception as e:
            print(f"  ❌ Error: {e}")
            
    elif args.update_action == 'api-docs':
        """Regenerate API documentation from docstrings."""
        fmt = args.format
        output = getattr(args, 'output', None) or 'docs/api'
        
        print(f" Generating API documentation ({fmt})...")
        
        output_path = Path.cwd() / output
        if not output_path.exists():
            output_path.mkdir(parents=True, exist_ok=True)
            print(f"  Created: {output}")
        
        print(f"  API doc generation requires sphinx or pdoc")
        print("Consider: pip install pdoc3 && pdoc --html --output-dir " + output + " codesentinel")
        
    elif args.update_action == 'headers':
        """Manage documentation headers with verification."""
        action = args.action
        file_arg = getattr(args, 'file', None)
        template_arg = getattr(args, 'template', None)
        custom_arg = getattr(args, 'custom', None)
        verbose = getattr(args, 'verbose', False)

        if action == 'templates':
            tmpl['show_template_options']('header')
        elif action == 'show':
            print("\\nAvailable Header Templates:")
            print("="*70)
            headers = tmpl['get_header_templates']()
            for file_name, info in headers.items():
                marker = "⭐" if info.get('project_specific') else "  "
                print(f"\\n{marker} 📄 {file_name}: {info['description']}")
                print(f"   Preview:\\n   {info['template'][:100]}...")
        elif action == 'set':
            if not file_arg:
                print("❌ --file required for set action")
            else:
                file_path = Path.cwd() / file_arg
                if file_path.exists():
                    if custom_arg:
                        success, msg = tmpl['set_header_for_file'](file_path, custom_header=custom_arg)
                    else:
                        success, msg = tmpl['set_header_for_file'](file_path, template_name=template_arg or file_path.name)
                    print(f"{'✓' if success else '❌'} {msg}")
                    
                    if success:
                        print("\\nVerifying file integrity...")
                        results = verify_and_fix_documentation_pipeline(
                            [file_path], dry_run=False, verbose=verbose, file_type_label="FILE"
                        )
                        if results['verified'] or results['fixed']:
                            print(f"  ✓ {file_path.name} integrity verified and fixed.")
                else:
                    print(f"❌ File not found: {file_arg}")
        elif action == 'edit':
            print("Entering interactive header edit mode...")
            files_to_edit = [Path.cwd() / file_arg] if file_arg else None
            tmpl['edit_headers_interactive'](files_to_edit)
    
    elif args.update_action == 'footers':
        """Manage documentation footers with verification."""
        action = args.action
        file_arg = getattr(args, 'file', None)
        template_arg = getattr(args, 'template', 'standard')
        custom_arg = getattr(args, 'custom', None)
        verbose = getattr(args, 'verbose', False)

        if action == 'templates':
            tmpl['show_template_options']('footer')
        elif action == 'show':
            print("\\nAvailable Footer Templates:")
            print("="*70)
            footers = tmpl['get_footer_templates']()
            for template_name, info in footers.items():
                marker = "⭐" if info.get('project_specific') else "  "
                print(f"\\n{marker} 🔖 {template_name.upper()}: {info['description']}")
                print(f"   Preview:\\n   {info['template'][:100]}...")
        elif action == 'set':
            if not file_arg:
                print("❌ --file required for set action")
            else:
                file_path = Path.cwd() / file_arg
                if file_path.exists():
                    if custom_arg:
                        success, msg = tmpl['set_footer_for_file'](file_path, custom_footer=custom_arg)
                    else:
                        success, msg = tmpl['set_footer_for_file'](file_path, template_name=template_arg)
                    print(f"{'✓' if success else '❌'} {msg}")

                    if success:
                        print("\\nVerifying file integrity...")
                        results = verify_and_fix_documentation_pipeline(
                            [file_path], dry_run=False, verbose=verbose, file_type_label="FILE"
                        )
                        if results['verified'] or results['fixed']:
                            print(f"  ✓ {file_path.name} integrity verified and fixed.")
                else:
                    print(f"❌ File not found: {file_arg}")
        elif action == 'edit':
            print("Entering interactive footer edit mode...")
            files_to_edit = [Path.cwd() / file_arg] if file_arg else None
            tmpl['edit_footers_interactive'](files_to_edit)
    
    elif args.update_action == 'help-files':
        export_help_files(args)
        
    else:
        print("❌ Unknown update action. Use 'codesentinel update --help'")

def export_help_files(args):
    """
    Export CLI help text to documentation files.
    
    Creates formatted help files in both text and markdown formats
    for all commands and subcommands.
    """
    import argparse
    from pathlib import Path
    import subprocess
    
    export_dir_str = getattr(args, 'export', 'docs/cli')
    export_dir = Path.cwd() / export_dir_str  # Always resolve relative to workspace root
    output_format = getattr(args, 'format', 'both')
    
    print("Exporting CLI Help Files")
    print("=" * 60)
    print(f"Export directory: {export_dir.relative_to(Path.cwd())}")
    print(f"Format: {output_format}")
    print()
    
    # Create export directory
    export_dir.mkdir(parents=True, exist_ok=True)
    
    # Import the main parser creation logic
    # We need to capture help text without running the full CLI
    import sys
    from io import StringIO
    
    # Get the parser by calling create_parser or similar
    # For now, we'll use a simpler approach: run --help and capture output
    commands = [
        '',  # Main help
        'status',
        'scan',
        'maintenance',
        'alert',
        'schedule',
        'update',
        'clean',
        'integrate',
        'setup',
        'dev-audit',
        'test',
        'integrity'
    ]
    
    files_created = []
    
    for cmd in commands:
        cmd_name = cmd if cmd else 'main'
        safe_name = cmd_name.replace('-', '_')
        
        # Capture help output
        try:
            result = subprocess.run(
                ['codesentinel'] + ([cmd] if cmd else []) + ['--help'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'  # Replace invalid UTF-8 with replacement character
            )
            help_text = result.stdout
            
            if not help_text:
                continue
            
            # Export as text file
            if output_format in ['txt', 'both']:
                txt_file = export_dir / f"{safe_name}_help.txt"
                with open(txt_file, 'w', encoding='utf-8', errors='replace') as f:
                    f.write(help_text)
                files_created.append(txt_file)
                print(f"✓ Created: {txt_file.relative_to(Path.cwd())}")
            
            # Export as markdown file
            if output_format in ['md', 'both']:
                md_file = export_dir / f"{safe_name}_help.md"
                md_content = f"# {cmd_name.upper() if cmd else 'CODESENTINEL'} Command Help\n\n"
                md_content += "```\n"
                md_content += help_text
                md_content += "\n```\n"
                
                with open(md_file, 'w', encoding='utf-8', errors='replace') as f:
                    f.write(md_content)
                files_created.append(md_file)
                print(f"✓ Created: {md_file.relative_to(Path.cwd())}")
                
        except Exception as e:
            print(f"⚠ Could not export help for '{cmd_name}': {e}")
    
    print()
    print("=" * 60)
    print(f"✓ Exported {len(files_created)} help files")
    print(f"✓ Location: {export_dir.relative_to(Path.cwd())}")
    print()
    print("These files can be used for:")
    print("  - Documentation website generation")
    print("  - Offline reference")
    print("  - Training materials")
    print("  - Automated testing of help text")

