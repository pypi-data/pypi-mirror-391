"""
Report Workflow Automation
===========================

Orchestrates report generation and integrates with existing CLI commands.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging
import argparse


# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from codesentinel.utils.config import ConfigManager
from codesentinel.utils.alerts import AlertManager
from tools.codesentinel.report_generator import ReportGenerator


class ReportWorkflow:
    """Manages report generation workflows."""

    def __init__(self):
        """Initialize report workflow."""
        self.logger = self._setup_logging()
        self.workspace_root = Path(__file__).parent.parent.parent

        # Initialize managers
        config_path = self.workspace_root / 'codesentinel.json'
        self.config_manager = ConfigManager(config_path=config_path)
        self.config_manager.load_config()

        self.alert_manager = AlertManager(self.config_manager)
        self.report_generator = ReportGenerator(self.config_manager, self.alert_manager)

    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger('ReportWorkflow')

    def generate_daily_reports(self) -> Dict[str, Any]:
        """Generate all daily reports."""
        self.logger.info("Generating daily reports")
        try:
            reports = self.report_generator.generate_scheduled_reports('daily')
            return {
                'success': True,
                'reports_generated': len(reports),
                'report_paths': reports
            }
        except Exception as e:
            self.logger.error(f"Daily report generation failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def generate_weekly_reports(self) -> Dict[str, Any]:
        """Generate all weekly reports."""
        self.logger.info("Generating weekly reports")
        try:
            reports = self.report_generator.generate_scheduled_reports('weekly')
            return {
                'success': True,
                'reports_generated': len(reports),
                'report_paths': reports
            }
        except Exception as e:
            self.logger.error(f"Weekly report generation failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def generate_biweekly_reports(self) -> Dict[str, Any]:
        """Generate all bi-weekly reports."""
        self.logger.info("Generating bi-weekly reports")
        try:
            reports = self.report_generator.generate_scheduled_reports('biweekly')
            return {
                'success': True,
                'reports_generated': len(reports),
                'report_paths': reports
            }
        except Exception as e:
            self.logger.error(f"Bi-weekly report generation failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def generate_monthly_reports(self) -> Dict[str, Any]:
        """Generate all monthly reports."""
        self.logger.info("Generating monthly reports")
        try:
            reports = self.report_generator.generate_scheduled_reports('monthly')
            return {
                'success': True,
                'reports_generated': len(reports),
                'report_paths': reports
            }
        except Exception as e:
            self.logger.error(f"Monthly report generation failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def generate_single_report(self, report_type: str, **kwargs) -> Dict[str, Any]:
        """
        Generate a single report by type.

        Args:
            report_type: Type of report to generate
            **kwargs: Additional parameters for report generation

        Returns:
            Dict containing generation results
        """
        self.logger.info(f"Generating {report_type} report")
        try:
            report_path = self.report_generator.generate_report(report_type, **kwargs)
            if report_path:
                return {
                    'success': True,
                    'report_path': report_path
                }
            else:
                return {
                    'success': False,
                    'error': 'Report generation returned None'
                }
        except Exception as e:
            self.logger.error(f"{report_type} report generation failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def cleanup_old_reports(self) -> Dict[str, Any]:
        """Clean up old reports according to retention policy."""
        self.logger.info("Cleaning up old reports")
        try:
            self.report_generator.cleanup_old_reports()
            return {
                'success': True,
                'message': 'Old reports cleaned up successfully'
            }
        except Exception as e:
            self.logger.error(f"Report cleanup failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def list_available_reports(self) -> List[str]:
        """List all available report types."""
        config = self.report_generator.reporting_config.get('reports', {})
        return list(config.keys())


def main():
    """Main entry point for report workflow."""
    parser = argparse.ArgumentParser(description='CodeSentinel Report Workflow')
    parser.add_argument('action', choices=['daily', 'weekly', 'biweekly', 'monthly', 'single', 'cleanup', 'list'],
                        help='Action to perform')
    parser.add_argument('--report-type', help='Specific report type to generate (for single action)')
    parser.add_argument('--version', help='Release version (for release reports)')
    parser.add_argument('--feature-name', help='Feature name (for feature reports)')

    args = parser.parse_args()

    workflow = ReportWorkflow()

    if args.action == 'daily':
        result = workflow.generate_daily_reports()
        print(f"Daily reports: {result}")

    elif args.action == 'weekly':
        result = workflow.generate_weekly_reports()
        print(f"Weekly reports: {result}")

    elif args.action == 'biweekly':
        result = workflow.generate_biweekly_reports()
        print(f"Bi-weekly reports: {result}")

    elif args.action == 'monthly':
        result = workflow.generate_monthly_reports()
        print(f"Monthly reports: {result}")

    elif args.action == 'single':
        if not args.report_type:
            print("Error: --report-type required for single report generation")
            sys.exit(1)

        kwargs = {}
        if args.version:
            kwargs['version'] = args.version
        if args.feature_name:
            kwargs['feature_name'] = args.feature_name

        result = workflow.generate_single_report(args.report_type, **kwargs)
        print(f"Single report: {result}")

    elif args.action == 'cleanup':
        result = workflow.cleanup_old_reports()
        print(f"Cleanup: {result}")

    elif args.action == 'list':
        reports = workflow.list_available_reports()
        print("Available report types:")
        for report in reports:
            print(f"  - {report}")


if __name__ == '__main__':
    main()
