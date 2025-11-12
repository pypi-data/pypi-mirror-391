#!/usr/bin/env python3
"""
CodeSentinel Version Verification Script
========================================

A Polymath Project | Created by joediggidyyy

This script performs comprehensive version verification across all version declaration
points in the CodeSentinel codebase. It is designed to be integrated into packaging
and publication workflows with redundant checking at multiple stages.

Usage:
    python tools/verify_version.py [--strict] [--quiet]

Options:
    --strict    Exit with error code 1 if any version mismatches are found
    --quiet     Suppress informational output, only show errors/warnings

Exit Codes:
    0 - All versions match (success)
    1 - Version mismatches found (failure, when --strict is used)
    2 - File reading/parsing errors
"""

import sys
import re
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class VersionVerifier:
    """Comprehensive version verification across CodeSentinel codebase."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.versions_found: Dict[str, List[str]] = {}
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def extract_version_from_file(self, file_path: Path, patterns: List[str]) -> Optional[str]:
        """Extract version from a file using regex patterns."""
        try:
            content = file_path.read_text(encoding='utf-8')
            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    # Return the first match (should be the primary version declaration)
                    return matches[0].strip('"\'')
        except Exception as e:
            self.errors.append(f"Error reading {file_path}: {e}")
        return None

    def check_setup_py(self) -> Optional[str]:
        """Check version in setup.py."""
        setup_py = self.project_root / "setup.py"
        patterns = [
            r'version\s*=\s*["\']([^"\']+)["\']',
            r'version="([^"]+)"',
            r"version='([^']+)'"
        ]
        return self.extract_version_from_file(setup_py, patterns)

    def check_pyproject_toml(self) -> Optional[str]:
        """Check version in pyproject.toml."""
        pyproject_toml = self.project_root / "pyproject.toml"
        patterns = [
            r'version\s*=\s*["\']([^"\']+)["\']',
            r'^version\s*=\s*["\']([^"\']+)["\']'
        ]
        return self.extract_version_from_file(pyproject_toml, patterns)

    def check_init_py(self) -> Optional[str]:
        """Check version in codesentinel/__init__.py."""
        init_py = self.project_root / "codesentinel" / "__init__.py"
        patterns = [
            r'__version__\s*=\s*["\']([^"\']+)["\']',
            r'^__version__\s*=\s*["\']([^"\']+)["\']'
        ]
        return self.extract_version_from_file(init_py, patterns)

    def check_readme_md(self) -> Optional[str]:
        """Check version references in README.md."""
        readme_md = self.project_root / "README.md"
        patterns = [
            r'version:\s*([0-9]+\.[0-9]+\.[0-9]+(?:\.[a-zA-Z0-9]+)?)',
            r'v([0-9]+\.[0-9]+\.[0-9]+(?:\.[a-zA-Z0-9]+)?)',
            r'([0-9]+\.[0-9]+\.[0-9]+(?:\.[a-zA-Z0-9]+)?):\s*PyPI'
        ]
        version = self.extract_version_from_file(readme_md, patterns)
        if version and version.startswith('v'):
            version = version[1:]  # Remove 'v' prefix for consistency
        return version

    def check_changelog_md(self) -> Optional[str]:
        """Check latest version in CHANGELOG.md."""
        changelog_md = self.project_root / "CHANGELOG.md"
        patterns = [
            r'#+\s*v?([0-9]+\.[0-9]+\.[0-9]+(?:\.[a-zA-Z0-9]+)?)',
            r'Version\s*v?([0-9]+\.[0-9]+\.[0-9]+(?:\.[a-zA-Z0-9]+)?)',
            r'##\s*\[?v?([0-9]+\.[0-9]+\.[0-9]+(?:\.[a-zA-Z0-9]+)?)\]?'
        ]
        version = self.extract_version_from_file(changelog_md, patterns)
        if version and version.startswith('v'):
            version = version[1:]  # Remove 'v' prefix for consistency
        return version

    def check_security_md(self) -> Optional[str]:
        """Check supported version in SECURITY.md (major.minor format)."""
        security_md = self.project_root / "SECURITY.md"
        patterns = [
            r'\|\s*([0-9]+\.[0-9]+)\.[xX]\s*\|',  # Table format with .x
            r'Version\s*([0-9]+\.[0-9]+)',
        ]
        version = self.extract_version_from_file(security_md, patterns)
        # SECURITY.md uses major.minor format, so we'll mark it with .x for comparison
        return f"{version}.x" if version else None

    def verify_all_versions(self) -> bool:
        """Verify all version declarations match."""
        # Check all version sources
        version_sources = {
            'setup.py': self.check_setup_py(),
            'pyproject.toml': self.check_pyproject_toml(),
            'codesentinel/__init__.py': self.check_init_py(),
            'README.md': self.check_readme_md(),
            'CHANGELOG.md': self.check_changelog_md(),
            'SECURITY.md': self.check_security_md()
        }

        # Collect all found versions
        for source, version in version_sources.items():
            if version:
                if version not in self.versions_found:
                    self.versions_found[version] = []
                self.versions_found[version].append(source)

        # Handle SECURITY.md special case (major.minor.x format)
        # We need to check if SECURITY.md's major.minor matches the canonical version
        canonical_version = None
        security_version = version_sources.get('SECURITY.md')
        
        # Find the canonical version (most common full version)
        full_versions = {v: sources for v, sources in self.versions_found.items() if not v.endswith('.x')}
        if full_versions:
            # Get the version with the most sources
            canonical_version = max(full_versions.items(), key=lambda x: len(x[1]))[0]
            
            # Check if SECURITY.md matches canonical version's major.minor
            if security_version:
                canonical_major_minor = '.'.join(canonical_version.split('.')[:2])
                security_major_minor = security_version.replace('.x', '')
                
                if canonical_major_minor == security_major_minor:
                    # SECURITY.md matches, add it to canonical version sources
                    if canonical_version in self.versions_found:
                        self.versions_found[canonical_version].append('SECURITY.md (major.minor)')
                    # Remove the .x version entry
                    if security_version in self.versions_found:
                        del self.versions_found[security_version]
                else:
                    self.warnings.append(
                        f"SECURITY.md version {security_major_minor}.x doesn't match "
                        f"canonical {canonical_major_minor}.x"
                    )

        # Check for consistency
        if len(self.versions_found) > 1:
            self.errors.append("Version mismatch detected!")
            for version, sources in self.versions_found.items():
                self.errors.append(f"  {version}: {', '.join(sources)}")
            return False
        elif len(self.versions_found) == 0:
            self.errors.append("No version declarations found!")
            return False
        else:
            # All versions match
            version = list(self.versions_found.keys())[0]
            sources = self.versions_found[version]
            if len(sources) < len(version_sources):
                missing_sources = [s for s in version_sources.keys() if s not in sources and not s.endswith('(major.minor)')]
                if missing_sources:
                    self.warnings.append(f"Version {version} found in {len(sources)}/{len(version_sources)} sources")
                    self.warnings.append(f"Missing from: {', '.join(missing_sources)}")
            return True

    def get_canonical_version(self) -> Optional[str]:
        """Get the canonical version (from primary sources)."""
        if self.versions_found:
            return list(self.versions_found.keys())[0]
        return None


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Verify version consistency across CodeSentinel codebase")
    parser.add_argument('--strict', action='store_true', help='Exit with error code 1 if mismatches found')
    parser.add_argument('--quiet', action='store_true', help='Suppress informational output')
    args = parser.parse_args()

    # Determine project root
    script_dir = Path(__file__).parent
    if (script_dir / "verify_version.py").exists():
        # Running from tools/ directory
        project_root = script_dir.parent
    else:
        # Running from project root
        project_root = script_dir

    verifier = VersionVerifier(project_root)

    if not args.quiet:
        print("[VERIFY] CodeSentinel Version Verification")
        print("=" * 40)

    # Perform verification
    versions_match = verifier.verify_all_versions()

    # Report results
    if verifier.errors:
        if not args.quiet:
            print("[FAIL] ERRORS:")
        for error in verifier.errors:
            print(f"   {error}")

    if verifier.warnings:
        if not args.quiet:
            print("[WARN] WARNINGS:")
        for warning in verifier.warnings:
            print(f"   {warning}")

    if versions_match and not verifier.errors:
        canonical_version = verifier.get_canonical_version()
        if canonical_version and not args.quiet:
            print("[OK] SUCCESS: All version declarations are consistent")
            print(f"   Canonical version: {canonical_version}")
            sources = verifier.versions_found[canonical_version]
            print(f"   Found in {len(sources)} sources: {', '.join(sources)}")
        return 0
    else:
        if args.strict:
            if not args.quiet:
                print("[STRICT] STRICT MODE: Exiting with error code due to version inconsistencies")
            return 1
        else:
            if not args.quiet:
                print("[WARN] NON-STRICT MODE: Version issues found but continuing")
            return 0


if __name__ == "__main__":
    sys.exit(main())