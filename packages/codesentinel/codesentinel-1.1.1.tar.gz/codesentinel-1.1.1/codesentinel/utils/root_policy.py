"""
Root Directory Policy Configuration
====================================

Central configuration for allowed files and directories in repository root.
Used by both CLI clean command and maintenance automation to ensure consistency.

Following SEAM Protection™: Security, Efficiency, And Minimalism
"""

# Essential files that are allowed in root directory
ALLOWED_ROOT_FILES = {
    # Python project files
    'setup.py',
    'pyproject.toml',
    'MANIFEST.in',
    
    # Configuration files
    'pytest.ini',
    'requirements.txt',
    'requirements-dev.txt',
    
    # Scripts
    'run_tests.py',
    'publish_to_pypi.py',
    
    # Core user-facing documentation only
    'README.md',
    'LICENSE',
    'CHANGELOG.md',
    'CONTRIBUTING.md',
    'SECURITY.md',
    'QUICK_START.md',
    
    # Project-specific config and state
    'codesentinel.json',
    'codesentinel.log',
    '.codesentinel_integrity.json',
    '.test_integrity.json',
    '.gitignore',
}

# Essential directories that are allowed in root directory
ALLOWED_ROOT_DIRS = {
    '.git',
    '.github',
    '.venv',
    '.vscode',
    '.codesentinel',
    '.pytest_cache',
    'archive',
    'codesentinel',
    'deployment',
    'dist',  # Package build artifacts
    'docs',
    'github',
    'infrastructure',
    'logs',
    'requirements',
    'scripts',
    'tests',
    'tools',
    'quarantine_legacy_archive',
}

# File patterns that indicate where misplaced files should be moved
FILE_MAPPINGS = {
    # Audit files -> docs/audit/
    'AUDIT_': 'docs/audit/',
    
    # Report files -> docs/reports/
    'PHASE_': 'docs/reports/',
    'TEST_CASE_': 'docs/reports/',
    'MEASUREMENT_': 'docs/reports/',
    'FINAL_DOC_': 'docs/reports/',
    'READY_FOR_': 'docs/reports/',
    'SYSTEM_': 'docs/reports/',
    'MERGE_READY_': 'docs/reports/',
    
    # Planning files -> docs/planning/
    'ROADMAP': 'docs/planning/',
    'PLAN': 'docs/planning/',
    'PROPOSED_': 'docs/planning/',
    'SECURE_CREDENTIALS_': 'docs/planning/',
    'DEVELOPMENT_': 'docs/planning/',
    
    # Implementation documentation -> docs/architecture/
    'IMPLEMENTATION': 'docs/architecture/',
    'ASSESSMENT': 'docs/architecture/',
    'POLICY_VIOLATION': 'docs/architecture/',
}
