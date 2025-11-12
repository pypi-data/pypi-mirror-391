
import re
from pathlib import Path
from datetime import datetime

def set_project_version(project_root: Path, new_version: str):
    """
    Finds and replaces the version number in all critical project files.

    Args:
        project_root (Path): The root directory of the project.
        new_version (str): The new version string (e.g., "1.1.1.b1").
    
    Returns:
        list[str]: A list of files that were successfully updated.
    """
    updated_files = []
    pyproject_toml_path = project_root / "pyproject.toml"
    setup_py_path = project_root / "setup.py"
    init_py_path = project_root / "codesentinel" / "__init__.py"
    instructions_path = project_root / ".github" / "copilot-instructions.md"
    changelog_path = project_root / "CHANGELOG.md"
    readme_path = project_root / "README.md"
    security_path = project_root / "SECURITY.md"

    # --- Regex Patterns ---
    pyproject_pattern = re.compile(r'(^\s*version\s*=\s*["\'])([^"\']+)(["\'])', re.MULTILINE)
    setup_py_pattern = re.compile(r'(version\s*=\s*["\'])([^"\']+)(["\'])')
    setup_return_pattern = re.compile(r'(return\s*["\'])([^"\']+)(["\'])')
    init_py_pattern = re.compile(r'(__version__\s*=\s*["\'])([^"\']+)(["\'])')
    instructions_pattern = re.compile(r'(CANONICAL_PROJECT_VERSION:\s*["\'])([^"\']+)(["\'])')
    readme_badge_pattern = re.compile(r'(badge/version-)([0-9]+\.[0-9]+\.[0-9]+(?:\.[a-zA-Z0-9]+)?)')
    security_table_pattern = re.compile(r'(\|\s*)([0-9]+\.[0-9]+)(\.[xX]\s*\|)')

    # 1. Update pyproject.toml (Canonical Source)
    if pyproject_toml_path.exists():
        content = pyproject_toml_path.read_text(encoding='utf-8')
        new_content, count = pyproject_pattern.subn(rf'\g<1>{new_version}\g<3>', content)
        if count > 0:
            pyproject_toml_path.write_text(new_content, encoding='utf-8')
            updated_files.append(str(pyproject_toml_path))

    # 2. Update setup.py
    if setup_py_path.exists():
        content = setup_py_path.read_text(encoding='utf-8')
        modified = False

        new_content, count = setup_py_pattern.subn(rf'\g<1>{new_version}\g<3>', content)
        if count > 0:
            content = new_content
            modified = True

        new_content, count = setup_return_pattern.subn(rf'\g<1>{new_version}\g<3>', content)
        if count > 0:
            content = new_content
            modified = True

        if modified:
            setup_py_path.write_text(content, encoding='utf-8')
            updated_files.append(str(setup_py_path))

    # 3. Update codesentinel/__init__.py
    if init_py_path.exists():
        content = init_py_path.read_text(encoding='utf-8')
        new_content, count = init_py_pattern.subn(rf'\g<1>{new_version}\g<3>', content)
        if count > 0:
            init_py_path.write_text(new_content, encoding='utf-8')
            updated_files.append(str(init_py_path))

    # 4. Update .github/copilot-instructions.md
    if instructions_path.exists():
        content = instructions_path.read_text(encoding='utf-8')
        new_content, count = instructions_pattern.subn(rf'\g<1>{new_version}\g<3>', content)
        if count > 0:
            instructions_path.write_text(new_content, encoding='utf-8')
            updated_files.append(str(instructions_path))

    # 5. Update CHANGELOG.md
    if changelog_path.exists():
        content = changelog_path.read_text(encoding='utf-8')
        # Look for the most recent version heading
        latest_version_pattern = re.compile(r'(##\s*\[?v?)(\d+\.\d+\.\d+[^\]\s]*)', re.IGNORECASE)
        match = latest_version_pattern.search(content)
        
        if match and match.group(2) != new_version:
            # Add a new entry for the new version
            today = datetime.now().strftime('%Y-%m-%d')
            new_entry = f"## [v{new_version}] - {today}\n\n-   Initial release for this version.\n\n"
            # Insert the new entry after the main changelog title
            changelog_header = "# Changelog\n\n"
            if changelog_header in content:
                new_content = content.replace(changelog_header, changelog_header + new_entry)
                changelog_path.write_text(new_content, encoding='utf-8')
                updated_files.append(str(changelog_path))

    # 6. Update README.md (version badge)
    if readme_path.exists():
        content = readme_path.read_text(encoding='utf-8')
        new_content, count = readme_badge_pattern.subn(rf'\g<1>{new_version}', content)
        if count > 0:
            readme_path.write_text(new_content, encoding='utf-8')
            updated_files.append(str(readme_path))

    # 7. Update SECURITY.md (supported versions table)
    if security_path.exists():
        content = security_path.read_text(encoding='utf-8')
        # Extract major.minor from new version (e.g., "1.1.1.b1" -> "1.1")
        version_parts = new_version.split('.')
        if len(version_parts) >= 2:
            major_minor = f"{version_parts[0]}.{version_parts[1]}"
            new_content, count = security_table_pattern.subn(rf'\g<1>{major_minor}\g<3>', content)
            if count > 0:
                security_path.write_text(new_content, encoding='utf-8')
                updated_files.append(str(security_path))

    return updated_files
