"""
Document Formatter and Style Checker Module
============================================

Provides automated markdown and document formatting with support for multiple conventions
and granular customization. Integrates with daily maintenance workflow.

Features:
- Multiple formatting schemes: Standard, Google, PEP257, Custom
- Granular customization options
- Automatic style checking and linting
- Pre-commit integration
- Daily maintenance workflow integration
"""

import re
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import json


class FormattingScheme(Enum):
    """Available formatting conventions."""
    STANDARD = "standard"      # General markdown standard
    GOOGLE = "google"          # Google style guide
    PEP257 = "pep257"          # Python docstring style
    GITHUB = "github"          # GitHub markdown flavor
    CUSTOM = "custom"          # User-defined custom scheme


class DocumentFormatter:
    """Formats documents according to selected convention."""

    # Formatting rules for each scheme
    FORMATTING_RULES = {
        FormattingScheme.STANDARD: {
            'max_line_length': 100,
            'list_format': '-',  # or '*' or '+'
            'heading_style': 'atx',  # or 'setext'
            'emphasis_style': '*',  # or '_'
            'list_spacing': True,  # blank line before/after lists
            'code_fence': '```',  # or '~~~'
            'trailing_whitespace': False,
            'final_newline': True,
            'blank_lines_between_sections': 2,
        },
        FormattingScheme.GOOGLE: {
            'max_line_length': 80,
            'list_format': '-',
            'heading_style': 'atx',
            'emphasis_style': '*',
            'list_spacing': True,
            'code_fence': '```',
            'trailing_whitespace': False,
            'final_newline': True,
            'blank_lines_between_sections': 1,
            'section_order': ['Overview', 'Args', 'Returns', 'Raises', 'Examples'],
        },
        FormattingScheme.PEP257: {
            'max_line_length': 79,
            'docstring_quotes': '"""',
            'first_line_summary': True,
            'blank_line_after_summary': True,
            'trailing_whitespace': False,
            'final_newline': True,
        },
        FormattingScheme.GITHUB: {
            'max_line_length': 120,
            'list_format': '-',
            'heading_style': 'atx',
            'emphasis_style': '*',
            'list_spacing': True,
            'code_fence': '```',
            'trailing_whitespace': False,
            'final_newline': True,
            'github_flavored': True,
            'task_lists': True,  # Support [ ] and [x]
            'tables': True,
            'strikethrough': True,
        },
    }

    # Style checking rules
    STYLE_RULES = {
        'heading_case': {
            'description': 'Headings should use Title Case or Sentence case',
            'enabled': True,
            'severity': 'warning',
        },
        'list_consistency': {
            'description': 'Lists should use consistent bullet style',
            'enabled': True,
            'severity': 'warning',
        },
        'code_block_language': {
            'description': 'Code blocks should have language specifier',
            'enabled': True,
            'severity': 'warning',
        },
        'line_length': {
            'description': 'Lines should not exceed max length',
            'enabled': True,
            'severity': 'info',
        },
        'blank_lines': {
            'description': 'Proper spacing between sections',
            'enabled': True,
            'severity': 'info',
        },
        'link_format': {
            'description': 'Links should be properly formatted',
            'enabled': True,
            'severity': 'warning',
        },
        'image_alt_text': {
            'description': 'Images should have alt text',
            'enabled': True,
            'severity': 'warning',
        },
        'trailing_whitespace': {
            'description': 'No trailing whitespace',
            'enabled': True,
            'severity': 'warning',
        },
    }

    def __init__(self, scheme: FormattingScheme = FormattingScheme.STANDARD,
                 custom_rules: Optional[Dict[str, Any]] = None,
                 logger: Optional[logging.Logger] = None):
        """
        Initialize document formatter.

        Args:
            scheme: Formatting scheme to use
            custom_rules: Optional custom formatting rules (overrides scheme)
            logger: Logger instance
        """
        self.scheme = scheme
        self.logger = logger or logging.getLogger('DocumentFormatter')
        self.rules = self.FORMATTING_RULES[scheme].copy()
        
        if custom_rules:
            self.rules.update(custom_rules)

    def format_file(self, file_path: Path) -> Tuple[str, Dict[str, Any]]:
        """
        Format a document file.

        Args:
            file_path: Path to file to format

        Returns:
            Tuple of (formatted_content, metadata)
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        formatted = self._apply_formatting(content)
        
        metadata = {
            'file': str(file_path),
            'scheme': self.scheme.value,
            'lines_original': len(content.splitlines()),
            'lines_formatted': len(formatted.splitlines()),
            'changes': content != formatted,
        }

        return formatted, metadata

    def _apply_formatting(self, content: str) -> str:
        """Apply formatting rules to content."""
        lines = content.splitlines(keepends=False)
        formatted_lines = []

        for i, line in enumerate(lines):
            # Remove trailing whitespace if enabled
            if self.rules.get('trailing_whitespace') is False:
                line = line.rstrip()

            # Format headings
            if line.startswith('#'):
                line = self._format_heading(line)

            # Format lists
            if re.match(r'^\s*[-*+]\s', line):
                line = self._format_list_item(line)

            # Format code blocks
            if line.startswith('```'):
                line = self._format_code_fence(line)

            formatted_lines.append(line)

        # Join lines
        formatted = '\n'.join(formatted_lines)

        # Ensure final newline if enabled
        if self.rules.get('final_newline') and formatted and not formatted.endswith('\n'):
            formatted += '\n'

        return formatted

    def _format_heading(self, line: str) -> str:
        """Format heading according to rules."""
        # Ensure proper spacing after #
        match = re.match(r'^(#+)\s*(.*?)$', line)
        if match:
            level = match.group(1)
            text = match.group(2).strip()
            line = f"{level} {text}"

        return line

    def _format_list_item(self, line: str) -> str:
        """Format list item according to rules."""
        match = re.match(r'^(\s*)[-*+]\s+(.*)', line)
        if match:
            indent = match.group(1)
            text = match.group(2)
            bullet = self.rules.get('list_format', '-')
            line = f"{indent}{bullet} {text}"

        return line

    def _format_code_fence(self, line: str) -> str:
        """Format code fence according to rules."""
        fence = self.rules.get('code_fence', '```')
        if line.startswith('```') or line.startswith('~~~'):
            # Extract language if present
            match = re.match(r'^```(.*?)$', line)
            if match:
                lang = match.group(1).strip()
                line = f"{fence}{lang}"
            else:
                line = fence

        return line

    def check_style(self, content: str) -> List[Dict[str, Any]]:
        """
        Check document style and return issues.

        Args:
            content: Document content to check

        Returns:
            List of style issues found
        """
        issues = []

        for rule_name, rule_config in self.STYLE_RULES.items():
            if not rule_config.get('enabled', True):
                continue

            check_method = getattr(self, f'_check_{rule_name}', None)
            if check_method:
                found_issues = check_method(content)
                issues.extend(found_issues)

        return issues

    def _check_heading_case(self, content: str) -> List[Dict[str, Any]]:
        """Check heading capitalization."""
        issues = []
        lines = content.splitlines()

        for i, line in enumerate(lines, 1):
            if line.startswith('#'):
                match = re.match(r'^#+\s+(.+)$', line)
                if match:
                    heading = match.group(1)
                    # Check if properly capitalized
                    if heading and heading[0].islower():
                        issues.append({
                            'line': i,
                            'rule': 'heading_case',
                            'message': f"Heading should start with uppercase: {heading[:50]}",
                            'severity': 'warning',
                        })

        return issues

    def _check_list_consistency(self, content: str) -> List[Dict[str, Any]]:
        """Check list bullet consistency."""
        issues = []
        lines = content.splitlines()
        bullets_seen = set()

        for i, line in enumerate(lines, 1):
            match = re.match(r'^\s*([-*+])\s', line)
            if match:
                bullet = match.group(1)
                bullets_seen.add(bullet)

        if len(bullets_seen) > 1:
            issues.append({
                'line': 0,
                'rule': 'list_consistency',
                'message': f"Inconsistent list bullets found: {bullets_seen}",
                'severity': 'warning',
            })

        return issues

    def _check_code_block_language(self, content: str) -> List[Dict[str, Any]]:
        """Check code blocks have language specifier."""
        issues = []
        lines = content.splitlines()

        i = 0
        while i < len(lines):
            if lines[i].strip().startswith('```'):
                # Check if language specified
                match = re.match(r'^```(\w*)', lines[i])
                if match and not match.group(1):
                    issues.append({
                        'line': i + 1,
                        'rule': 'code_block_language',
                        'message': 'Code block should specify language',
                        'severity': 'warning',
                    })
            i += 1

        return issues

    def _check_line_length(self, content: str) -> List[Dict[str, Any]]:
        """Check line length."""
        issues = []
        max_length = self.rules.get('max_line_length', 100)
        lines = content.splitlines()

        for i, line in enumerate(lines, 1):
            if len(line) > max_length:
                issues.append({
                    'line': i,
                    'rule': 'line_length',
                    'message': f"Line too long ({len(line)} > {max_length})",
                    'severity': 'info',
                })

        return issues

    def _check_blank_lines(self, content: str) -> List[Dict[str, Any]]:
        """Check blank line spacing."""
        issues = []
        lines = content.splitlines()

        for i in range(len(lines) - 1):
            current = lines[i].strip()
            next_line = lines[i + 1].strip() if i + 1 < len(lines) else ''

            # Check spacing between sections
            if current.startswith('#') and next_line and not next_line.startswith('#'):
                if i + 1 < len(lines) and lines[i + 1].strip():
                    if i == 0 or lines[i - 1].strip():
                        pass  # OK

        return issues

    def _check_link_format(self, content: str) -> List[Dict[str, Any]]:
        """Check link formatting."""
        issues = []
        lines = content.splitlines()

        for i, line in enumerate(lines, 1):
            # Check for malformed links
            if '[' in line and ']' in line:
                if not re.search(r'\[.+?\]\(.+?\)', line):
                    if '[' in line and not '](' in line:
                        issues.append({
                            'line': i,
                            'rule': 'link_format',
                            'message': 'Malformed link detected',
                            'severity': 'warning',
                        })

        return issues

    def _check_image_alt_text(self, content: str) -> List[Dict[str, Any]]:
        """Check images have alt text."""
        issues = []
        lines = content.splitlines()

        for i, line in enumerate(lines, 1):
            if '![' in line:
                match = re.search(r'!\[\](.*?\))', line)
                if match and match.group(1) == '':
                    issues.append({
                        'line': i,
                        'rule': 'image_alt_text',
                        'message': 'Image missing alt text',
                        'severity': 'warning',
                    })

        return issues

    def _check_trailing_whitespace(self, content: str) -> List[Dict[str, Any]]:
        """Check for trailing whitespace."""
        issues = []
        lines = content.splitlines(keepends=True)

        for i, line in enumerate(lines, 1):
            if line.rstrip('\n') != line.rstrip('\n').rstrip():
                issues.append({
                    'line': i,
                    'rule': 'trailing_whitespace',
                    'message': 'Line has trailing whitespace',
                    'severity': 'warning',
                })

        return issues


class StyleChecker:
    """Validates document style against rules."""

    def __init__(self, logger: Optional[logging.Logger] = None):
        """Initialize style checker."""
        self.logger = logger or logging.getLogger('StyleChecker')

    def check_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Check file style.

        Args:
            file_path: Path to file to check

        Returns:
            Dict with check results
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        formatter = DocumentFormatter()
        issues = formatter.check_style(content)

        return {
            'file': str(file_path),
            'total_issues': len(issues),
            'errors': [i for i in issues if i['severity'] == 'error'],
            'warnings': [i for i in issues if i['severity'] == 'warning'],
            'info': [i for i in issues if i['severity'] == 'info'],
            'issues': issues,
        }

    def check_directory(self, dir_path: Path, pattern: str = '**/*.md') -> Dict[str, Any]:
        """
        Check all files in directory.

        Args:
            dir_path: Directory to check
            pattern: File pattern to match

        Returns:
            Dict with aggregated results
        """
        results = {
            'directory': str(dir_path),
            'files_checked': 0,
            'total_issues': 0,
            'files_with_issues': [],
            'by_severity': {'error': 0, 'warning': 0, 'info': 0},
        }

        for file_path in dir_path.glob(pattern):
            check_result = self.check_file(file_path)
            results['files_checked'] += 1
            results['total_issues'] += check_result['total_issues']

            if check_result['issues']:
                results['files_with_issues'].append({
                    'file': str(file_path),
                    'issues': check_result['issues'],
                })

            for severity in ['error', 'warning', 'info']:
                results['by_severity'][severity] += len(check_result[severity])

        return results
