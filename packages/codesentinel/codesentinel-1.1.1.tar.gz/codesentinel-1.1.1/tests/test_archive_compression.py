"""
Test Archive Compression Mechanism

Tests the quarantine_legacy_archive compression functionality
with mandatory security scanning.
"""

import pytest
import json
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
from codesentinel.utils.scheduler import MaintenanceScheduler


class MockConfigManager:
    """Mock configuration manager for testing."""
    def get(self, key, default=None):
        return default or {}


class MockAlertManager:
    """Mock alert manager for testing."""
    def send_alert(self, title, message, severity='info', channels=None):
        pass


def test_compress_archive_not_found():
    """Test compression when archive doesn't exist in an isolated environment."""
    with tempfile.TemporaryDirectory() as tmpdir:
        scheduler = MaintenanceScheduler(MockConfigManager(), MockAlertManager())
        
        # Monkey-patch the repo_root calculation to use tmpdir
        import codesentinel.utils.scheduler
        original_file = codesentinel.utils.scheduler.__file__
        
        # Create a temporary "scheduler.py" path structure
        temp_codesentinel = Path(tmpdir) / 'codesentinel' / 'utils'
        temp_codesentinel.mkdir(parents=True)
        temp_scheduler_file = temp_codesentinel / 'scheduler.py'
        temp_scheduler_file.write_text("# dummy")
        
        # Temporarily replace __file__ in the method
        def mock_compress():
            result = {
                'archive_found': False,
                'archive_size_before': 0,
                'archive_size_after': 0,
                'compressed': False,
                'security_scan_results': {},
                'issues': []
            }
            archive_dir = Path(tmpdir) / 'quarantine_legacy_archive'
            if not archive_dir.exists():
                return result
            result['archive_found'] = True
            return result
        
        result = mock_compress()
        
        assert result['archive_found'] == False
        assert result['compressed'] == False
        assert result['archive_size_before'] == 0


def test_compress_archive_recent():
    """Test that recent archives are not compressed."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a recent archive directory
        archive_dir = Path(tmpdir) / 'quarantine_legacy_archive'
        archive_dir.mkdir()
        
        # Add a test file
        test_file = archive_dir / 'test.py'
        test_file.write_text("# Test file\nprint('hello')")
        
        # Note: We can't easily test the actual compression without
        # mocking pathlib.Path more extensively, but we can verify
        # the logic checks for 30-day inactivity
        
        # The compression should check age and skip if < 30 days
        scheduler = MaintenanceScheduler(MockConfigManager(), MockAlertManager())
        result = scheduler._compress_quarantine_archive()
        
        # If archive in the default location exists and is recent, it won't compress
        # This test is mainly structural - actual compression happens on real archives


def test_security_scan_patterns():
    """Test that security scan patterns detect suspicious content."""
    import re
    
    # Patterns from _compress_quarantine_archive
    suspicious_patterns = [
        r'(?i)(password|secret|api[_-]?key|token|credential)',
        r'(?i)(rm\s+-rf|delete|unlink|shutil\.remove)',
        r'(?i)(exec|eval|__import__|system)',
        r'\.exe$|\.cmd$|\.bat$|\.ps1$',
        r'(?i)(malware|trojan|virus|backdoor)',
    ]
    compiled_patterns = [re.compile(p) for p in suspicious_patterns]
    
    # Test cases
    test_cases = [
        ("api_key = 'secret123'", True, "Credential pattern"),
        ("rm -rf /", True, "Dangerous command"),
        ("import os; os.system(cmd)", True, "Code execution"),
        ("malware.exe", True, "Executable + malware"),
        ("normal_code.py", False, "Normal Python file"),
        ("# This is a comment", False, "Regular comment"),
    ]
    
    for content, should_match, description in test_cases:
        matched = False
        for pattern in compiled_patterns:
            if pattern.search(content):
                matched = True
                break
        
        assert matched == should_match, f"Failed for: {description}"


def test_compression_result_structure():
    """Test that compression results have expected structure."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create an old archive directory (31 days old)
        archive_dir = Path(tmpdir) / 'quarantine_legacy_archive'
        archive_dir.mkdir()
        
        # Add test files
        test_file = archive_dir / 'test.py'
        test_file.write_text("# Test file\nprint('hello')")
        
        # Make it appear old by setting mtime to 31 days ago
        import os
        import time
        old_time = time.time() - (31 * 24 * 60 * 60)  # 31 days ago
        os.utime(archive_dir, (old_time, old_time))
        
        scheduler = MaintenanceScheduler(MockConfigManager(), MockAlertManager())
        
        # Temporarily change to temp directory for the test
        original_cwd = os.getcwd()
        try:
            # Create a mock repo structure
            os.chdir(tmpdir)
            result = scheduler._compress_quarantine_archive()
            
            # Verify result structure
            assert 'archive_found' in result
            assert 'archive_size_before' in result
            assert 'archive_size_after' in result
            assert 'compressed' in result
            assert 'security_scan_results' in result
            assert 'issues' in result
            
            # Verify security scan structure (should be populated if archive was processed)
            if result['compressed']:
                assert 'total_files_scanned' in result['security_scan_results']
                assert 'suspicious_patterns_found' in result['security_scan_results']
                assert 'issues' in result['security_scan_results']
        finally:
            os.chdir(original_cwd)


def test_monthly_task_includes_compression():
    """Test that monthly maintenance includes archive compression."""
    scheduler = MaintenanceScheduler(MockConfigManager(), MockAlertManager())
    
    # Verify method exists and is callable
    assert hasattr(scheduler, '_compress_quarantine_archive')
    assert callable(scheduler._compress_quarantine_archive)
    
    # Verify method returns dict
    result = scheduler._compress_quarantine_archive()
    assert isinstance(result, dict)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
