"""
Maintenance Scheduler
=====================

Handles scheduling and execution of automated maintenance tasks.
"""

import json
import logging
import time
import os
import sys
import subprocess
import psutil
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, Callable
import threading

try:
    import schedule
    SCHEDULE_AVAILABLE = True
except ImportError:
    schedule = None
    SCHEDULE_AVAILABLE = False

# State file location
STATE_FILE = Path.home() / ".codesentinel" / "scheduler.state"


class MaintenanceScheduler:
    """Schedules and executes automated maintenance tasks."""

    def __init__(self, config_manager, alert_manager):
        """
        Initialize maintenance scheduler.

        Args:
            config_manager: Configuration manager instance.
            alert_manager: Alert manager instance.
        """
        self.config_manager = config_manager
        self.alert_manager = alert_manager
        self.logger = logging.getLogger('MaintenanceScheduler')
        self.scheduler_thread = None
        self.running = False

        if not SCHEDULE_AVAILABLE:
            self.logger.warning("schedule library not available - scheduling features disabled")

        # Initialize report generator
        try:
            from tools.codesentinel.report_generator import ReportGenerator
            self.report_generator = ReportGenerator(config_manager, alert_manager)
            self.logger.info("Report generator initialized")
        except ImportError as e:
            self.logger.warning(f"Report generator not available: {e}")
            self.report_generator = None

        # Task registry
        self.tasks = {
            'daily': self._run_daily_tasks,
            'weekly': self._run_weekly_tasks,
            'biweekly': self._run_biweekly_tasks,
            'monthly': self._run_monthly_tasks
        }

    def _save_state(self, active: bool, pid: Optional[int] = None):
        """Save scheduler state to file."""
        try:
            STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
            state = {
                'active': active,
                'pid': pid or os.getpid(),
                'timestamp': datetime.now().isoformat()
            }
            with open(STATE_FILE, 'w') as f:
                json.dump(state, f)
        except Exception as e:
            self.logger.warning(f"Failed to save scheduler state: {e}")

    def _load_state(self) -> Dict[str, Any]:
        """Load scheduler state from file."""
        try:
            if STATE_FILE.exists():
                with open(STATE_FILE, 'r') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.warning(f"Failed to load scheduler state: {e}")
        return {}

    def _clear_state(self):
        """Clear scheduler state file."""
        try:
            if STATE_FILE.exists():
                STATE_FILE.unlink()
        except Exception as e:
            self.logger.warning(f"Failed to clear scheduler state: {e}")

    def start(self):
        """Start the maintenance scheduler."""
        if self.running:
            self.logger.warning("Scheduler is already running")
            return

        self.running = True
        # Use daemon thread for in-process scheduling
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        # Save state with current PID
        self._save_state(active=True)

        self.logger.info("Maintenance scheduler started")

    def stop(self):
        """Stop the maintenance scheduler."""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        
        # Clear state file
        self._clear_state()
        
        self.logger.info("Maintenance scheduler stopped")

    def is_active(self) -> bool:
        """Check if scheduler is active."""
        # Check in-process thread status first
        if self.running and self.scheduler_thread and self.scheduler_thread.is_alive():
            return True
        
        # Check persisted state from state file
        state = self._load_state()
        if state.get('active'):
            pid = state.get('pid')
            # Verify the process is still running
            if pid:
                try:
                    process = psutil.Process(pid)
                    # Check if it's a Python process (scheduler should be Python)
                    if process.is_running() and 'python' in process.name().lower():
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    # Process no longer exists, clear stale state
                    self._clear_state()
        
        return False

    def _run_scheduler(self):
        """Run the scheduler loop."""
        if not SCHEDULE_AVAILABLE:
            self.logger.error("Cannot run scheduler - schedule library not available")
            return

        # Clear existing jobs
        schedule.clear()  # type: ignore

        # Setup scheduled tasks
        self._setup_scheduled_tasks()

        # Run scheduler loop
        while self.running:
            try:
                schedule.run_pending()  # type: ignore
                time.sleep(60)  # Check every minute
            except Exception as e:
                self.logger.error(f"Scheduler error: {e}")
                time.sleep(300)  # Wait 5 minutes on error

    def _setup_scheduled_tasks(self):
        """Setup scheduled maintenance tasks."""
        if not SCHEDULE_AVAILABLE:
            self.logger.warning("Cannot setup scheduled tasks - schedule library not available")
            return

        maintenance_config = self.config_manager.get('maintenance', {})

        # Daily tasks
        if maintenance_config.get('daily', {}).get('enabled', False):
            schedule_time = maintenance_config['daily'].get('schedule', '09:00')
            try:
                hour, minute = map(int, schedule_time.split(':'))
                schedule.every().day.at(f"{hour:02d}:{minute:02d}").do(  # type: ignore
                    self._execute_task, 'daily'
                )
                self.logger.info(f"Scheduled daily tasks for {schedule_time}")
            except (ValueError, AttributeError) as e:
                self.logger.error(f"Invalid daily schedule time '{schedule_time}': {e}")

        # Weekly tasks
        if maintenance_config.get('weekly', {}).get('enabled', False):
            schedule_str = maintenance_config['weekly'].get('schedule', 'Monday 10:00')
            try:
                day, time_str = schedule_str.split(' ', 1)
                hour, minute = map(int, time_str.split(':'))

                day_map = {
                    'monday': schedule.every().monday,  # type: ignore
                    'tuesday': schedule.every().tuesday,  # type: ignore
                    'wednesday': schedule.every().wednesday,  # type: ignore
                    'thursday': schedule.every().thursday,  # type: ignore
                    'friday': schedule.every().friday,  # type: ignore
                    'saturday': schedule.every().saturday,  # type: ignore
                    'sunday': schedule.every().sunday  # type: ignore
                }

                if day.lower() in day_map:
                    day_map[day.lower()].at(f"{hour:02d}:{minute:02d}").do(
                        self._execute_task, 'weekly'
                    )
                    self.logger.info(f"Scheduled weekly tasks for {schedule_str}")
                else:
                    self.logger.error(f"Invalid day '{day}' in weekly schedule")

            except (ValueError, AttributeError) as e:
                self.logger.error(f"Invalid weekly schedule '{schedule_str}': {e}")

        # Bi-weekly tasks
        if maintenance_config.get('biweekly', {}).get('enabled', False):
            schedule_str = maintenance_config['biweekly'].get('schedule', 'Friday 17:00')
            try:
                day, time_str = schedule_str.split(' ', 1)
                hour, minute = map(int, time_str.split(':'))

                day_map = {
                    'monday': schedule.every(2).weeks.monday,  # type: ignore
                    'tuesday': schedule.every(2).weeks.tuesday,  # type: ignore
                    'wednesday': schedule.every(2).weeks.wednesday,  # type: ignore
                    'thursday': schedule.every(2).weeks.thursday,  # type: ignore
                    'friday': schedule.every(2).weeks.friday,  # type: ignore
                    'saturday': schedule.every(2).weeks.saturday,  # type: ignore
                    'sunday': schedule.every(2).weeks.sunday  # type: ignore
                }

                if day.lower() in day_map:
                    day_map[day.lower()].at(f"{hour:02d}:{minute:02d}").do(
                        self._execute_task, 'biweekly'
                    )
                    self.logger.info(f"Scheduled bi-weekly tasks for {schedule_str}")
                else:
                    self.logger.error(f"Invalid day '{day}' in bi-weekly schedule")

            except (ValueError, AttributeError) as e:
                self.logger.error(f"Invalid bi-weekly schedule '{schedule_str}': {e}")

        # Monthly tasks
        if maintenance_config.get('monthly', {}).get('enabled', False):
            schedule_str = maintenance_config['monthly'].get('schedule', '1st 11:00')
            try:
                day_str, time_str = schedule_str.split(' ', 1)
                hour, minute = map(int, time_str.split(':'))

                # Parse day (e.g., "1st", "15th", "last")
                if day_str.lower() == 'last':
                    day = 31  # Will be adjusted by scheduler
                else:
                    day = int(day_str.rstrip('stndrh'))

                # Schedule on the specified day of month
                schedule.every().month.at(f"{hour:02d}:{minute:02d}").do(  # type: ignore
                    self._execute_task, 'monthly'
                )
                self.logger.info(f"Scheduled monthly tasks for {schedule_str}")

            except (ValueError, AttributeError) as e:
                self.logger.error(f"Invalid monthly schedule '{schedule_str}': {e}")

    def _execute_task(self, task_type: str):
        """Execute a scheduled task."""
        try:
            self.logger.info(f"Executing scheduled {task_type} maintenance tasks")

            if task_type in self.tasks:
                results = self.tasks[task_type]()

                # Send success alert
                self.alert_manager.send_alert(
                    f"{task_type.capitalize()} Maintenance Completed",
                    f"Successfully executed {len(results.get('tasks_executed', []))} {task_type} maintenance tasks.",
                    severity='info',
                    channels=['console', 'file']
                )

                # Send failure alerts if any
                if results.get('errors'):
                    self.alert_manager.send_alert(
                        f"{task_type.capitalize()} Maintenance Errors",
                        f"Encountered {len(results['errors'])} errors during {task_type} maintenance.",
                        severity='warning',
                        channels=['console', 'file']
                    )

            else:
                self.logger.error(f"Unknown task type: {task_type}")

        except Exception as e:
            self.logger.error(f"Failed to execute {task_type} tasks: {e}")
            self.alert_manager.send_alert(
                f"{task_type.capitalize()} Maintenance Failed",
                f"Critical error during {task_type} maintenance execution: {e}",
                severity='error'
            )

    def run_task_now(self, task_type: str) -> Dict[str, Any]:
        """
        Run maintenance task immediately.

        Args:
            task_type: Type of task to run ('daily', 'weekly', 'monthly').

        Returns:
            Dict containing task results.
        """
        if task_type not in self.tasks:
            raise ValueError(f"Unknown task type: {task_type}")

        self.logger.info(f"Running {task_type} maintenance tasks on demand")
        return self.tasks[task_type]()

    def _run_daily_tasks(self) -> Dict[str, Any]:
        """Run daily maintenance tasks."""
        tasks_executed = []
        errors = []
        
        # Root directory cleanup using CLI clean command
        try:
            repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            os.chdir(repo_root)  # Change to repo root for CLI command

            # Run clean --root command
            result = subprocess.run([
                sys.executable, '-m', 'codesentinel.cli', 'clean', '--root'
            ], capture_output=True, text=True, timeout=300)

            if result.returncode == 0:
                tasks_executed.append('root_directory_cleanup')
                self.logger.info("Root directory cleanup completed successfully")
                # Parse output to get cleanup statistics if needed
                if "Space to reclaim:" in result.stdout:
                    self.logger.info("Cleanup statistics available in CLI output")
            else:
                self.logger.warning(f"Root cleanup failed: {result.stderr}")
                errors.append(f"Root cleanup failed: {result.stderr}")

        except subprocess.TimeoutExpired:
            self.logger.error("Root cleanup timed out")
            errors.append("Root cleanup timed out")
        except Exception as e:
            self.logger.error(f"Root cleanup error: {e}")
            errors.append(f"Root cleanup failed: {str(e)}")
        
        # Python cache cleanup using CLI clean command
        try:
            # Run clean --cache command
            result = subprocess.run([
                sys.executable, '-m', 'codesentinel.cli', 'clean', '--cache'
            ], capture_output=True, text=True, timeout=300)

            if result.returncode == 0:
                tasks_executed.append('python_cache_cleanup')
                self.logger.info("Python cache cleanup completed successfully")
            else:
                self.logger.warning(f"Cache cleanup failed: {result.stderr}")
                errors.append(f"Cache cleanup failed: {result.stderr}")

        except subprocess.TimeoutExpired:
            self.logger.error("Cache cleanup timed out")
            errors.append("Cache cleanup timed out")
        except Exception as e:
            self.logger.error(f"Cache cleanup error: {e}")
            errors.append(f"Cache cleanup failed: {str(e)}")
        
        # Temp files and logs cleanup using CLI clean command
        try:
            # Run clean --temp --logs command
            result = subprocess.run([
                sys.executable, '-m', 'codesentinel.cli', 'clean', '--temp', '--logs'
            ], capture_output=True, text=True, timeout=300)

            if result.returncode == 0:
                tasks_executed.append('temp_logs_cleanup')
                self.logger.info("Temp files and logs cleanup completed successfully")
            else:
                self.logger.warning(f"Temp/logs cleanup failed: {result.stderr}")
                errors.append(f"Temp/logs cleanup failed: {result.stderr}")

        except subprocess.TimeoutExpired:
            self.logger.error("Temp/logs cleanup timed out")
            errors.append("Temp/logs cleanup timed out")
        except Exception as e:
            self.logger.error(f"Temp/logs cleanup error: {e}")
            errors.append(f"Temp/logs cleanup failed: {str(e)}")
        
        # Document formatting and style checking
        try:
            from codesentinel.utils.document_formatter import DocumentFormatter, StyleChecker, FormattingScheme
            import os
            from pathlib import Path
            
            repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            docs_dir = Path(repo_root) / 'docs'
            
            if docs_dir.exists():
                # Check document style
                style_checker = StyleChecker(logger=self.logger)
                check_result = style_checker.check_directory(docs_dir, pattern='**/*.md')
                
                if check_result['total_issues'] > 0:
                    self.logger.info(f"Document style issues found: {check_result['total_issues']}")
                    tasks_executed.append('document_style_check')
                else:
                    tasks_executed.append('document_style_validation')
                    
        except ImportError:
            self.logger.warning("Document formatter not available - skipping")
        except Exception as e:
            self.logger.error(f"Document formatting error: {e}")
            errors.append(f"Document formatting failed: {str(e)}")
        
        # Duplication detection (AI tool bug mitigation)
        try:
            import os
            import re
            from pathlib import Path
            
            repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            duplications_found = []
            
            # Simple inline duplication detector
            duplication_patterns = [
                re.compile(r"^(.+)\1$"),  # texttext on same line
                re.compile(r"^(#\s*.+)#"),  # #comment#comment
            ]
            
            scan_extensions = {'.py', '.md', '.txt', '.json', '.toml', '.ini'}
            
            for file_path in Path(repo_root).iterdir():
                if file_path.is_file() and file_path.suffix in scan_extensions:
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            for line_num, line in enumerate(f, 1):
                                line = line.rstrip()
                                if not line.strip():
                                    continue
                                for pattern in duplication_patterns:
                                    if pattern.match(line):
                                        duplications_found.append({
                                            'file': file_path.name,
                                            'line': line_num
                                        })
                                        break
                    except:
                        pass
            
            if duplications_found:
                self.logger.warning(f"Duplication detected in {len(duplications_found)} locations")
                tasks_executed.append('duplication_detection_alert')
            else:
                tasks_executed.append('duplication_detection_passed')
                
        except Exception as e:
            self.logger.error(f"Duplication detection error: {e}")
            errors.append(f"Duplication detection failed: {str(e)}")
        
        # File duplication detection (AI tool bug mitigation)
        try:
            import re
            import os
            from pathlib import Path
            
            repo_root = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            duplications_found = 0
            
            # Known duplication patterns from AI create_file bug
            patterns = [
                re.compile(r"^(.+)\1$"),  # texttext on same line
                re.compile(r"^(#\s*.+)#"),  # #comment#comment
                re.compile(r"^([\"\'`]{1,3})\1+"),  # """ duplication
            ]
            
            # Scan root directory files
            scan_extensions = {'.py', '.md', '.txt', '.json', '.toml', '.ini', '.yml', '.yaml'}
            for file_path in repo_root.iterdir():
                if file_path.is_file() and file_path.suffix in scan_extensions:
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            for line_num, line in enumerate(f, 1):
                                line = line.rstrip()
                                if not line.strip():
                                    continue
                                for pattern in patterns:
                                    if pattern.match(line):
                                        duplications_found += 1
                                        self.logger.warning(f"Duplication found in {file_path.name}:{line_num}")
                                        break
                    except Exception:
                        pass
            
            if duplications_found > 0:
                self.logger.warning(f"Found {duplications_found} line duplications - AI tool bug detected")
                tasks_executed.append(f'duplication_detection_{duplications_found}_issues')
            else:
                tasks_executed.append('duplication_scan_clean')
                
        except Exception as e:
            self.logger.error(f"Duplication detection error: {e}")
            errors.append(f"Duplication detection failed: {str(e)}")
        
        # Dependency check using CLI update command
        try:
            # Run update --dependencies --check-only command
            result = subprocess.run([
                sys.executable, '-m', 'codesentinel.cli', 'update', 'dependencies', '--check-only'
            ], capture_output=True, text=True, timeout=300)

            if result.returncode == 0:
                tasks_executed.append('dependency_check')
                self.logger.info("Dependency check completed successfully")
            else:
                self.logger.warning(f"Dependency check failed: {result.stderr}")
                errors.append(f"Dependency check failed: {result.stderr}")

        except subprocess.TimeoutExpired:
            self.logger.error("Dependency check timed out")
            errors.append("Dependency check timed out")
        except Exception as e:
            self.logger.error(f"Dependency check error: {e}")
            errors.append(f"Dependency check failed: {str(e)}")
        
        # Emoji policy enforcement using CLI clean command
        try:
            # Run clean --emojis command
            result = subprocess.run([
                sys.executable, '-m', 'codesentinel.cli', 'clean', '--emojis'
            ], capture_output=True, text=True, timeout=300)

            if result.returncode == 0:
                tasks_executed.append('emoji_policy_enforcement')
                self.logger.info("Emoji policy enforcement completed successfully")
            else:
                self.logger.warning(f"Emoji policy enforcement failed: {result.stderr}")
                errors.append(f"Emoji policy enforcement failed: {result.stderr}")

        except subprocess.TimeoutExpired:
            self.logger.error("Emoji policy enforcement timed out")
            errors.append("Emoji policy enforcement timed out")
        except Exception as e:
            self.logger.error(f"Emoji policy enforcement error: {e}")
            errors.append(f"Emoji policy enforcement failed: {str(e)}")
        
        # Standard daily tasks
        tasks_executed.extend(['security_check', 'log_cleanup'])

        # Generate daily reports
        if self.report_generator:
            try:
                daily_reports = self.report_generator.generate_scheduled_reports('daily')
                if daily_reports:
                    tasks_executed.append(f'report_generation_{len(daily_reports)}_reports')
                    self.logger.info(f"Generated {len(daily_reports)} daily reports")
                else:
                    self.logger.warning("No daily reports were generated")
            except Exception as e:
                self.logger.error(f"Daily report generation failed: {e}")
                errors.append(f"Daily report generation failed: {str(e)}")
        
        return {
            'task_type': 'daily',
            'tasks_executed': tasks_executed,
            'errors': errors,
            'warnings': []
        }

    def _run_weekly_tasks(self) -> Dict[str, Any]:
        """Run weekly maintenance tasks."""
        tasks_executed = []
        errors = []
        
        # Change to repo root for CLI commands
        repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        original_cwd = os.getcwd()
        os.chdir(repo_root)
        
        try:
            # Changelog update using CLI update command
            try:
                result = subprocess.run([
                    sys.executable, '-m', 'codesentinel.cli', 'update', 'changelog'
                ], capture_output=True, text=True, timeout=300)

                if result.returncode == 0:
                    tasks_executed.append('changelog_update')
                    self.logger.info("Changelog update completed successfully")
                else:
                    self.logger.warning(f"Changelog update failed: {result.stderr}")
                    errors.append(f"Changelog update failed: {result.stderr}")

            except subprocess.TimeoutExpired:
                self.logger.error("Changelog update timed out")
                errors.append("Changelog update timed out")
            except Exception as e:
                self.logger.error(f"Changelog update error: {e}")
                errors.append(f"Changelog update failed: {str(e)}")
            
            # Build and test artifacts cleanup using CLI clean command
            try:
                result = subprocess.run([
                    sys.executable, '-m', 'codesentinel.cli', 'clean', '--build', '--test'
                ], capture_output=True, text=True, timeout=300)

                if result.returncode == 0:
                    tasks_executed.append('build_test_cleanup')
                    self.logger.info("Build and test artifacts cleanup completed successfully")
                else:
                    self.logger.warning(f"Build/test cleanup failed: {result.stderr}")
                    errors.append(f"Build/test cleanup failed: {result.stderr}")

            except subprocess.TimeoutExpired:
                self.logger.error("Build/test cleanup timed out")
                errors.append("Build/test cleanup timed out")
            except Exception as e:
                self.logger.error(f"Build/test cleanup error: {e}")
                errors.append(f"Build/test cleanup failed: {str(e)}")
            
            # Document update check using CLI update command
            try:
                result = subprocess.run([
                    sys.executable, '-m', 'codesentinel.cli', 'update', 'docs'
                ], capture_output=True, text=True, timeout=300)

                if result.returncode == 0:
                    tasks_executed.append('documentation_check')
                    self.logger.info("Documentation check completed successfully")
                else:
                    self.logger.warning(f"Documentation check failed: {result.stderr}")
                    errors.append(f"Documentation check failed: {result.stderr}")

            except subprocess.TimeoutExpired:
                self.logger.error("Documentation check timed out")
                errors.append("Documentation check timed out")
            except Exception as e:
                self.logger.error(f"Documentation check error: {e}")
                errors.append(f"Documentation check failed: {str(e)}")
        
        finally:
            # Restore original working directory
            os.chdir(original_cwd)

        # Generate weekly reports
        if self.report_generator:
            try:
                weekly_reports = self.report_generator.generate_scheduled_reports('weekly')
                if weekly_reports:
                    tasks_executed.append(f'report_generation_{len(weekly_reports)}_reports')
                    self.logger.info(f"Generated {len(weekly_reports)} weekly reports")
                else:
                    self.logger.warning("No weekly reports were generated")
            except Exception as e:
                self.logger.error(f"Weekly report generation failed: {e}")
                errors.append(f"Weekly report generation failed: {str(e)}")
        
        return {
            'task_type': 'weekly',
            'tasks_executed': tasks_executed,
            'errors': errors,
            'warnings': []
        }

    def _run_biweekly_tasks(self) -> Dict[str, Any]:
        """Run bi-weekly maintenance tasks."""
        tasks_executed = []
        errors = []

        # Change to repo root for CLI commands
        repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        original_cwd = os.getcwd()
        os.chdir(repo_root)

        try:
            # Security audit using CLI audit command
            try:
                result = subprocess.run([
                    sys.executable, '-m', 'codesentinel.cli', 'audit', '--comprehensive'
                ], capture_output=True, text=True, timeout=600)

                if result.returncode == 0:
                    tasks_executed.append('security_audit')
                    self.logger.info("Security audit completed successfully")
                else:
                    self.logger.warning(f"Security audit failed: {result.stderr}")
                    errors.append(f"Security audit failed: {result.stderr}")

            except subprocess.TimeoutExpired:
                self.logger.error("Security audit timed out")
                errors.append("Security audit timed out")
            except Exception as e:
                self.logger.error(f"Security audit error: {e}")
                errors.append(f"Security audit failed: {str(e)}")

            # Efficiency analysis using CLI analyze command
            try:
                result = subprocess.run([
                    sys.executable, '-m', 'codesentinel.cli', 'analyze', '--efficiency'
                ], capture_output=True, text=True, timeout=300)

                if result.returncode == 0:
                    tasks_executed.append('efficiency_analysis')
                    self.logger.info("Efficiency analysis completed successfully")
                else:
                    self.logger.warning(f"Efficiency analysis failed: {result.stderr}")
                    errors.append(f"Efficiency analysis failed: {result.stderr}")

            except subprocess.TimeoutExpired:
                self.logger.error("Efficiency analysis timed out")
                errors.append("Efficiency analysis timed out")
            except Exception as e:
                self.logger.error(f"Efficiency analysis error: {e}")
                errors.append(f"Efficiency analysis failed: {str(e)}")

            # Minimalism compliance check using CLI clean command
            try:
                result = subprocess.run([
                    sys.executable, '-m', 'codesentinel.cli', 'clean', '--archive', '--check-only'
                ], capture_output=True, text=True, timeout=300)

                if result.returncode == 0:
                    tasks_executed.append('minimalism_compliance')
                    self.logger.info("Minimalism compliance check completed successfully")
                else:
                    self.logger.warning(f"Minimalism compliance check failed: {result.stderr}")
                    errors.append(f"Minimalism compliance check failed: {result.stderr}")

            except subprocess.TimeoutExpired:
                self.logger.error("Minimalism compliance check timed out")
                errors.append("Minimalism compliance check timed out")
            except Exception as e:
                self.logger.error(f"Minimalism compliance check error: {e}")
                errors.append(f"Minimalism compliance check failed: {str(e)}")

            # Integration tests using CLI test command
            try:
                result = subprocess.run([
                    sys.executable, '-m', 'codesentinel.cli', 'test', '--integration'
                ], capture_output=True, text=True, timeout=600)

                if result.returncode == 0:
                    tasks_executed.append('integration_tests')
                    self.logger.info("Integration tests completed successfully")
                else:
                    self.logger.warning(f"Integration tests failed: {result.stderr}")
                    errors.append(f"Integration tests failed: {result.stderr}")

            except subprocess.TimeoutExpired:
                self.logger.error("Integration tests timed out")
                errors.append("Integration tests timed out")
            except Exception as e:
                self.logger.error(f"Integration tests error: {e}")
                errors.append(f"Integration tests failed: {str(e)}")

        finally:
            # Restore original working directory
            os.chdir(original_cwd)

        # Generate bi-weekly reports
        if self.report_generator:
            try:
                biweekly_reports = self.report_generator.generate_scheduled_reports('biweekly')
                if biweekly_reports:
                    tasks_executed.append(f'report_generation_{len(biweekly_reports)}_reports')
                    self.logger.info(f"Generated {len(biweekly_reports)} bi-weekly reports")
                else:
                    self.logger.warning("No bi-weekly reports were generated")
            except Exception as e:
                self.logger.error(f"Bi-weekly report generation failed: {e}")
                errors.append(f"Bi-weekly report generation failed: {str(e)}")

        return {
            'task_type': 'biweekly',
            'tasks_executed': tasks_executed,
            'errors': errors,
            'warnings': []
        }

    def _run_monthly_tasks(self) -> Dict[str, Any]:
        """Run monthly maintenance tasks."""
        tasks_executed = []
        errors = []
        
        # Change to repo root for CLI commands
        repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        original_cwd = os.getcwd()
        os.chdir(repo_root)
        
        try:
            # Comprehensive cleanup using CLI clean command
            try:
                result = subprocess.run([
                    sys.executable, '-m', 'codesentinel.cli', 'clean', '--all'
                ], capture_output=True, text=True, timeout=600)  # Longer timeout for comprehensive cleanup

                if result.returncode == 0:
                    tasks_executed.append('comprehensive_cleanup')
                    self.logger.info("Comprehensive cleanup completed successfully")
                else:
                    self.logger.warning(f"Comprehensive cleanup failed: {result.stderr}")
                    errors.append(f"Comprehensive cleanup failed: {result.stderr}")

            except subprocess.TimeoutExpired:
                self.logger.error("Comprehensive cleanup timed out")
                errors.append("Comprehensive cleanup timed out")
            except Exception as e:
                self.logger.error(f"Comprehensive cleanup error: {e}")
                errors.append(f"Comprehensive cleanup failed: {str(e)}")
            
            # Version bump check (dry run) using CLI update command
            try:
                result = subprocess.run([
                    sys.executable, '-m', 'codesentinel.cli', 'update', 'version', 'patch', '--dry-run'
                ], capture_output=True, text=True, timeout=300)

                if result.returncode == 0:
                    tasks_executed.append('version_bump_check')
                    self.logger.info("Version bump check completed successfully")
                else:
                    self.logger.warning(f"Version bump check failed: {result.stderr}")
                    errors.append(f"Version bump check failed: {result.stderr}")

            except subprocess.TimeoutExpired:
                self.logger.error("Version bump check timed out")
                errors.append("Version bump check timed out")
            except Exception as e:
                self.logger.error(f"Version bump check error: {e}")
                errors.append(f"Version bump check failed: {str(e)}")
            
            # README update using CLI update command
            try:
                result = subprocess.run([
                    sys.executable, '-m', 'codesentinel.cli', 'update', 'readme'
                ], capture_output=True, text=True, timeout=300)

                if result.returncode == 0:
                    tasks_executed.append('readme_update')
                    self.logger.info("README update completed successfully")
                else:
                    self.logger.warning(f"README update failed: {result.stderr}")
                    errors.append(f"README update failed: {result.stderr}")

            except subprocess.TimeoutExpired:
                self.logger.error("README update timed out")
                errors.append("README update timed out")
            except Exception as e:
                self.logger.error(f"README update error: {e}")
                errors.append(f"README update failed: {str(e)}")
            
            # Archive compression with mandatory security scanning
            try:
                compression_result = self._compress_quarantine_archive()
                if compression_result['archive_found']:
                    if compression_result['compressed']:
                        tasks_executed.append('archive_compression')
                        self.logger.info(f"Archive compression completed: "
                                       f"{compression_result['archive_size_before']} -> "
                                       f"{compression_result['archive_size_after']} bytes")
                    else:
                        self.logger.info("Archive not yet inactive for compression (< 30 days)")
                    
                    # Report security scan issues if found
                    if compression_result['security_scan_results'].get('suspicious_patterns_found', 0) > 0:
                        msg = (f"Security scan found {compression_result['security_scan_results']['suspicious_patterns_found']} "
                               f"suspicious patterns in archive")
                        self.logger.warning(msg)
                        # Don't add to errors - logged but doesn't fail monthly tasks
                else:
                    self.logger.debug("No quarantine archive found to compress")
                
                # Report any compression issues
                if compression_result['issues']:
                    for issue in compression_result['issues']:
                        self.logger.warning(f"Archive compression issue: {issue}")
                
            except Exception as e:
                self.logger.error(f"Archive compression error: {e}")
                errors.append(f"Archive compression failed: {str(e)}")
        
        finally:
            # Restore original working directory
            os.chdir(original_cwd)
        
        return {
            'task_type': 'monthly',
            'tasks_executed': tasks_executed,
            'errors': errors,
            'warnings': []
        }

    def get_schedule_status(self) -> Dict[str, Any]:
        """
        Get current schedule status.

        Returns:
            Dict containing schedule information.
        """
        maintenance_config = self.config_manager.get('maintenance', {})

        return {
            'scheduler_active': self.is_active(),
            'daily_enabled': maintenance_config.get('daily', {}).get('enabled', False),
            'daily_schedule': maintenance_config.get('daily', {}).get('schedule', 'Not set'),
            'weekly_enabled': maintenance_config.get('weekly', {}).get('enabled', False),
            'weekly_schedule': maintenance_config.get('weekly', {}).get('schedule', 'Not set'),
            'monthly_enabled': maintenance_config.get('monthly', {}).get('enabled', False),
            'monthly_schedule': maintenance_config.get('monthly', {}).get('schedule', 'Not set'),
            'next_daily_run': self._get_next_run_time('daily'),
            'next_weekly_run': self._get_next_run_time('weekly'),
            'next_monthly_run': self._get_next_run_time('monthly')
        }

    def _compress_quarantine_archive(self) -> Dict[str, Any]:
        """
        Compress quarantine_legacy_archive directory if inactive for 30+ days.
        Performs mandatory security scanning before compression.
        
        Returns:
            Dict containing compression results.
        """
        result = {
            'archive_found': False,
            'archive_size_before': 0,
            'archive_size_after': 0,
            'compressed': False,
            'security_scan_results': {},
            'issues': []
        }
        
        try:
            import tarfile
            import hashlib
            
            repo_root = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            archive_dir = repo_root / 'quarantine_legacy_archive'
            
            if not archive_dir.exists():
                self.logger.info("No quarantine_legacy_archive directory found")
                return result
            
            result['archive_found'] = True
            
            # Calculate current size
            def get_dir_size(path):
                total = 0
                for entry in path.rglob('*'):
                    if entry.is_file():
                        total += entry.stat().st_size
                return total
            
            result['archive_size_before'] = get_dir_size(archive_dir)
            
            # Check for inactivity (30+ days)
            archive_stat = archive_dir.stat()
            last_modified = datetime.fromtimestamp(archive_stat.st_mtime)
            days_inactive = (datetime.now() - last_modified).days
            
            if days_inactive < 30:
                self.logger.info(f"Archive is only {days_inactive} days old - no compression needed")
                return result
            
            # SECURITY SCAN: Check for malicious files before compression
            self.logger.info("Performing security scan on archive before compression...")
            security_issues = []
            file_hashes = {}
            
            # Scan for suspicious patterns
            suspicious_patterns = [
                r'(?i)(password|secret|api[_-]?key|token|credential)',  # Credentials
                r'(?i)(rm\s+-rf|delete|unlink|shutil\.remove)',  # Dangerous commands
                r'(?i)(exec|eval|__import__|system)',  # Code execution patterns
                r'\.exe$|\.cmd$|\.bat$|\.ps1$',  # Executable files
                r'(?i)(malware|trojan|virus|backdoor)',  # Malware indicators
            ]
            compiled_patterns = [re.compile(p) for p in suspicious_patterns]
            
            for file_path in archive_dir.rglob('*'):
                if file_path.is_file():
                    try:
                        # Hash each file for integrity verification
                        with open(file_path, 'rb') as f:
                            file_hashes[str(file_path)] = hashlib.sha256(f.read()).hexdigest()
                        
                        # Scan file content for suspicious patterns
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                for pattern in compiled_patterns:
                                    if pattern.search(content):
                                        security_issues.append({
                                            'file': str(file_path.relative_to(archive_dir)),
                                            'pattern': pattern.pattern[:50]
                                        })
                        except:
                            pass
                    except Exception as e:
                        self.logger.warning(f"Could not scan file {file_path}: {e}")
            
            result['security_scan_results'] = {
                'total_files_scanned': len(file_hashes),
                'suspicious_patterns_found': len(security_issues),
                'issues': security_issues[:10]  # Cap at 10 for display
            }
            
            if security_issues:
                self.logger.warning(f"Found {len(security_issues)} files with suspicious patterns")
                result['issues'].append(f"Security scan found {len(security_issues)} suspicious patterns")
                # Log but continue - human review required
            
            # Create compression archive
            archive_name = f"quarantine_legacy_archive_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tar.gz"
            archive_path = repo_root / archive_name
            
            self.logger.info(f"Compressing archive to {archive_name}...")
            
            with tarfile.open(archive_path, 'w:gz') as tar:
                tar.add(archive_dir, arcname='quarantine_legacy_archive')
            
            # Calculate compressed size
            result['archive_size_after'] = archive_path.stat().st_size
            result['compressed'] = True
            
            # Store file hashes for integrity verification
            hashes_file = repo_root / f"{archive_name}.hashes.json"
            with open(hashes_file, 'w') as f:
                json.dump(file_hashes, f, indent=2)
            
            self.logger.info(f"Archive compressed successfully")
            self.logger.info(f"Size reduction: {result['archive_size_before']} -> {result['archive_size_after']} bytes")
            
            # Don't delete original - keep for reference (per QUARANTINE policy)
            self.logger.info("Original archive retained for reference (per policy)")
            
        except Exception as e:
            self.logger.error(f"Archive compression error: {e}")
            result['issues'].append(f"Compression failed: {str(e)}")
        
        return result

    def _get_next_run_time(self, task_type: str) -> Optional[str]:
        """Get next run time for a task type."""
        # This is a simplified implementation
        # In a real implementation, you'd query the schedule library
        maintenance_config = self.config_manager.get('maintenance', {})

        if task_type not in maintenance_config or not maintenance_config[task_type].get('enabled', False):
            return None

        schedule_str = maintenance_config[task_type].get('schedule', '')

        try:
            if task_type == 'daily':
                hour, minute = map(int, schedule_str.split(':'))
                now = datetime.now()
                next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                if next_run <= now:
                    next_run += timedelta(days=1)
                return next_run.isoformat()

            elif task_type == 'weekly':
                day, time_str = schedule_str.split(' ', 1)
                hour, minute = map(int, time_str.split(':'))
                # Simplified - would need more complex logic for actual day calculation
                return f"Next {day} at {hour:02d}:{minute:02d}"

            elif task_type == 'monthly':
                day_str, time_str = schedule_str.split(' ', 1)
                hour, minute = map(int, time_str.split(':'))
                # Simplified
                return f"Next month {day_str} at {hour:02d}:{minute:02d}"

        except (ValueError, AttributeError):
            pass

        return "Schedule parsing error"