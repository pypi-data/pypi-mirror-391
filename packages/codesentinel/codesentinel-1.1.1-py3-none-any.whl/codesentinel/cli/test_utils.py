"""
Utility functions for the 'test' command in the CodeSentinel CLI.

This module provides integration between the main CLI and the beta testing suite,
enabling streamlined beta testing workflows directly from the command line.
"""

import sys
import re
import subprocess
from pathlib import Path


def _get_relative_path(absolute_path):
    """
    Convert an absolute path to a repository-relative path.
    
    Args:
        absolute_path: Absolute path to convert (Path or str)
        
    Returns:
        String representation of path relative to repository root, prefixed with 'CodeSentinel/'
    """
    try:
        abs_path = Path(absolute_path)
        repo_root = Path.cwd()
        
        # Try to get relative path
        try:
            rel_path = abs_path.relative_to(repo_root)
            return f"CodeSentinel/{rel_path}".replace("\\", "/")
        except ValueError:
            # If path is not under repo root, just return the name with parent
            return f"CodeSentinel/.../{abs_path.parent.name}/{abs_path.name}".replace("\\", "/")
    except Exception:
        return str(absolute_path)


def _select_python_executable():
    """
    Smart Python executable selection.
    
    Auto-detects the current Python interpreter and suggests it as default.
    Allows user to confirm or specify a different Python executable.
    
    Returns:
        Path to selected Python executable, or None if cancelled.
    """
    # Detect current Python interpreter
    current_python = sys.executable
    
    # Get Python version
    try:
        version_output = subprocess.check_output(
            [current_python, '--version'],
            stderr=subprocess.STDOUT,
            text=True
        ).strip()
    except Exception:
        version_output = "Unknown version"
    
    print(f"\nDetected Python interpreter:")
    print(f"  🐍 {version_output}")
    print(f"  📁 {current_python}")
    
    choice = input("\nUse this Python interpreter? (y/n): ").strip().lower()
    
    if choice == 'y':
        return current_python
    
    # User wants to specify a different Python
    print("\nEnter path to Python executable (or press Enter to cancel):")
    print("Examples:")
    print("  - python")
    print("  - python3.13")
    print("  - C:\\Python313\\python.exe")
    
    custom_path = input("\nPython executable: ").strip()
    
    if not custom_path:
        print("Cancelled.")
        return None
    
    # Validate the custom Python executable
    try:
        test_output = subprocess.check_output(
            [custom_path, '--version'],
            stderr=subprocess.STDOUT,
            text=True
        ).strip()
        print(f"✓ Found: {test_output}")
        return custom_path
    except FileNotFoundError:
        print(f"❌ Python executable not found: {custom_path}")
        return None
    except Exception as e:
        print(f"❌ Error validating Python executable: {e}")
        return None


def _select_wheel_file():
    """
    Smart wheel file selection from dist directory.
    
    Scans the dist directory for .whl files, identifies the most recent version,
    and prompts the user to confirm or select a different file.
    
    Returns:
        Path to selected wheel file, or None if cancelled.
    """
    dist_dir = Path.cwd() / 'dist'
    
    if not dist_dir.exists():
        print(f"❌ Distribution directory not found: {dist_dir}")
        print("Please build the package first (e.g., python -m build)")
        return None
    
    # Find all wheel files
    wheel_files = list(dist_dir.glob('*.whl'))
    
    if not wheel_files:
        print(f"❌ No wheel files found in: {dist_dir}")
        print("Please build the package first (e.g., python -m build)")
        return None
    
    # Extract version numbers and sort by version
    def extract_version(wheel_path):
        """Extract version from wheel filename (e.g., codesentinel-1.1.0b1-py3-none-any.whl)"""
        match = re.search(r'-(\d+\.\d+\.\d+(?:b\d+)?)-', wheel_path.name)
        if match:
            version_str = match.group(1)
            # Convert to tuple for proper version comparison (e.g., '1.1.0b1' -> (1, 1, 0, 'b', 1))
            parts = re.split(r'(\d+|[a-z]+)', version_str)
            parts = [int(p) if p.isdigit() else p for p in parts if p]
            return parts
        return (0,)  # Fallback for malformed filenames
    
    wheel_files.sort(key=extract_version, reverse=True)
    latest_wheel = wheel_files[0]
    
    # Suggest the latest version
    print(f"\nMost recent wheel file found:")
    print(f"  📦 {latest_wheel.name}")
    print(f"  📁 {latest_wheel}")
    
    choice = input("\nUse this file? (y/n): ").strip().lower()
    
    if choice == 'y':
        return str(latest_wheel)
    
    # Show list of all available wheel files
    print("\nAvailable wheel files in dist/:")
    print("-" * 70)
    for idx, wheel in enumerate(wheel_files, 1):
        print(f"  {idx}. {wheel.name}")
    print(f"  0. Cancel")
    print("-" * 70)
    
    while True:
        try:
            selection = input("Select file number (or 0 to cancel): ").strip()
            if not selection:
                continue
            
            selection = int(selection)
            
            if selection == 0:
                print("Installation cancelled.")
                return None
            
            if 1 <= selection <= len(wheel_files):
                selected_wheel = wheel_files[selection - 1]
                print(f"✓ Selected: {selected_wheel.name}")
                return str(selected_wheel)
            else:
                print(f"❌ Invalid selection. Please enter a number between 0 and {len(wheel_files)}.")
        except ValueError:
            print("❌ Invalid input. Please enter a number.")
        except KeyboardInterrupt:
            print("\nCancelled.")
            return None


def add_test_parser(subparsers):
    """
    Add the 'test' command parser to the main CLI.
    
    Args:
        subparsers: The subparsers object from argparse.
        
    Returns:
        The test parser object.
    """
    test_parser = subparsers.add_parser(
        'test',
        help='Run beta testing workflow'
    )
    test_parser.add_argument(
        '--version',
        type=str,
        default='v1.1.0-beta.1',
        help='Version to test (default: v1.1.0-beta.1)'
    )
    test_parser.add_argument(
        '--interactive',
        action='store_true',
        default=True,
        help='Run in interactive mode (default)'
    )
    test_parser.add_argument(
        '--automated',
        action='store_true',
        help='Run in automated mode without user prompts'
    )
    test_parser.set_defaults(func=handle_test_command)
    
    return test_parser


def handle_test_command(args, codesentinel=None):
    """
    Handle the 'test' command execution.
    
    Args:
        args: Parsed command-line arguments.
        codesentinel: CodeSentinel instance (not used for testing).
    """
    # Add the tests directory to the path to import beta_testing_suite
    workspace_root = Path.cwd()
    tests_path = workspace_root / 'tests' / 'beta_testing'
    
    if not tests_path.exists():
        print(f"❌ Beta testing directory not found: {tests_path}")
        print("Please ensure you're running from the CodeSentinel workspace root.")
        sys.exit(1)
    
    sys.path.insert(0, str(tests_path.parent))
    sys.path.insert(0, str(tests_path))  # Also add tests directory directly
    
    try:
        from beta_testing.beta_testing_suite import BetaTestingManager
    except ImportError as e:
        print(f"❌ Could not import BetaTestingManager: {e}")
        print(f"Tried to import from: {tests_path.parent} and {tests_path}")
        sys.exit(1)
    
    print("=" * 70)
    print("CodeSentinel Beta Testing Workflow")
    print("=" * 70)
    print(f"Version: {args.version}")
    print(f"Mode: {'Automated' if args.automated else 'Interactive'}")
    print()
    
    # Initialize the beta testing manager
    manager = BetaTestingManager(version=args.version)
    
    if args.automated:
        print("Running automated beta testing pipeline...")
        run_automated_workflow(manager)
    else:
        print("Running interactive beta testing pipeline...")
        run_interactive_workflow(manager)


def run_interactive_workflow(manager):
    """
    Run the interactive beta testing workflow with menu-driven test suite.
    
    Args:
        manager: BetaTestingManager instance.
    """
    print("\n" + "=" * 70)
    print(f"CodeSentinel Beta Testing Workflow - {manager.version}")
    print("=" * 70)
    print()
    
    # Check for existing sessions
    active_sessions = manager.__class__.find_active_sessions(manager.version)
    
    resume_session = False
    if active_sessions:
        print(f"Found {len(active_sessions)} active session(s):")
        for idx, (session_id, session_file, last_updated) in enumerate(active_sessions, 1):
            print(f"  {idx}. {session_id[-5:]} (Last: {last_updated})")
        print()
        choice = input("Resume a session? (Enter number, last 5 chars, or N for new): ").strip()
        
        # Try to match by number first
        if choice.upper() == 'N':
            print("✓ Starting new session...")
        elif choice.isdigit() and 1 <= int(choice) <= len(active_sessions):
            selected_session = active_sessions[int(choice) - 1]
            manager.session_id = selected_session[0]
            resume_session = True
            print(f"✓ Resuming session: {manager.session_id[-5:]}...")
        else:
            # Try to match by partial session ID (last 5 chars)
            matched_sessions = [s for s in active_sessions if s[0].endswith(choice)]
            if len(matched_sessions) == 1:
                manager.session_id = matched_sessions[0][0]
                resume_session = True
                print(f"✓ Resuming session: {manager.session_id[-5:]}...")
            elif len(matched_sessions) > 1:
                print(f"❌ Ambiguous session ID. Multiple matches found.")
                print("✓ Starting new session...")
            else:
                print(f"❌ No session found matching '{choice}'")
                print("✓ Starting new session...")
    
    if resume_session:
        # Load session state
        tests, tester_name, venv_path = _load_session_state(manager)
        
        if tests and tester_name and venv_path:
            print(f"✓ Session restored!")
            print(f"  Tester: {tester_name}")
            print(f"  Environment: {_get_relative_path(venv_path)}")
            print(f"  Tests completed: {sum(1 for t in tests if t.get('completed', False))}/{len(tests)}")
            print()
            
            # Verify venv still exists
            if not Path(venv_path).exists():
                print("⚠️  Virtual environment not found. Recreating...")
                venv_path = manager.create_isolated_env(manager.python_executable or sys.executable)
                manager.install_beta_version(venv_path, manager.wheel_file)
                manager.venv_path = venv_path
            
            # Jump directly to test menu
            _run_test_menu(manager, venv_path, tester_name, installation_complete=tests[0].get('completed', False))
            return
        else:
            print("⚠️  Could not restore session. Starting fresh...")
            resume_session = False
    
    # New session - continue with normal workflow
    # Auto-detect Python and wheel
    python_exec = sys.executable
    try:
        python_version = subprocess.check_output(
            [python_exec, '--version'],
            stderr=subprocess.STDOUT,
            text=True
        ).strip()
        print(f"Detected Python: {python_version} ✓")
    except Exception:
        print(f"Detected Python: {python_exec}")
    
    # Find latest wheel
    dist_dir = Path.cwd() / 'dist'
    wheel_files = list(dist_dir.glob('*.whl')) if dist_dir.exists() else []
    
    if wheel_files:
        def extract_version(wheel_path):
            match = re.search(r'-(\d+\.\d+\.\d+(?:b\d+)?)-', wheel_path.name)
            if match:
                version_str = match.group(1)
                parts = re.split(r'(\d+|[a-z]+)', version_str)
                parts = [int(p) if p.isdigit() else p for p in parts if p]
                return parts
            return (0,)
        
        wheel_files.sort(key=extract_version, reverse=True)
        latest_wheel = wheel_files[0]
        print(f"Latest wheel: {latest_wheel.name} ✓")
    else:
        print("⚠️  No wheel files found in dist/")
        print("Please build the package first (e.g., python -m build)")
        return
    
    print()
    
    # Get tester name (only question asked upfront)
    tester_name = input("Your name: ").strip() or "Anonymous"
    
    # Clear input buffer to prevent bleed-through to menu
    sys.stdout.flush()
    print()
    
    # Store configuration in manager
    manager.python_executable = python_exec
    manager.wheel_file = str(latest_wheel)
    manager.tester_name = tester_name
    
    # Auto-setup: Create environment and install
    print("Setting up isolated environment...")
    venv_path = manager.create_isolated_env(python_exec)
    if not venv_path:
        print("❌ Failed to create environment.")
        return
    
    print("Installing CodeSentinel beta...")
    manager.install_beta_version(venv_path, str(latest_wheel))
    
    # Install pytest in the venv for testing
    print("Installing test dependencies...")
    if sys.platform == "win32":
        pip_exec = Path(venv_path) / 'Scripts' / 'pip.exe'
    else:
        pip_exec = Path(venv_path) / 'bin' / 'pip'
    
    try:
        subprocess.run([str(pip_exec), 'install', 'pytest'], check=True, capture_output=True)
        print("✓ Test dependencies installed")
    except Exception as e:
        print(f"⚠️  Could not install pytest: {e}")
    
    print()
    
    # Store venv path in manager
    manager.venv_path = venv_path
    
    # Start test iteration
    iteration_path = manager.start_test_iteration(tester_name)
    if not iteration_path:
        print("❌ Failed to start test iteration.")
        return
    
    print(f"✓ Test iteration ready!")
    print(f"  Report: {_get_relative_path(iteration_path)}")
    print()
    
    # Run interactive test menu (mark installation as complete since we just did it)
    _run_test_menu(manager, venv_path, tester_name, installation_complete=True)
    
    # Workflow complete - final report shown in menu if 'C' option was chosen


def _run_test_menu(manager, venv_path, tester_name, installation_complete=False):
    """
    Display and handle the interactive test menu.
    
    Args:
        manager: BetaTestingManager instance.
        venv_path: Path to the virtual environment.
        tester_name: Name of the tester.
        installation_complete: Whether installation was already completed.
    """
    # Define available tests
    tests = [
        {"id": 1, "name": "Installation Test", "script": "test_installation.py", "completed": installation_complete, "skip_in_run_all": True},
        {"id": 2, "name": "CLI Commands Test", "script": "test_cli.py", "completed": False, "skip_in_run_all": False},
        {"id": 3, "name": "Core Functionality Test", "script": "test_core.py", "completed": False, "skip_in_run_all": False},
        {"id": 4, "name": "Configuration Test", "script": "test_config.py", "completed": False, "skip_in_run_all": False},
        {"id": 5, "name": "Documentation Test", "script": "test_docs_formatting.py", "completed": False, "skip_in_run_all": False},
        {"id": 6, "name": "Integrity Test", "script": "test_integrity.py", "completed": False, "skip_in_run_all": False},
        {"id": 7, "name": "Process Monitor Test", "script": "test_process_monitor.py", "completed": False, "skip_in_run_all": False},
        {"id": 8, "name": "Dev Audit Test", "script": "test_dev_audit.py", "completed": False, "skip_in_run_all": False},
    ]
    
    # Track if any test has been run
    any_test_run = False
    
    while True:
        # Display menu
        print("\n" + "=" * 70)
        print("TEST SUITE MENU")
        print("=" * 70)
        print()
        
        for test in tests:
            if test["completed"]:
                status = "✓"
            elif test.get("failed", False):
                status = "✗"
            else:
                status = " "
            print(f"  [{status}] {test['id']}. {test['name']}")
        
        print()
        print("  A. Run All Tests")
        
        # Show reload option only after tests have been run
        if any_test_run:
            print("  R. Reload Version (reinstall from updated wheel)")
        
        print("  S. Save & Exit (resume later)")
        
        # Show complete session option only after tests have been run
        if any_test_run:
            print("  C. Complete Session (Save & Generate Final Report)")
        
        print("  X. Exit Without Saving")
        
        # Show change options only if no tests have been run yet
        if not any_test_run:
            print()
            print("  P. Change Python Interpreter")
            print("  V. Change Version/Wheel")
        
        print()
        print("=" * 70)
        
        try:
            choice = input("Select option: ").strip().upper()
        except KeyboardInterrupt:
            # Ctrl+C should act like 'X' (Exit Without Saving)
            print("\n\nInterrupted. Exiting without saving...")
            confirm = input("Are you sure? Test results will be lost. (y/n): ").strip().lower()
            if confirm == 'y':
                _cleanup_session(manager, venv_path)
                print("Session discarded.")
                break
            else:
                continue  # Return to menu
        
        if choice == 'A':
            # Run all tests (skip installation test)
            print("\nRunning all tests...")
            for test in tests:
                if not test.get("skip_in_run_all", False):
                    _run_single_test(manager, venv_path, test)
            any_test_run = True
            
            # Auto-save after running tests
            _save_session_state(manager, tests, tester_name)
        
        elif choice == 'R':
            # Reload version - reinstall from updated wheel
            if not any_test_run:
                print("\n❌ Reload Version option not available yet.")
                print("   Run at least one test before reloading to a new version.")
                continue
            
            print("\n" + "=" * 70)
            print("RELOAD VERSION")
            print("=" * 70)
            print("\nThis will reinstall CodeSentinel from an updated wheel file.")
            print("Your test progress will be preserved.")
            print()
            
            # Save current state
            _save_session_state(manager, tests, tester_name)
            
            # Select new wheel
            new_wheel = _select_wheel_file()
            if new_wheel:
                print(f"\nReinstalling from: {new_wheel.name if hasattr(new_wheel, 'name') else str(new_wheel)}")
                try:
                    # Uninstall current version
                    if sys.platform == "win32":
                        pip_exec = Path(venv_path) / 'Scripts' / 'pip.exe'
                    else:
                        pip_exec = Path(venv_path) / 'bin' / 'pip'
                    
                    subprocess.run([str(pip_exec), 'uninstall', 'codesentinel', '-y'], 
                                   check=True, capture_output=True)
                    print("✓ Uninstalled previous version")
                    
                    # Install new version
                    manager.install_beta_version(venv_path, str(new_wheel))
                    print("✓ Installed updated version")
                    
                    # Update manager state
                    manager.wheel_file = str(new_wheel)
                    manager.iteration_count += 1
                    
                    # Save updated state
                    _save_session_state(manager, tests, tester_name)
                    
                except Exception as e:
                    print(f"❌ Error reloading version: {e}")
            else:
                print("❌ No wheel file selected")
        
        elif choice == 'S':
            # Save and exit (resume later)
            print("\nSaving session state...")
            session_file = _save_session_state(manager, tests, tester_name)
            print(f"\n✓ Session saved!")
            print(f"  Resume with: codesentinel test --resume {manager.session_id[-5:]}")
            print()
            print("Session preserved. Use 'C' option when ready to complete.")
            break
        
        elif choice == 'C':
            # Complete session - save and generate final report
            if not any_test_run:
                print("\n❌ Complete Session option not available yet.")
                print("   Run at least one test before completing the session.")
                continue
            
            print("\nCompleting session...")
            _save_session_state(manager, tests, tester_name)
            final_report = _generate_final_report(manager, tester_name)
            
            # Display session summary
            print()
            print("=" * 70)
            print("Beta Testing Session Complete!")
            print("=" * 70)
            
            if final_report and final_report.exists():
                print(f"Final Report: {_get_relative_path(final_report)}")
                
                # Display summary
                try:
                    with open(final_report, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # Extract key metrics from the report
                    print()
                    print("Session Summary:")
                    print("-" * 70)
                    
                    # Parse session ID
                    if 'Session ID:' in content:
                        session_line = [line for line in content.split('\n') if 'Session ID:' in line][0]
                        print(f"  {session_line.strip()}")
                    
                    # Parse tester
                    if 'Lead Tester:' in content:
                        tester_line = [line for line in content.split('\n') if 'Lead Tester:' in line][0]
                        print(f"  {tester_line.strip()}")
                    
                    # Parse total iterations
                    if 'Total Iterations:' in content:
                        iter_line = [line for line in content.split('\n') if 'Total Iterations:' in line][0]
                        print(f"  {iter_line.strip()}")
                        
                    print("-" * 70)
                except Exception as e:
                    print(f"⚠️  Could not read report summary: {e}")
            
            print("=" * 70)
            
            _cleanup_session(manager, venv_path)
            break
        
        elif choice == 'X':
            # Exit without saving
            print("\nExiting without saving...")
            confirm = input("Are you sure? Test results will be lost. (y/n): ").strip().lower()
            if confirm == 'y':
                _cleanup_session(manager, venv_path)
                print("Session discarded.")
                break
        
        elif choice.isdigit():
            # Run specific test
            test_id = int(choice)
            test = next((t for t in tests if t["id"] == test_id), None)
            if test:
                _run_single_test(manager, venv_path, test)
                any_test_run = True
                
                # Auto-save after each test
                _save_session_state(manager, tests, tester_name)
            else:
                print(f"❌ Invalid test number: {test_id}")
        
        elif choice == 'P' and not any_test_run:
            # Change Python interpreter (only before tests run)
            print("\n⚠️  Changing Python will require reinstalling the environment.")
            confirm = input("Continue? (y/n): ").strip().lower()
            if confirm == 'y':
                new_python = _select_python_executable()
                if new_python:
                    print("\nRecreating environment with new Python...")
                    _cleanup_session(manager, venv_path)
                    # This would need to return and restart the workflow
                    print("⚠️  Please restart the test workflow to use the new Python interpreter.")
                    break
        
        elif choice == 'V' and not any_test_run:
            # Change version/wheel (only before tests run)
            print("\n⚠️  Changing version will require reinstalling the environment.")
            confirm = input("Continue? (y/n): ").strip().lower()
            if confirm == 'y':
                new_wheel = _select_wheel_file()
                if new_wheel:
                    print("\nReinstalling with new wheel...")
                    # Reinstall in existing venv
                    if sys.platform == "win32":
                        pip_exec = Path(venv_path) / 'Scripts' / 'pip.exe'
                    else:
                        pip_exec = Path(venv_path) / 'bin' / 'pip'
                    
                    try:
                        # Uninstall old version
                        subprocess.run([str(pip_exec), 'uninstall', 'codesentinel', '-y'], 
                                     check=False, capture_output=True)
                        # Install new version
                        subprocess.run([str(pip_exec), 'install', new_wheel], 
                                     check=True, capture_output=True)
                        print("✓ New version installed successfully")
                    except Exception as e:
                        print(f"❌ Error reinstalling: {e}")
        
        else:
            if choice in ['P', 'V'] and any_test_run:
                print(f"❌ Cannot change configuration after tests have been run")
            else:
                print(f"❌ Invalid option: {choice}")


def _run_single_test(manager, venv_path, test):
    """
    Run a single test and update its status.
    
    Args:
        manager: BetaTestingManager instance.
        venv_path: Path to the virtual environment.
        test: Test dictionary.
    """
    print(f"\n{'─' * 70}")
    print(f"Running: {test['name']}")
    print('─' * 70)
    
    # Determine Python executable in venv
    if sys.platform == "win32":
        python_exec = Path(venv_path) / 'Scripts' / 'python.exe'
    else:
        python_exec = Path(venv_path) / 'bin' / 'python'
    
    # Path to test file
    test_file = Path.cwd() / 'tests' / test['script']
    
    if not test_file.exists():
        print(f"⚠️  Test file not found: {test_file}")
        print(f"   Skipping {test['name']}")
        test['completed'] = False
        print('─' * 70)
        return
    
    try:
        # Run the test using pytest in the venv
        result = subprocess.run(
            [str(python_exec), '-m', 'pytest', str(test_file), '-v'],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # Display the test output first
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        # Then show pass/fail status with enhanced verbosity
        print()  # Blank line for separation
        print("=" * 70)
        if result.returncode == 0:
            print(f"✅✅✅ {test['name']} PASSED ✅✅✅")
            print(f"Status: ALL TESTS SUCCESSFUL")
            print(f"Return Code: {result.returncode}")
            test['completed'] = True
            test['failed'] = False
        else:
            print(f"❌❌❌ {test['name']} FAILED ❌❌❌")
            print(f"Status: TEST FAILURES DETECTED")
            print(f"Return Code: {result.returncode}")
            
            # Extract and display consolidated failure summary
            print()
            print("Failure Summary:")
            print("-" * 70)
            
            # Combine stdout and stderr for analysis
            combined_output = (result.stdout or "") + (result.stderr or "")
            
            # Parse pytest output for failure information
            if "FAILED" in combined_output:
                # Extract failed test names
                import re
                failed_tests = re.findall(r'FAILED (.*?)(?:\s-|\s\[|$)', combined_output)
                if failed_tests:
                    for failed_test in failed_tests:
                        print(f"  • {failed_test.strip()}")
                else:
                    print("  • See output above for details")
            else:
                print("  • See output above for details")
            
            # Check for common error patterns
            if "ModuleNotFoundError" in combined_output or "ImportError" in combined_output:
                print("  • Missing dependencies detected")
            if "AssertionError" in combined_output:
                print("  • Assertion failures detected")
            if "AttributeError" in combined_output:
                print("  • Attribute/method errors detected")
            
            print("-" * 70)
            
            test['completed'] = False
            test['failed'] = True
        print("=" * 70)
    
    except subprocess.TimeoutExpired:
        print(f"❌ {test['name']} TIMEOUT (exceeded 60s)")
        test['completed'] = False
        test['failed'] = True
    except Exception as e:
        print(f"❌ {test['name']} ERROR: {e}")
        test['completed'] = False
        test['failed'] = True
    
    print('─' * 70)


def _save_session_state(manager, tests, tester_name):
    """
    Save the current session state including test results.
    
    Args:
        manager: BetaTestingManager instance.
        tests: List of test dictionaries with status.
        tester_name: Name of the tester.
        
    Returns:
        Path to the saved session file.
    """
    # Convert tests to serializable format
    test_results = {
        str(test['id']): {
            'name': test['name'],
            'script': test['script'],
            'completed': test.get('completed', False),
            'failed': test.get('failed', False),
            'skip_in_run_all': test.get('skip_in_run_all', False)
        }
        for test in tests
    }
    
    # Update manager state
    manager.tester_name = tester_name
    
    # Save to file
    return manager.save_session_state(test_results)


def _load_session_state(manager):
    """
    Load a previously saved session state and reconstruct test list.
    
    Args:
        manager: BetaTestingManager instance.
        
    Returns:
        Tuple of (tests_list, tester_name, venv_path) or (None, None, None) if load failed.
    """
    state = manager.load_session_state()
    
    if not state:
        return None, None, None
    
    # Reconstruct tests list from saved state
    test_results = state.get('test_results', {})
    tests = []
    for test_id, test_data in sorted(test_results.items(), key=lambda x: int(x[0])):
        tests.append({
            'id': int(test_id),
            'name': test_data['name'],
            'script': test_data['script'],
            'completed': test_data.get('completed', False),
            'failed': test_data.get('failed', False),
            'skip_in_run_all': test_data.get('skip_in_run_all', False)
        })
    
    tester_name = state.get('tester_name')
    venv_path = state.get('venv_path')
    
    return tests, tester_name, venv_path


def _generate_final_report(manager, tester_name):
    """
    Generate the final consolidated report and return its path.
    
    Args:
        manager: BetaTestingManager instance.
        tester_name: Name of the tester.
        
    Returns:
        Path to the consolidated report, or None if generation failed.
    """
    print("\nGenerating final report...")
    try:
        manager.consolidate_reports(tester_name)
        consolidated_path = manager.consolidated_dir / f"consolidated_report_{manager.session_id}.md"
        
        if consolidated_path.exists():
            print(f"✓ Consolidated report: {_get_relative_path(consolidated_path)}")
            return consolidated_path
        else:
            print("⚠️  Report file not found after generation")
            return None
    except Exception as e:
        print(f"❌ Error generating report: {e}")
        return None


def _cleanup_session(manager, venv_path):
    """
    Clean up the testing session.
    
    Args:
        manager: BetaTestingManager instance.
        venv_path: Path to the virtual environment.
    """
    print("\nCleaning up session...")
    try:
        # Remove virtual environment
        if Path(venv_path).exists():
            import shutil
            shutil.rmtree(venv_path)
            print(f"✓ Removed virtual environment: {_get_relative_path(venv_path)}")
    except Exception as e:
        print(f"⚠️  Could not remove venv: {e}")
    
    print("✓ Cleanup complete")


def run_automated_workflow(manager):
    """
    Run the automated beta testing workflow.
    
    Args:
        manager: BetaTestingManager instance.
    """
    print("⚠️  Automated workflow not yet fully implemented.")
    print("This will be enhanced in future releases.")
    print("\nPlease use interactive mode (default) for now.")
