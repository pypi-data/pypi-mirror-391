"""
Document Formatting Command-Line Interface
===========================================

Complete CLI for document formatting, style checking, and configuration.
Integrates with setup pipeline and daily maintenance.
"""

import argparse
import sys
import json
import logging
from pathlib import Path
from typing import Optional
import os

from codesentinel.utils.document_formatter import (
    DocumentFormatter,
    StyleChecker,
    FormattingScheme,
)


class FormattingCLI:
    """Command-line interface for document formatting operations."""

    def __init__(self):
        """Initialize CLI."""
        self.logger = self._setup_logging()

    def _setup_logging(self) -> logging.Logger:
        """Setup logging."""
        logger = logging.getLogger('FormattingCLI')
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        return logger

    def format_file(self, file_path: str, scheme: str, custom_rules: Optional[dict] = None,
                   dry_run: bool = False, write: bool = False) -> int:
        """
        Format a single file.

        Args:
            file_path: Path to file to format
            scheme: Formatting scheme
            custom_rules: Custom formatting rules
            dry_run: Show changes without applying
            write: Write changes to file

        Returns:
            Exit code
        """
        try:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                self.logger.error(f"File not found: {file_path}")
                return 1

            # Parse scheme
            try:
                formatting_scheme = FormattingScheme(scheme)
            except ValueError:
                self.logger.error(f"Invalid scheme: {scheme}")
                return 1

            # Create formatter
            formatter = DocumentFormatter(formatting_scheme, custom_rules, self.logger)

            # Format file
            formatted_content, metadata = formatter.format_file(file_path_obj)

            # Display results
            print(f"\n{'='*60}")
            print(f"File: {file_path}")
            print(f"Scheme: {scheme}")
            print(f"Status: {'Modified' if metadata['changes'] else 'No changes'}")
            print(f"Lines: {metadata['lines_original']} → {metadata['lines_formatted']}")
            print(f"{'='*60}\n")

            if metadata['changes']:
                if dry_run:
                    print("DRY RUN - Changes NOT applied")
                    print("\nPreview of changes:")
                    print("-" * 60)
                    print(formatted_content[:500])
                    if len(formatted_content) > 500:
                        print(f"\n... ({len(formatted_content) - 500} more characters)")
                    print("-" * 60)

                elif write:
                    with open(file_path_obj, 'w', encoding='utf-8') as f:
                        f.write(formatted_content)
                    self.logger.info(f"File formatted and written: {file_path}")
                    print("✓ Changes applied to file")

                else:
                    print("Use --write to apply changes or --dry-run for preview")

            return 0

        except Exception as e:
            self.logger.error(f"Format error: {e}")
            return 1

    def format_directory(self, dir_path: str, scheme: str, pattern: str = '**/*.md',
                        custom_rules: Optional[dict] = None, dry_run: bool = False,
                        write: bool = False) -> int:
        """
        Format all files in directory.

        Args:
            dir_path: Directory path
            scheme: Formatting scheme
            pattern: File glob pattern
            custom_rules: Custom formatting rules
            dry_run: Show changes without applying
            write: Write changes to files

        Returns:
            Exit code
        """
        try:
            dir_path_obj = Path(dir_path)
            if not dir_path_obj.exists():
                self.logger.error(f"Directory not found: {dir_path}")
                return 1

            # Parse scheme
            try:
                formatting_scheme = FormattingScheme(scheme)
            except ValueError:
                self.logger.error(f"Invalid scheme: {scheme}")
                return 1

            # Find matching files
            matching_files = list(dir_path_obj.glob(pattern))
            if not matching_files:
                self.logger.warning(f"No files matching pattern: {pattern}")
                return 0

            self.logger.info(f"Found {len(matching_files)} files to format")

            # Create formatter
            formatter = DocumentFormatter(formatting_scheme, custom_rules, self.logger)

            # Format each file
            results = {
                'total': len(matching_files),
                'modified': 0,
                'unchanged': 0,
                'errors': 0,
                'files': [],
            }

            for file_path in matching_files:
                try:
                    formatted_content, metadata = formatter.format_file(file_path)

                    file_result = {
                        'file': str(file_path),
                        'modified': metadata['changes'],
                        'lines_before': metadata['lines_original'],
                        'lines_after': metadata['lines_formatted'],
                    }

                    if metadata['changes']:
                        results['modified'] += 1
                        if write:
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(formatted_content)
                            file_result['status'] = 'formatted'
                        else:
                            file_result['status'] = 'would be formatted'
                    else:
                        results['unchanged'] += 1
                        file_result['status'] = 'unchanged'

                    results['files'].append(file_result)

                except Exception as e:
                    self.logger.error(f"Error formatting {file_path}: {e}")
                    results['errors'] += 1

            # Print summary
            print(f"\n{'='*60}")
            print(f"Formatting Summary")
            print(f"{'='*60}")
            print(f"Directory: {dir_path}")
            print(f"Scheme: {scheme}")
            print(f"Pattern: {pattern}")
            print(f"Total files: {results['total']}")
            print(f"Modified: {results['modified']}")
            print(f"Unchanged: {results['unchanged']}")
            print(f"Errors: {results['errors']}")
            print(f"{'='*60}\n")

            if dry_run:
                print("DRY RUN - No changes applied\n")

            return 0 if results['errors'] == 0 else 1

        except Exception as e:
            self.logger.error(f"Directory format error: {e}")
            return 1

    def check_file(self, file_path: str) -> int:
        """
        Check file style.

        Args:
            file_path: Path to file to check

        Returns:
            Exit code
        """
        try:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                self.logger.error(f"File not found: {file_path}")
                return 1

            # Create style checker
            checker = StyleChecker(self.logger)

            # Check file
            result = checker.check_file(file_path_obj)

            # Print results
            print(f"\n{'='*60}")
            print(f"Style Check Results")
            print(f"{'='*60}")
            print(f"File: {file_path}")
            print(f"Total issues: {result['total_issues']}")
            print(f"Errors: {len(result['errors'])}")
            print(f"Warnings: {len(result['warnings'])}")
            print(f"Info: {len(result['info'])}")

            if result['issues']:
                print(f"\nIssues:")
                for issue in result['issues']:
                    severity = issue['severity'].upper()
                    line = issue['line']
                    message = issue['message']
                    print(f"  [{severity}] Line {line}: {message}")

            print(f"{'='*60}\n")

            return 0 if len(result['errors']) == 0 else 1

        except Exception as e:
            self.logger.error(f"Style check error: {e}")
            return 1

    def check_directory(self, dir_path: str, pattern: str = '**/*.md') -> int:
        """
        Check directory style.

        Args:
            dir_path: Directory path
            pattern: File glob pattern

        Returns:
            Exit code
        """
        try:
            dir_path_obj = Path(dir_path)
            if not dir_path_obj.exists():
                self.logger.error(f"Directory not found: {dir_path}")
                return 1

            # Create style checker
            checker = StyleChecker(self.logger)

            # Check directory
            result = checker.check_directory(dir_path_obj, pattern)

            # Print summary
            print(f"\n{'='*60}")
            print(f"Directory Style Check Summary")
            print(f"{'='*60}")
            print(f"Directory: {dir_path}")
            print(f"Pattern: {pattern}")
            print(f"Files checked: {result['files_checked']}")
            print(f"Total issues: {result['total_issues']}")
            print(f"Errors: {result['by_severity']['error']}")
            print(f"Warnings: {result['by_severity']['warning']}")
            print(f"Info: {result['by_severity']['info']}")

            if result['files_with_issues']:
                print(f"\nFiles with issues:")
                for file_info in result['files_with_issues']:
                    print(f"  {Path(file_info['file']).name}: {len(file_info['issues'])} issues")

            print(f"{'='*60}\n")

            return 0 if result['by_severity']['error'] == 0 else 1

        except Exception as e:
            self.logger.error(f"Directory check error: {e}")
            return 1

    def show_schemes(self) -> int:
        """Show available formatting schemes."""
        print("\nAvailable Formatting Schemes:")
        print("=" * 60)

        for scheme in FormattingScheme:
            rules = DocumentFormatter.FORMATTING_RULES.get(scheme, {})
            print(f"\n{scheme.value.upper()}")
            print(f"  Max line length: {rules.get('max_line_length', 'N/A')}")
            print(f"  List format: {rules.get('list_format', 'N/A')}")
            print(f"  Heading style: {rules.get('heading_style', 'N/A')}")

        print("\n" + "=" * 60 + "\n")
        return 0

    def list_rules(self) -> int:
        """List available style rules."""
        print("\nAvailable Style Rules:")
        print("=" * 60)

        formatter = DocumentFormatter()
        for rule_name, rule_config in formatter.STYLE_RULES.items():
            status = "✓ Enabled" if rule_config.get('enabled') else " Disabled"
            severity = rule_config.get('severity', 'N/A')
            desc = rule_config['description']

            print(f"\n{rule_name}")
            print(f"  Status: {status}")
            print(f"  Severity: {severity}")
            print(f"  Description: {desc}")

        print("\n" + "=" * 60 + "\n")
        return 0


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser."""
    parser = argparse.ArgumentParser(
        description='CodeSentinel Document Formatting Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Format a single file with preview
  %(prog)s format docs/README.md --scheme standard --dry-run
  
  # Format all markdown files and write changes
  %(prog)s format-dir docs --scheme google --write
  
  # Check style of a file
  %(prog)s check docs/README.md
  
  # Check all markdown files
  %(prog)s check-dir docs --pattern '**/*.md'
  
  # Show available schemes
  %(prog)s schemes
        """
    )

    # Subparsers for commands
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # format command
    format_parser = subparsers.add_parser('format', help='Format a single file')
    format_parser.add_argument('file', help='File to format')
    format_parser.add_argument('--scheme', default='standard', choices=[s.value for s in FormattingScheme],
                               help='Formatting scheme (default: standard)')
    format_parser.add_argument('--dry-run', action='store_true', help='Show changes without applying')
    format_parser.add_argument('--write', '-w', action='store_true', help='Write formatted content to file')
    format_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    # format-dir command
    format_dir_parser = subparsers.add_parser('format-dir', help='Format all files in directory')
    format_dir_parser.add_argument('directory', help='Directory to format')
    format_dir_parser.add_argument('--scheme', default='standard', choices=[s.value for s in FormattingScheme],
                                   help='Formatting scheme (default: standard)')
    format_dir_parser.add_argument('--pattern', default='**/*.md', help='File pattern (default: **/*.md)')
    format_dir_parser.add_argument('--dry-run', action='store_true', help='Show changes without applying')
    format_dir_parser.add_argument('--write', '-w', action='store_true', help='Write formatted content to files')
    format_dir_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    # check command
    check_parser = subparsers.add_parser('check', help='Check file style')
    check_parser.add_argument('file', help='File to check')
    check_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    # check-dir command
    check_dir_parser = subparsers.add_parser('check-dir', help='Check directory style')
    check_dir_parser.add_argument('directory', help='Directory to check')
    check_dir_parser.add_argument('--pattern', default='**/*.md', help='File pattern (default: **/*.md)')
    check_dir_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    # schemes command
    subparsers.add_parser('schemes', help='Show available formatting schemes')

    # rules command
    subparsers.add_parser('rules', help='Show available style rules')

    # gui command
    gui_parser = subparsers.add_parser('gui', help='Open configuration GUI')
    gui_parser.add_argument('--save-path', default='codesentinel.json',
                            help='Path to save configuration (default: codesentinel.json)')

    return parser


def main():
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    cli = FormattingCLI()

    # Setup verbose logging
    if hasattr(args, 'verbose') and args.verbose:
        cli.logger.setLevel(logging.DEBUG)

    # Execute command
    if args.command == 'format':
        return cli.format_file(args.file, args.scheme, dry_run=args.dry_run, write=args.write)

    elif args.command == 'format-dir':
        return cli.format_directory(
            args.directory, args.scheme, args.pattern,
            dry_run=args.dry_run, write=args.write
        )

    elif args.command == 'check':
        return cli.check_file(args.file)

    elif args.command == 'check-dir':
        return cli.check_directory(args.directory, args.pattern)

    elif args.command == 'schemes':
        return cli.show_schemes()

    elif args.command == 'rules':
        return cli.list_rules()

    elif args.command == 'gui':
        try:
            import tkinter as tk
            from codesentinel.gui.formatting_config import open_formatting_config_gui

            root = tk.Tk()

            def on_save(config):
                # Save configuration
                config_path = Path(args.save_path)
                with open(config_path, 'w') as f:
                    json.dump(config, f, indent=2)
                print(f"Configuration saved to: {config_path}")

            window = open_formatting_config_gui(root, on_save=on_save)
            root.mainloop()
            return 0

        except ImportError:
            print("Error: tkinter not available. Cannot open GUI.")
            return 1

    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())
