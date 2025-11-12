"""
Archive Index Maintenance Scheduler

Manages automated maintenance tasks for archival indices including:
- Query performance monitoring
- Cache freshness management
- Index integrity verification
- Decision context enrichment

Author: CodeSentinel
Date: 2025-11-11
"""

import json
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, asdict
import logging
from enum import Enum
from threading import Thread, Event, RLock
import time

from codesentinel.utils.oracl_context_tier import prune_old_context_logs, get_weekly_summaries
from codesentinel.utils.archive_enrichment_pipeline import enrich_from_context_tier

logger = logging.getLogger(__name__)


class TaskPriority(Enum):
    """Task priority levels."""
    LOW = 3
    MEDIUM = 2
    HIGH = 1


class TaskState(Enum):
    """Task execution state."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class MaintenanceTask:
    """Represents a maintenance task."""
    task_id: str
    task_type: str
    priority: TaskPriority
    scheduled_time: datetime
    timeout_seconds: int = 300
    state: TaskState = TaskState.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class MaintenanceScheduler:
    """
    Schedules and manages archival index maintenance tasks.
    
    Supports:
    - Scheduled recurring tasks
    - Priority-based execution
    - Concurrent safe operations
    - Background and in-place processing
    """
    
    # Task definitions with schedules
    TASK_DEFINITIONS = {
        "query_performance_monitoring": {
            "priority": TaskPriority.LOW,
            "frequency_hours": 24,
            "timeout_seconds": 300,
            "description": "Monitor query performance and optimize hot paths"
        },
        "cache_freshness_management": {
            "priority": TaskPriority.LOW,
            "frequency_hours": 6,
            "timeout_seconds": 60,
            "description": "Prune expired cache entries"
        },
        "index_integrity_check": {
            "priority": TaskPriority.MEDIUM,
            "frequency_hours": 168,  # Weekly
            "timeout_seconds": 600,
            "description": "Verify index integrity and detect corruption"
        },
        "decision_context_extraction": {
            "priority": TaskPriority.LOW,
            "frequency_hours": 12,
            "timeout_seconds": 300,
            "description": "Extract agent-usable decision patterns"
        },
        "tier2_to_tier3_promotion": {
            "priority": TaskPriority.MEDIUM,
            "frequency_hours": 168,  # Weekly
            "timeout_seconds": 900,
            "description": "Promote insights from Tier 2 (Context) to Tier 3 (Intelligence)"
        },
        "tier2_log_pruning": {
            "priority": TaskPriority.LOW,
            "frequency_hours": 24, # Daily
            "timeout_seconds": 120,
            "description": "Prune old logs from Tier 2 (Context) to maintain a 7-day window"
        }
    }
    
    def __init__(self, archive_manager):
        """
        Initialize scheduler.
        
        Args:
            archive_manager: ArchiveIndexManager instance
        """
        self.archive_manager = archive_manager
        self.tasks: Dict[str, MaintenanceTask] = {}
        self.task_log: List[Dict[str, Any]] = []
        self._lock = RLock()
        self._running = False
        self._scheduler_thread: Optional[Thread] = None
        self._stop_event = Event()
        self._task_handlers = {
            "query_performance_monitoring": self._handle_performance_monitoring,
            "cache_freshness_management": self._handle_cache_freshness,
            "index_integrity_check": self._handle_integrity_check,
            "decision_context_extraction": self._handle_context_extraction,
            "tier2_to_tier3_promotion": self._handle_tier2_to_tier3_promotion,
            "tier2_log_pruning": self._handle_tier2_log_pruning
        }
    
    def start(self) -> None:
        """Start the maintenance scheduler."""
        if self._running:
            logger.warning("Scheduler already running")
            return
        
        self._running = True
        self._stop_event.clear()
        
        self._scheduler_thread = Thread(
            target=self._scheduler_loop,
            name="ArchiveMaintenanceScheduler",
            daemon=True
        )
        self._scheduler_thread.start()
        
        logger.info("Archive maintenance scheduler started")
    
    def stop(self, timeout_seconds: int = 30) -> None:
        """Stop the maintenance scheduler."""
        if not self._running:
            return
        
        self._stop_event.set()
        
        if self._scheduler_thread:
            self._scheduler_thread.join(timeout=timeout_seconds)
        
        self._running = False
        logger.info("Archive maintenance scheduler stopped")
    
    def _scheduler_loop(self) -> None:
        """Main scheduler loop (runs in background thread)."""
        
        # Initialize task schedules
        next_run_times = self._initialize_schedules()
        
        while not self._stop_event.is_set():
            try:
                now = datetime.now()
                
                # Find tasks that should run
                tasks_to_run = [
                    task_type for task_type, next_time in next_run_times.items()
                    if now >= next_time
                ]
                
                # Execute tasks (highest priority first)
                tasks_to_run.sort(
                    key=lambda t: self.TASK_DEFINITIONS[t]["priority"].value
                )
                
                for task_type in tasks_to_run:
                    try:
                        self._execute_task(task_type)
                        next_run_times[task_type] = self._calculate_next_run_time(
                            task_type
                        )
                    except Exception as e:
                        logger.error(f"Task execution failed: {task_type}: {e}")
                
                # Sleep briefly before checking again
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Scheduler loop error: {e}")
                time.sleep(60)
    
    def _initialize_schedules(self) -> Dict[str, datetime]:
        """Initialize first run times for all tasks."""
        schedules = {}
        now = datetime.now()
        
        for task_type, definition in self.TASK_DEFINITIONS.items():
            # First run: now + frequency (stagger to avoid thundering herd)
            offset_minutes = list(self.TASK_DEFINITIONS.keys()).index(task_type) * 10
            first_run = now + timedelta(minutes=offset_minutes)
            schedules[task_type] = first_run
        
        return schedules
    
    def _calculate_next_run_time(self, task_type: str) -> datetime:
        """Calculate next run time for a task."""
        definition = self.TASK_DEFINITIONS[task_type]
        frequency = timedelta(hours=definition["frequency_hours"])
        
        return datetime.now() + frequency
    
    def _execute_task(self, task_type: str) -> None:
        """Execute a single maintenance task."""
        
        task_id = f"{task_type}_{datetime.now().isoformat()}"
        task = MaintenanceTask(
            task_id=task_id,
            task_type=task_type,
            priority=self.TASK_DEFINITIONS[task_type]["priority"],
            scheduled_time=datetime.now(),
            timeout_seconds=self.TASK_DEFINITIONS[task_type]["timeout_seconds"]
        )
        
        with self._lock:
            self.tasks[task_id] = task
        
        try:
            logger.info(f"Starting maintenance task: {task_type}")
            task.state = TaskState.RUNNING
            task.started_at = datetime.now()
            
            # Execute handler
            handler = self._task_handlers.get(task_type)
            if handler:
                result = handler()
                task.result = result
                task.state = TaskState.COMPLETED
            else:
                task.state = TaskState.SKIPPED
                logger.warning(f"No handler for task: {task_type}")
            
            task.completed_at = datetime.now()
            duration_seconds = (task.completed_at - task.started_at).total_seconds()
            
            logger.info(
                f"Completed maintenance task {task_type} "
                f"(duration: {duration_seconds:.1f}s)"
            )
            
            # Log task
            with self._lock:
                self.task_log.append(asdict(task))
                if len(self.task_log) > 1000:
                    self.task_log = self.task_log[-1000:]
            
        except Exception as e:
            task.state = TaskState.FAILED
            task.error = str(e)
            task.completed_at = datetime.now()
            
            logger.error(f"Maintenance task failed: {task_type}: {e}")
            
            with self._lock:
                self.task_log.append(asdict(task))
    
    def _handle_performance_monitoring(self) -> Dict[str, Any]:
        """Handle query performance monitoring task."""
        analysis = self.archive_manager.get_performance_analysis()
        
        # Log analysis
        logger.info(f"Performance analysis: {json.dumps(analysis, indent=2)}")
        
        return analysis
    
    def _handle_cache_freshness(self) -> Dict[str, Any]:
        """Handle cache freshness management task."""
        pruned = self.archive_manager.maintenance_prune_cache()
        
        logger.info(f"Cache maintenance: pruned {pruned['entries_pruned']} entries")
        
        return pruned
    
    def _handle_integrity_check(self) -> Dict[str, Any]:
        """Handle index integrity verification task."""
        verification = self.archive_manager.maintenance_verify_index()
        
        logger.info(f"Index verification: {verification['status']}")
        
        if verification.get("issues"):
            for issue in verification["issues"]:
                logger.warning(f"Index issue: {issue}")
        
        return verification
    
    def _handle_context_extraction(self) -> Dict[str, Any]:
        """Handle decision context extraction task."""
        
        # Extract context from archive
        decision_contexts = self.archive_manager.query_decision_context(
            context_type="violations",
            limit=100
        )
        
        # Analyze for patterns
        patterns = {}

    def _handle_tier2_to_tier3_promotion(self) -> Dict[str, Any]:
        """
        Handles the promotion of insights from Tier 2 to Tier 3.
        This is a wrapper around the enrichment pipeline functionality.
        """
        logger.info("Starting Tier 2 to Tier 3 promotion task.")
        
        # The core logic is in the enrichment pipeline module to keep concerns separate.
        # The scheduler is only responsible for triggering it.
        result = enrich_from_context_tier(self.archive_manager.workspace_root)
        
        logger.info(f"Tier 2 to Tier 3 promotion task completed. Promoted {result.get('patterns_promoted', 0)} new patterns.")
        return result

    def _handle_tier2_log_pruning(self) -> Dict[str, Any]:
        """
        Handles the daily pruning of old logs from the Tier 2 Context Tier.
        """
        logger.info("Starting Tier 2 log pruning task.")
        
        prune_old_context_logs(self.archive_manager.workspace_root)
        
        # This function doesn't return a detailed dict, so we create one.
        result = {
            "status": "completed",
            "description": "Checked for and pruned old Tier 2 logs."
        }
        logger.info("Tier 2 log pruning task completed.")
        return result
    
    def get_task_status(self, task_id: Optional[str] = None) -> Dict[str, Any]:
        """Get status of task(s)."""
        with self._lock:
            if task_id:
                task = self.tasks.get(task_id)
                return asdict(task) if task else {"error": "Task not found"}
            
            # Return summary
            return {
                "total_tasks": len(self.tasks),
                "running": sum(
                    1 for t in self.tasks.values()
                    if t.state == TaskState.RUNNING
                ),
                "completed": sum(
                    1 for t in self.tasks.values()
                    if t.state == TaskState.COMPLETED
                ),
                "failed": sum(
                    1 for t in self.tasks.values()
                    if t.state == TaskState.FAILED
                ),
                "recent_tasks": [
                    asdict(t) for t in sorted(
                        self.tasks.values(),
                        key=lambda t: t.scheduled_time,
                        reverse=True
                    )[:5]
                ]
            }
    
    def get_task_log(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get task execution log."""
        with self._lock:
            return self.task_log[-limit:]
    
    def get_scheduler_status(self) -> Dict[str, Any]:
        """Get overall scheduler status."""
        return {
            "running": self._running,
            "uptime": "TODO",  # Calculate if started
            "task_definitions": {
                name: {
                    "priority": def_["priority"].name,
                    "frequency_hours": def_["frequency_hours"],
                    "description": def_["description"]
                }
                for name, def_ in self.TASK_DEFINITIONS.items()
            },
            "task_status": self.get_task_status(),
            "recent_tasks": self.get_task_log(10)
        }


# Singleton instance
_scheduler_instance: Optional[MaintenanceScheduler] = None


def get_maintenance_scheduler(
    archive_manager=None
) -> MaintenanceScheduler:
    """Get or create singleton scheduler."""
    global _scheduler_instance
    
    if _scheduler_instance is None:
        if archive_manager is None:
            from .archive_index_manager import get_archive_manager
            archive_manager = get_archive_manager()
        
        _scheduler_instance = MaintenanceScheduler(archive_manager)
    
    return _scheduler_instance
