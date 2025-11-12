"""
Session Memory Management for CodeSentinel Agent.

Provides short-term task context caching to reduce re-reading and re-analysis
during multi-step agent operations. Implements file context caching, decision
logging, and task state persistence.

This module follows existing patterns from scheduler.py for state management.
"""

import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
import atexit
import threading

from .oracl_context_tier import add_context_summary

logger = logging.getLogger(__name__)


class SessionMemory:
    """
    Short-term task context cache for agent efficiency.
    
    Stores:
    - Task state (current todos and their status)
    - File context (parsed structures, summaries, hashes)
    - Decision log (recent analysis decisions)
    - Config state (last-loaded configuration values)
    
    Auto-invalidates after 60 minutes of inactivity.
    """
    
    def __init__(self, workspace_root: Optional[Path] = None):
        """Initialize session memory."""
        if workspace_root is None:
            workspace_root = Path.cwd()
        
        self.workspace_root = Path(workspace_root)
        self.cache_dir = self.workspace_root / ".agent_session"
        self.task_state_file = self.cache_dir / "task_state.md"
        self.context_file = self.cache_dir / "context_cache.json"
        self.decision_file = self.cache_dir / "decision_log.md"
        self.metadata_file = self.cache_dir / "metadata.json"
        
        # In-memory cache (for current session only)
        self._file_cache = {}  # {path: {hash, summary, timestamp}}
        self._decisions = []   # [{decision, rationale, timestamp}]
        self._tasks = []       # [{id, title, status, timestamp}]
        
        # Configuration
        self.MAX_CACHE_ENTRIES = 50
        self.MAX_CACHE_SIZE_MB = 5
        self.CACHE_TTL_MINUTES = 60
        
        # Unique ID for this session
        self.session_id = f"{datetime.now().strftime('%Y%m%d%H%M%S')}-{Path.cwd().name}"

        # Initialize cache directory
        self._init_cache_dir()
        
        # Load existing session if valid
        self._load_session()

        # Register persistence and promotion on exit
        self._register_exit_handler()

    def _register_exit_handler(self):
        """Register persistence and promotion logic to run on script exit."""
        atexit.register(self.persist)
        atexit.register(self.promote_session_to_context)

    def is_task_successful(self) -> bool:
        """
        Determine if the overall task was successful.
        
        For now, success is defined as having at least one 'completed' task
        and no 'in-progress' tasks.
        """
        if not self._tasks:
            return False
        
        has_completed = any(t.get('status') == 'completed' for t in self._tasks)
        has_in_progress = any(t.get('status') == 'in-progress' for t in self._tasks)
        
        return has_completed and not has_in_progress

    def has_significant_decisions(self, min_decisions: int = 2) -> bool:
        """Check if the session contains a minimum number of decisions."""
        return len(self._decisions) >= min_decisions

    def get_most_accessed_files(self, limit: int = 3) -> List[str]:
        """Get the most frequently accessed files from the cache history."""
        # This is a simple proxy for access frequency.
        # A more robust implementation would track access counts.
        sorted_files = sorted(self._file_cache.items(), key=lambda x: x[1]['timestamp'], reverse=True)
        return [path for path, _ in sorted_files[:limit]]

    def promote_session_to_context(self) -> None:
        """
        Extracts a high-level summary and sends it to the Context Tier (Tier 2).
        
        This is designed to be called on exit, and runs in a background thread
        to avoid blocking the main process.
        """
        def promotion_task():
            if not self.is_task_successful() or not self.has_significant_decisions():
                logger.debug("Session not eligible for promotion to Tier 2.")
                return

            summary = {
                "session_id": self.session_id,
                "timestamp": datetime.now().isoformat(),
                "outcome": "success",
                "task_summary": self.get_task_summary(),
                "key_decisions": self.get_recent_decisions(limit=5),
                "critical_files": self.get_most_accessed_files(limit=3)
            }
            
            try:
                add_context_summary(self.workspace_root, summary)
                logger.debug(f"Successfully promoted session {self.session_id} to Tier 2.")
            except Exception as e:
                logger.error(f"Error during session promotion to Tier 2: {e}", exc_info=True)

        # Run promotion in a non-daemon thread to ensure it completes on exit
        promo_thread = threading.Thread(target=promotion_task, daemon=False)

        # Test doubles may execute the promotion_task immediately and return None.
        if hasattr(promo_thread, "start"):
            promo_thread.start()
        else:  # pragma: no cover - defensive path for patched thread factories
            logger.debug("Promotion thread factory executed synchronously; no thread started.")

    def _init_cache_dir(self) -> None:
        """Create cache directory if it doesn't exist."""
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.warning(f"Failed to create session cache directory: {e}")
    
    def _get_file_hash(self, file_path: Path) -> str:
        """Compute hash of file for change detection."""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return ""
    
    def _load_session(self) -> None:
        """Load existing session data if valid (not stale)."""
        try:
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r') as f:
                    metadata = json.load(f)
                
                # Check if session is stale
                session_age = datetime.now() - datetime.fromisoformat(metadata.get('created', ''))
                if session_age > timedelta(minutes=self.CACHE_TTL_MINUTES):
                    logger.debug(f"Session cache stale ({session_age.total_seconds() / 60:.0f} min old), discarding")
                    self._clear_session_files()
                    return
                
                # Load context cache
                if self.context_file.exists():
                    with open(self.context_file, 'r') as f:
                        self._file_cache = json.load(f)
                
                # Load decision log (parse from markdown)
                if self.decision_file.exists():
                    with open(self.decision_file, 'r') as f:
                        self._load_decisions_from_md(f.read())
                
                logger.debug(f"Loaded session cache: {len(self._file_cache)} files, {len(self._decisions)} decisions")
        except Exception as e:
            logger.warning(f"Failed to load session: {e}")
    
    def _load_decisions_from_md(self, content: str) -> None:
        """Parse decisions from markdown decision log."""
        lines = content.split('\n')
        current_decision = {}
        
        for line in lines:
            if line.startswith('## '):
                # Decision entry header
                if current_decision and 'decision' in current_decision:
                    self._decisions.append(current_decision)
                current_decision = {'decision': line[3:].strip()}
            elif line.startswith('**Rationale**:'):
                current_decision['rationale'] = line.split(':', 1)[1].strip()
            elif line.startswith('**Time**:'):
                current_decision['timestamp'] = line.split(':', 1)[1].strip()
        
        if current_decision and 'decision' in current_decision:
            self._decisions.append(current_decision)
    
    def save_task_state(self, tasks: List[Dict[str, Any]]) -> None:
        """
        Persist current task list.
        
        Args:
            tasks: List of task dicts with id, title, status, description
        """
        try:
            self._tasks = tasks
            content = "# Session Tasks\n\n"
            
            for task in tasks:
                status_symbol = {
                    'completed': '[OK]',
                    'in-progress': '[RUN]',
                    'not-started': '[WAIT]'
                }.get(task.get('status', 'not-started'), '[UNKNOWN]')
                
                content += f"## {status_symbol} {task.get('title', 'Untitled')}\n"
                content += f"- **Status**: {task.get('status', 'unknown')}\n"
                content += f"- **ID**: {task.get('id', 'N/A')}\n"
                if task.get('description'):
                    content += f"- **Description**: {task['description']}\n"
                content += "\n"
            
            with open(self.task_state_file, 'w') as f:
                f.write(content)
            
            logger.debug(f"Saved task state: {len(tasks)} tasks")
        except Exception as e:
            logger.warning(f"Failed to save task state: {e}")
    
    def save_file_context(self, file_path: str, summary: str, is_config: bool = False) -> None:
        """
        Cache parsed file structure to avoid re-reading.
        
        Args:
            file_path: Path to file being cached
            summary: Brief summary of file content/structure
            is_config: Whether this is a configuration file (special handling)
        """
        try:
            file_path_obj = Path(file_path)
            
            # Skip if file doesn't exist or is too large
            try:
                if file_path_obj.stat().st_size > 1_000_000:  # 1MB limit per file
                    return
            except OSError:
                return
            
            # Compute file hash for change detection
            file_hash = self._get_file_hash(file_path_obj)
            if not file_hash:
                return
            
            # Store in cache
            self._file_cache[file_path] = {
                'hash': file_hash,
                'summary': summary,
                'is_config': is_config,
                'timestamp': datetime.now().isoformat()
            }
            
            # Enforce cache size limits
            if len(self._file_cache) > self.MAX_CACHE_ENTRIES:
                # Remove oldest entry
                oldest = min(self._file_cache.items(), key=lambda x: x[1]['timestamp'])
                del self._file_cache[oldest[0]]
            
            logger.debug(f"Cached file context: {file_path} ({len(self._file_cache)} cached)")
        except Exception as e:
            logger.warning(f"Failed to cache file context for {file_path}: {e}")
    
    def get_file_context(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached file context if still valid.
        
        Returns None if file has been modified since cache.
        """
        try:
            if file_path not in self._file_cache:
                return None
            
            cached = self._file_cache[file_path]
            file_path_obj = Path(file_path)
            
            # Verify file still exists and hasn't changed
            current_hash = self._get_file_hash(file_path_obj)
            if current_hash != cached['hash']:
                del self._file_cache[file_path]
                return None
            
            return cached
        except Exception:
            return None
    
    def log_decision(self, decision: str, rationale: str) -> None:
        """
        Log a recent analysis decision.
        
        Args:
            decision: The decision made (e.g., "Config structure is alerts.{channel}, not alerts.channels")
            rationale: Why this decision was made
        """
        try:
            entry = {
                'decision': decision,
                'rationale': rationale,
                'timestamp': datetime.now().isoformat()
            }
            self._decisions.append(entry)
            
            # Append to markdown file
            with open(self.decision_file, 'a') as f:
                f.write(f"\n## {decision}\n")
                f.write(f"**Rationale**: {rationale}\n")
                f.write(f"**Time**: {entry['timestamp']}\n")
            
            logger.debug(f"Logged decision: {decision}")
        except Exception as e:
            logger.warning(f"Failed to log decision: {e}")
    
    def get_recent_decisions(self, limit: int = 10) -> List[Dict[str, str]]:
        """Retrieve recent analysis decisions."""
        return self._decisions[-limit:]
    
    def get_task_summary(self) -> str:
        """Generate summary of current task state for agent context."""
        if not self._tasks:
            return "No active tasks"
        
        completed = sum(1 for t in self._tasks if t.get('status') == 'completed')
        in_progress = sum(1 for t in self._tasks if t.get('status') == 'in-progress')
        not_started = sum(1 for t in self._tasks if t.get('status') == 'not-started')
        
        summary = f"Tasks: {completed} completed, {in_progress} in-progress, {not_started} not-started\n"
        
        if in_progress:
            active = [t for t in self._tasks if t.get('status') == 'in-progress']
            summary += f"Currently working on: {', '.join(t.get('title', 'Unknown') for t in active[:3])}"
        
        return summary
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get statistics about cache usage."""
        try:
            # Calculate actual disk usage
            disk_usage = 0
            file_count = 0
            
            if self.cache_dir.exists():
                for f in self.cache_dir.glob('*'):
                    if f.is_file():
                        disk_usage += f.stat().st_size
                        file_count += 1
            
            return {
                'cached_files': len(self._file_cache),
                'logged_decisions': len(self._decisions),
                'tasks_tracked': len(self._tasks),
                'cache_files': file_count,
                'disk_usage_bytes': disk_usage,
                'cache_dir': str(self.cache_dir),
                'ttl_minutes': self.CACHE_TTL_MINUTES
            }
        except Exception as e:
            logger.warning(f"Failed to get cache stats: {e}")
            return {}
    
    def persist(self) -> None:
        """Persist current session state to disk."""
        try:
            # Save metadata
            metadata = {
                'created': datetime.now().isoformat(),
                'files_cached': len(self._file_cache),
                'decisions_logged': len(self._decisions),
                'tasks_tracked': len(self._tasks),
                'ttl_minutes': self.CACHE_TTL_MINUTES
            }
            
            with open(self.metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # Save file context cache
            if self._file_cache:
                with open(self.context_file, 'w') as f:
                    json.dump(self._file_cache, f, indent=2)
            
            logger.debug("Session state persisted to disk")
        except Exception as e:
            logger.warning(f"Failed to persist session state: {e}")
    
    def invalidate_if_stale(self, max_age_minutes: Optional[int] = None) -> bool:
        """
        Check if session is stale and invalidate if so.
        
        Returns:
            True if session was invalidated, False otherwise
        """
        if max_age_minutes is None:
            max_age_minutes = self.CACHE_TTL_MINUTES
        
        try:
            if not self.metadata_file.exists():
                return False
            
            with open(self.metadata_file, 'r') as f:
                metadata = json.load(f)
            
            session_age = datetime.now() - datetime.fromisoformat(metadata['created'])
            if session_age > timedelta(minutes=max_age_minutes):
                logger.info(f"Session cache stale ({session_age.total_seconds() / 60:.0f} min old), invalidating")
                self._clear_session_files()
                return True
            
            return False
        except Exception as e:
            logger.warning(f"Failed to check session staleness: {e}")
            return False
    
    def _clear_session_files(self) -> None:
        """Remove all session cache files."""
        try:
            if self.cache_dir.exists():
                for f in self.cache_dir.glob('*'):
                    if f.is_file():
                        f.unlink()
                logger.debug("Session cache cleared")
        except Exception as e:
            logger.warning(f"Failed to clear session cache: {e}")
    
    def cleanup(self) -> None:
        """Purge session memory at end of work."""
        try:
            self._clear_session_files()
            self._file_cache.clear()
            self._decisions.clear()
            self._tasks.clear()
            logger.debug("Session memory cleaned up")
        except Exception as e:
            logger.warning(f"Failed to cleanup session memory: {e}")
