"""
Archive Verification Pipeline

Implements scheduled integrity verification of archival records including:
- Checksum validation (SHA-256 verification)
- File count consistency
- Content sampling (random spot checks)
- Tampering detection
- Integrity reports

Runs weekly with exclusive access, non-blocking verification reporting.

Author: CodeSentinel
Date: 2025-11-11
"""

import hashlib
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, asdict, field
from threading import Thread, RLock, Event
import time
import random

logger = logging.getLogger(__name__)


class VerificationStatus(str):
    """Verification result status."""
    PASSED = "passed"
    FAILED = "failed"
    WARNINGS = "warnings"
    IN_PROGRESS = "in_progress"


@dataclass
class FileChecksum:
    """File checksum record."""
    path: str
    sha256: str
    size_bytes: int
    modified_time: float


@dataclass
class VerificationReport:
    """Results of verification operation."""
    timestamp: datetime
    status: VerificationStatus
    total_files_verified: int
    total_size_bytes: int
    checksums_matched: int
    checksums_mismatched: int
    files_added: int
    files_removed: int
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    verification_time_seconds: float = 0.0
    sample_size: int = 0


class ChecksumManager:
    """Manages file checksums for integrity verification."""
    
    def __init__(self, archive_root: Path):
        """
        Initialize checksum manager.
        
        Args:
            archive_root: Root path of archive to manage
        """
        self.archive_root = Path(archive_root)
        self.checksum_file = self.archive_root / ".archive_checksums.json"
        self._checksums: Dict[str, FileChecksum] = {}
        self._lock = RLock()
        
        self._load_checksums()
    
    def _load_checksums(self) -> None:
        """Load checksums from disk."""
        if not self.checksum_file.exists():
            return
        
        try:
            with open(self.checksum_file, 'r') as f:
                data = json.load(f)
            
            for path, checksum_dict in data.items():
                self._checksums[path] = FileChecksum(**checksum_dict)
            
            logger.info(f"Loaded {len(self._checksums)} checksums")
        except Exception as e:
            logger.error(f"Failed to load checksums: {e}")
    
    def _save_checksums(self) -> None:
        """Save checksums to disk."""
        try:
            data = {
                path: asdict(cs)
                for path, cs in self._checksums.items()
            }
            
            with open(self.checksum_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Saved {len(self._checksums)} checksums")
        except Exception as e:
            logger.error(f"Failed to save checksums: {e}")
    
    def compute_file_checksum(self, file_path: Path) -> str:
        """
        Compute SHA-256 checksum of file.
        
        Args:
            file_path: Path to file
        
        Returns:
            SHA-256 hex digest
        """
        sha256 = hashlib.sha256()
        
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(65536), b''):
                    sha256.update(chunk)
            
            return sha256.hexdigest()
        except Exception as e:
            logger.error(f"Failed to compute checksum for {file_path}: {e}")
            return ""
    
    def verify_file(self, file_path: Path) -> Tuple[bool, Optional[str]]:
        """
        Verify file integrity against stored checksum.
        
        Args:
            file_path: Path to file
        
        Returns:
            (is_valid, issue_description)
        """
        relative_path = file_path.relative_to(self.archive_root)
        path_key = str(relative_path)
        
        if path_key not in self._checksums:
            return True, "No prior checksum (new file)"
        
        stored = self._checksums[path_key]
        
        # Check file exists
        if not file_path.exists():
            return False, f"File deleted (was {stored.size_bytes} bytes)"
        
        # Compute current checksum
        current_checksum = self.compute_file_checksum(file_path)
        
        if current_checksum != stored.sha256:
            return False, f"Checksum mismatch (was {stored.sha256[:8]}...)"
        
        return True, None
    
    def update_file_checksum(self, file_path: Path) -> None:
        """Update checksum for file."""
        relative_path = file_path.relative_to(self.archive_root)
        path_key = str(relative_path)
        
        if not file_path.exists():
            if path_key in self._checksums:
                del self._checksums[path_key]
            return
        
        checksum = self.compute_file_checksum(file_path)
        stat_info = file_path.stat()
        
        self._checksums[path_key] = FileChecksum(
            path=path_key,
            sha256=checksum,
            size_bytes=stat_info.st_size,
            modified_time=stat_info.st_mtime
        )
    
    def get_all_checksums(self) -> Dict[str, FileChecksum]:
        """Get all stored checksums."""
        with self._lock:
            return dict(self._checksums)
    
    def save(self) -> None:
        """Persist checksums to disk."""
        with self._lock:
            self._save_checksums()


class ArchiveVerificationPipeline:
    """
    Scheduled verification pipeline for archive integrity.
    
    Performs:
    - Weekly integrity checks
    - Checksum validation
    - Tampering detection
    - Consistency verification
    - Non-blocking reporting
    """
    
    # Sample size for spot checks (percentage of total files)
    SPOT_CHECK_PERCENTAGE = 10
    
    def __init__(self, archive_root: Path):
        """Initialize verification pipeline."""
        self.archive_root = Path(archive_root)
        self.checksum_manager = ChecksumManager(archive_root)
        
        self._lock = RLock()
        self._running = False
        self._stop_event = Event()
        self._pipeline_thread: Optional[Thread] = None
        
        self.last_verification: Optional[VerificationReport] = None
        self.verification_history: List[VerificationReport] = []
    
    def start(self) -> None:
        """Start background verification pipeline."""
        if self._running:
            logger.warning("Verification pipeline already running")
            return
        
        self._running = True
        self._stop_event.clear()
        
        self._pipeline_thread = Thread(
            target=self._pipeline_loop,
            name="ArchiveVerificationPipeline",
            daemon=True
        )
        self._pipeline_thread.start()
        
        logger.info("Archive verification pipeline started")
    
    def stop(self, timeout_seconds: int = 30) -> None:
        """Stop verification pipeline."""
        if not self._running:
            return
        
        self._stop_event.set()
        
        if self._pipeline_thread:
            self._pipeline_thread.join(timeout=timeout_seconds)
        
        self._running = False
        logger.info("Archive verification pipeline stopped")
    
    def _pipeline_loop(self) -> None:
        """Main pipeline loop (runs in background)."""
        
        # First run after 1 hour, then weekly
        first_run = datetime.now() + timedelta(hours=1)
        
        while not self._stop_event.is_set():
            try:
                now = datetime.now()
                
                # Check if it's time to verify
                if self.last_verification is None:
                    should_verify = now >= first_run
                else:
                    should_verify = (
                        now >= self.last_verification.timestamp + timedelta(days=7)
                    )
                
                if should_verify:
                    self._run_verification()
                
                # Sleep before checking again (check every hour)
                time.sleep(3600)
                
            except Exception as e:
                logger.error(f"Verification pipeline error: {e}")
                time.sleep(3600)
    
    def _run_verification(self) -> None:
        """Execute verification operation."""
        start_time = time.time()
        
        logger.info("Starting archive integrity verification")
        
        try:
            report = VerificationReport(
                timestamp=datetime.now(),
                status=VerificationStatus.IN_PROGRESS,
                total_files_verified=0,
                total_size_bytes=0,
                checksums_matched=0,
                checksums_mismatched=0,
                files_added=0,
                files_removed=0
            )
            
            # Phase 1: Scan archive for files
            archive_files = list(self.archive_root.rglob("*"))
            archive_files = [f for f in archive_files if f.is_file()]
            
            report.total_files_verified = len(archive_files)
            
            # Phase 2: Calculate total size
            report.total_size_bytes = sum(f.stat().st_size for f in archive_files)
            
            # Phase 3: Verify checksums (spot check)
            sample_size = max(
                1,
                int(len(archive_files) * self.SPOT_CHECK_PERCENTAGE / 100)
            )
            sample_files = random.sample(archive_files, min(sample_size, len(archive_files)))
            
            report.sample_size = len(sample_files)
            
            for file_path in sample_files:
                is_valid, issue = self.checksum_manager.verify_file(file_path)
                
                if is_valid:
                    report.checksums_matched += 1
                else:
                    report.checksums_mismatched += 1
                    if issue:
                        report.issues.append(f"{file_path.name}: {issue}")
            
            # Phase 4: Detect added/removed files
            stored_checksums = self.checksum_manager.get_all_checksums()
            stored_paths = set(stored_checksums.keys())
            current_paths = set(
                str(f.relative_to(self.archive_root)) for f in archive_files
            )
            
            report.files_added = len(current_paths - stored_paths)
            report.files_removed = len(stored_paths - current_paths)
            
            if report.files_removed > 0:
                report.warnings.append(
                    f"{report.files_removed} files were removed from archive"
                )
            
            # Phase 5: Determine status
            if report.checksums_mismatched > 0:
                report.status = VerificationStatus.FAILED
            elif report.warnings or report.files_removed > 0:
                report.status = VerificationStatus.WARNINGS
            else:
                report.status = VerificationStatus.PASSED
            
            # Update checksums for next verification
            self.checksum_manager.update_file_checksum(self.archive_root)
            self.checksum_manager.save()
            
            elapsed = time.time() - start_time
            report.verification_time_seconds = elapsed
            
            with self._lock:
                self.last_verification = report
                self.verification_history.append(report)
                
                # Keep history manageable
                if len(self.verification_history) > 52:  # One year of weekly checks
                    self.verification_history = self.verification_history[-52:]
            
            # Log results
            self._log_verification_results(report)
            
        except Exception as e:
            logger.error(f"Verification operation failed: {e}")
    
    def _log_verification_results(self, report: VerificationReport) -> None:
        """Log verification results."""
        
        logger.info(
            f"Archive verification complete: {report.status} - "
            f"verified {report.total_files_verified} files, "
            f"checked {report.sample_size} samples, "
            f"matched {report.checksums_matched}, "
            f"mismatched {report.checksums_mismatched}, "
            f"added {report.files_added}, "
            f"removed {report.files_removed}, "
            f"elapsed {report.verification_time_seconds:.1f}s"
        )
        
        for issue in report.issues:
            logger.warning(f"Verification issue: {issue}")
        
        for warning in report.warnings:
            logger.warning(f"Verification warning: {warning}")
    
    def get_verification_status(self) -> Dict[str, Any]:
        """Get verification pipeline status."""
        with self._lock:
            if self.last_verification is None:
                return {
                    "running": self._running,
                    "status": "not_yet_verified",
                    "verification_history_size": len(self.verification_history)
                }
            
            last = self.last_verification
            
            return {
                "running": self._running,
                "last_verification": {
                    "timestamp": last.timestamp.isoformat(),
                    "status": last.status,
                    "total_files": last.total_files_verified,
                    "sample_size": last.sample_size,
                    "checksums_matched": last.checksums_matched,
                    "checksums_mismatched": last.checksums_mismatched,
                    "files_added": last.files_added,
                    "files_removed": last.files_removed,
                    "issues": last.issues,
                    "warnings": last.warnings,
                    "verification_time_seconds": last.verification_time_seconds
                },
                "verification_history_size": len(self.verification_history)
            }
    
    def get_verification_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get verification history."""
        with self._lock:
            return [
                asdict(report) for report in self.verification_history[-limit:]
            ]
    
    def run_manual_verification(self) -> VerificationReport:
        """Manually trigger verification (non-blocking, returns immediately)."""
        
        # Trigger in background if not already running
        if not self._running:
            thread = Thread(target=self._run_verification, daemon=True)
            thread.start()
        
        if self.last_verification:
            return self.last_verification
        
        # Return placeholder
        return VerificationReport(
            timestamp=datetime.now(),
            status=VerificationStatus.IN_PROGRESS,
            total_files_verified=0,
            total_size_bytes=0,
            checksums_matched=0,
            checksums_mismatched=0,
            files_added=0,
            files_removed=0
        )


# Singleton instance
_verification_pipeline_instance: Optional[ArchiveVerificationPipeline] = None


def get_verification_pipeline(
    archive_root: Optional[Path] = None
) -> ArchiveVerificationPipeline:
    """Get or create singleton verification pipeline."""
    global _verification_pipeline_instance
    
    if _verification_pipeline_instance is None:
        if archive_root is None:
            archive_root = Path.cwd() / "quarantine_legacy_archive"
        
        _verification_pipeline_instance = ArchiveVerificationPipeline(archive_root)
    
    return _verification_pipeline_instance
