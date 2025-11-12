"""
Scan command utilities for CodeSentinel.

Handles security scans and repository bloat audits.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple


def run_bloat_audit(workspace_root: Path) -> Dict[str, Any]:
    """
    Run comprehensive repository bloat analysis.
    
    Based on tools/repository_bloat_audit.py with improvements.
    
    Args:
        workspace_root: Path to repository root
        
    Returns:
        Dictionary containing audit results
    """
    results = {
        'cache_artifacts': _audit_cache_artifacts(workspace_root),
        'build_artifacts': _audit_build_artifacts(workspace_root),
        'large_files': _audit_large_files(workspace_root),
        'documentation': _audit_documentation(workspace_root),
        'test_artifacts': _audit_test_artifacts(workspace_root),
        'archive': _audit_archive(workspace_root),
        'configuration': _audit_configuration(workspace_root),
        'dependencies': _audit_dependencies(workspace_root),
    }
    
    # Calculate summary statistics
    results['summary'] = _calculate_summary(results)
    
    return results


def _audit_cache_artifacts(root: Path) -> Dict[str, Any]:
    """Audit Python cache artifacts."""
    pycache_dirs = list(root.rglob('__pycache__'))
    pytest_cache = list(root.rglob('.pytest_cache'))
    pyc_files = list(root.rglob('*.pyc'))
    pyo_files = list(root.rglob('*.pyo'))
    egg_info = list(root.rglob('*.egg-info'))
    
    # Exclude virtual environments from counts
    venv_patterns = ['.venv', 'venv', 'env', '.env']
    
    def not_in_venv(path: Path) -> bool:
        return not any(pattern in path.parts for pattern in venv_patterns)
    
    pycache_dirs = [p for p in pycache_dirs if not_in_venv(p)]
    pyc_files = [p for p in pyc_files if not_in_venv(p)]
    pyo_files = [p for p in pyo_files if not_in_venv(p)]
    
    return {
        'pycache_count': len(pycache_dirs),
        'pytest_cache_count': len(pytest_cache),
        'pyc_count': len(pyc_files),
        'pyo_count': len(pyo_files),
        'egg_info_count': len(egg_info),
        'total_items': len(pycache_dirs) + len(pytest_cache) + len(pyc_files) + len(pyo_files) + len(egg_info),
        'recommendation': 'Run: codesentinel clean --cache --force' if pycache_dirs or pyc_files else None
    }


def _audit_build_artifacts(root: Path) -> Dict[str, Any]:
    """Audit build artifacts."""
    dist_dirs = list(root.glob('dist'))
    build_dirs = list(root.glob('build'))
    egg_info = list(root.glob('*.egg-info'))
    
    total_size = 0
    items = []
    
    for directory in dist_dirs + build_dirs + egg_info:
        if directory.is_dir():
            dir_size = sum(f.stat().st_size for f in directory.rglob('*') if f.is_file())
            total_size += dir_size
            items.append({
                'path': str(directory.relative_to(root)),
                'size_mb': round(dir_size / (1024 * 1024), 2),
                'type': 'directory'
            })
    
    return {
        'dist_count': len(dist_dirs),
        'build_count': len(build_dirs),
        'egg_info_count': len(egg_info),
        'total_size_mb': round(total_size / (1024 * 1024), 2),
        'items': items,
        'recommendation': 'Run: codesentinel clean --build --force' if items else None
    }


def _audit_large_files(root: Path, threshold_mb: float = 1.0) -> Dict[str, Any]:
    """Audit files larger than threshold."""
    large_files = []
    threshold_bytes = threshold_mb * 1024 * 1024
    
    # Exclude certain directories
    exclude_patterns = ['.venv', 'venv', 'env', '.git', 'node_modules', '__pycache__']
    
    for file_path in root.rglob('*'):
        if file_path.is_file():
            # Skip if in excluded directory
            if any(pattern in file_path.parts for pattern in exclude_patterns):
                continue
                
            size = file_path.stat().st_size
            if size > threshold_bytes:
                large_files.append({
                    'path': str(file_path.relative_to(root)),
                    'size_mb': round(size / (1024 * 1024), 2),
                    'extension': file_path.suffix
                })
    
    # Sort by size descending
    large_files.sort(key=lambda x: x['size_mb'], reverse=True)
    
    return {
        'count': len(large_files),
        'threshold_mb': threshold_mb,
        'files': large_files[:10],  # Top 10 largest
        'total_size_mb': round(sum(f['size_mb'] for f in large_files), 2),
        'recommendation': 'Review large files for archival or compression' if large_files else None
    }


def _audit_documentation(root: Path) -> Dict[str, Any]:
    """Audit documentation for bloat and duplication."""
    md_files = list(root.rglob('*.md'))
    
    # Exclude virtual environments and .git
    exclude_patterns = ['.venv', 'venv', 'env', '.git']
    md_files = [f for f in md_files if not any(pattern in f.parts for pattern in exclude_patterns)]
    
    # Find session/checkpoint docs
    session_docs = [f for f in md_files if any(keyword in f.name.upper() for keyword in ['SESSION', 'CHECKPOINT', 'TODO'])]
    
    # Find duplicates by name
    from collections import defaultdict
    by_name = defaultdict(list)
    for file in md_files:
        by_name[file.name].append(file)
    
    duplicates = {name: [str(f.relative_to(root)) for f in files] 
                  for name, files in by_name.items() if len(files) > 1}
    
    return {
        'total_markdown': len(md_files),
        'session_docs_count': len(session_docs),
        'session_docs': [str(f.relative_to(root)) for f in session_docs],
        'duplicate_count': len(duplicates),
        'duplicates': duplicates,
        'recommendation': 'Archive session docs to quarantine_legacy_archive/session_docs/' if session_docs else None
    }


def _audit_test_artifacts(root: Path) -> Dict[str, Any]:
    """Audit test artifacts and organization."""
    test_dirs = []
    test_files = []
    
    # Find test directories
    for pattern in ['test', 'tests', 'test_*']:
        test_dirs.extend(root.rglob(pattern))
    
    # Find test files
    for pattern in ['test_*.py', '*_test.py']:
        test_files.extend(root.rglob(pattern))
    
    # Exclude virtual environments
    exclude_patterns = ['.venv', 'venv', 'env', '.git', 'site-packages']
    test_dirs = [d for d in test_dirs if d.is_dir() and not any(pattern in d.parts for pattern in exclude_patterns)]
    test_files = [f for f in test_files if not any(pattern in f.parts for pattern in exclude_patterns)]
    
    # Find duplicates by name
    from collections import defaultdict
    by_name = defaultdict(list)
    for file in test_files:
        by_name[file.name].append(file)
    
    duplicate_tests = {name: [str(f.relative_to(root)) for f in files] 
                       for name, files in by_name.items() if len(files) > 1}
    
    return {
        'test_directories': len(test_dirs),
        'test_files': len(test_files),
        'duplicate_tests': len(duplicate_tests),
        'duplicates': duplicate_tests if len(duplicate_tests) <= 5 else dict(list(duplicate_tests.items())[:5]),
        'recommendation': 'Verify test files in site-packages are not user tests' if duplicate_tests else None
    }


def _audit_archive(root: Path) -> Dict[str, Any]:
    """Audit quarantine_legacy_archive organization."""
    archive_dir = root / 'quarantine_legacy_archive'
    
    if not archive_dir.exists():
        return {
            'exists': False,
            'recommendation': 'Create quarantine_legacy_archive/ for non-destructive archival'
        }
    
    files = list(archive_dir.rglob('*'))
    files = [f for f in files if f.is_file()]
    
    total_size = sum(f.stat().st_size for f in files)
    
    # Check for subdirectory organization
    subdirs = [d for d in archive_dir.iterdir() if d.is_dir()]
    
    return {
        'exists': True,
        'file_count': len(files),
        'total_size_mb': round(total_size / (1024 * 1024), 2),
        'subdirectories': len(subdirs),
        'organized': len(subdirs) > 0,
        'recommendation': 'Archive is organized' if subdirs else 'Organize archive into subdirectories by type/date'
    }


def _audit_configuration(root: Path) -> Dict[str, Any]:
    """Audit configuration file organization."""
    config_files = {
        'json': list(root.glob('*.json')),
        'toml': list(root.glob('*.toml')),
        'yml': list(root.glob('*.yml')) + list(root.glob('*.yaml')),
        'ini': list(root.glob('*.ini')),
        'cfg': list(root.glob('*.cfg')),
    }
    
    total_configs = sum(len(files) for files in config_files.values())
    
    return {
        'total_configs': total_configs,
        'by_type': {ext: len(files) for ext, files in config_files.items()},
        'recommendation': 'Consider consolidating config files' if total_configs > 10 else None
    }


def _audit_dependencies(root: Path) -> Dict[str, Any]:
    """Audit dependency file organization."""
    req_files = list(root.glob('requirements*.txt')) + list(root.rglob('requirements*.txt'))
    
    # Exclude virtual environments
    exclude_patterns = ['.venv', 'venv', 'env', '.git', 'site-packages']
    req_files = [f for f in req_files if not any(pattern in f.parts for pattern in exclude_patterns)]
    
    return {
        'requirement_files': len(req_files),
        'files': [str(f.relative_to(root)) for f in req_files],
        'recommendation': 'Consolidate into requirements.txt + requirements-dev.txt' if len(req_files) > 2 else None
    }


def _calculate_summary(results: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate summary statistics from audit results."""
    total_issues = 0
    priority_actions = []
    
    # Cache artifacts
    cache = results['cache_artifacts']
    if cache['total_items'] > 0:
        total_issues += 1
        priority_actions.append(f"Clean {cache['total_items']} cache artifacts")
    
    # Build artifacts
    build = results['build_artifacts']
    if build['total_size_mb'] > 0:
        total_issues += 1
        priority_actions.append(f"Clean {build['total_size_mb']}MB of build artifacts")
    
    # Large files
    large = results['large_files']
    if large['count'] > 0:
        total_issues += 1
        priority_actions.append(f"Review {large['count']} large files ({large['total_size_mb']}MB)")
    
    # Documentation
    docs = results['documentation']
    if docs['session_docs_count'] > 0:
        total_issues += 1
        priority_actions.append(f"Archive {docs['session_docs_count']} session documents")
    
    if docs['duplicate_count'] > 0:
        total_issues += 1
        priority_actions.append(f"Resolve {docs['duplicate_count']} duplicate documentation files")
    
    return {
        'total_issues': total_issues,
        'priority_actions': priority_actions,
        'status': 'clean' if total_issues == 0 else 'needs_attention'
    }


def handle_scan_command(args, codesentinel) -> int:
    """
    Handle scan command execution.
    
    Args:
        args: Parsed command line arguments
        codesentinel: CodeSentinel instance
        
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    # Determine which scans to run
    run_security = args.security or args.all or (not args.bloat_audit and not args.all)
    run_bloat = args.bloat_audit or args.all
    
    results = {}
    
    # Run security scan
    if run_security:
        print("Running security scan...")
        try:
            security_results = codesentinel.run_security_scan()
            results['security'] = security_results
            
            if not args.json:
                print(f"✓ Security scan completed. Found {security_results['summary']['total_vulnerabilities']} vulnerabilities.")
        except Exception as e:
            print(f"⚠ Security scan failed: {e}")
            results['security'] = {'error': str(e)}
    
    # Run bloat audit
    if run_bloat:
        print("\nRunning repository bloat audit...")
        try:
            workspace_root = Path.cwd()
            bloat_results = run_bloat_audit(workspace_root)
            results['bloat_audit'] = bloat_results
            
            if not args.json:
                _print_bloat_results(bloat_results, workspace_root)
        except Exception as e:
            print(f"⚠ Bloat audit failed: {e}")
            results['bloat_audit'] = {'error': str(e)}
    
    # Handle output
    if args.output or args.json:
        output_data = json.dumps(results, indent=2)
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output_data)
            print(f"\n✓ Scan results saved to {args.output}")
        else:
            print(output_data)
    
    return 0


def _print_bloat_results(results: Dict[str, Any], root: Path):
    """Print formatted bloat audit results to console."""
    print("\n" + "="*70)
    print("REPOSITORY BLOAT AUDIT RESULTS")
    print("="*70)
    
    # Summary
    summary = results['summary']
    print(f"\n📊 SUMMARY")
    print("-" * 60)
    print(f"  Status: {summary['status'].upper()}")
    print(f"  Issues Found: {summary['total_issues']}")
    
    if summary['priority_actions']:
        print(f"\n🎯 PRIORITY ACTIONS:")
        for i, action in enumerate(summary['priority_actions'], 1):
            print(f"  {i}. {action}")
    
    # Cache artifacts
    cache = results['cache_artifacts']
    if cache['total_items'] > 0:
        print(f"\n📦 CACHE ARTIFACTS")
        print("-" * 60)
        print(f"  __pycache__ directories: {cache['pycache_count']}")
        print(f"  .pytest_cache: {cache['pytest_cache_count']}")
        print(f"  Compiled Python files: {cache['pyc_count']}")
        if cache['recommendation']:
            print(f"  ➜ {cache['recommendation']}")
    
    # Build artifacts
    build = results['build_artifacts']
    if build['total_size_mb'] > 0:
        print(f"\n🏗️  BUILD ARTIFACTS")
        print("-" * 60)
        print(f"  Total size: {build['total_size_mb']} MB")
        print(f"  dist/ directories: {build['dist_count']}")
        print(f"  build/ directories: {build['build_count']}")
        if build['recommendation']:
            print(f"  ➜ {build['recommendation']}")
    
    # Large files
    large = results['large_files']
    if large['count'] > 0:
        print(f"\n📁 LARGE FILES (>{large['threshold_mb']}MB)")
        print("-" * 60)
        print(f"  Total: {large['count']} files ({large['total_size_mb']} MB)")
        if large['files']:
            print(f"  Top {min(5, len(large['files']))} largest:")
            for file in large['files'][:5]:
                print(f"    • {file['path']} ({file['size_mb']} MB)")
    
    # Documentation
    docs = results['documentation']
    if docs['session_docs_count'] > 0 or docs['duplicate_count'] > 0:
        print(f"\n📚 DOCUMENTATION")
        print("-" * 60)
        print(f"  Total markdown files: {docs['total_markdown']}")
        print(f"  Session/checkpoint docs: {docs['session_docs_count']}")
        if docs['duplicate_count'] > 0:
            print(f"  Duplicate files: {docs['duplicate_count']}")
        if docs['recommendation']:
            print(f"  ➜ {docs['recommendation']}")
    
    # Archive
    archive = results['archive']
    if archive['exists']:
        print(f"\n📦 ARCHIVE STATUS")
        print("-" * 60)
        print(f"  Files in archive: {archive['file_count']}")
        print(f"  Archive size: {archive['total_size_mb']} MB")
        print(f"  Organized: {'Yes' if archive['organized'] else 'No'} ({archive['subdirectories']} subdirectories)")
    
    print("\n" + "="*70)
    print(f"💡 Run 'codesentinel clean --help' to see cleanup options")
    print("="*70 + "\n")
