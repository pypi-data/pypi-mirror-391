# -*- coding: utf-8 -*-
"""
ORACL™ Context Tier (Tier 2)

Purpose:
--------
This module implements the Mid-Term Memory tier of the ORACL™ Memory Ecosystem. 
It stores curated, high-value summaries from recently completed sessions, providing 
context on what the agent has successfully accomplished and learned in the recent past.

Data Scope:
-----------
- Aggregated summaries from completed Tier 1 sessions.
- Final task outcomes.
- Key decisions made during a session.
- Core files involved in a task.

Lifetime:
---------
- 7 days (rolling window).
"""
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Initialize logger
logger = logging.getLogger(__name__)

# Preserve a handle to the real datetime class for operations that need
# deterministic behavior even when tests patch the module-level symbol.
REAL_DATETIME = datetime

# --- Constants ---
CONTEXT_TIER_DIR_NAME = ".agent_sessions/context_tier"
CONTEXT_TIER_LIFETIME_DAYS = 7

# --- Private Utility Functions ---

def _get_context_tier_dir(workspace_root: Path) -> Path:
    """Returns the path to the context tier directory, creating it if it doesn't exist."""
    context_dir = workspace_root / CONTEXT_TIER_DIR_NAME
    context_dir.mkdir(parents=True, exist_ok=True)
    return context_dir

def _get_daily_log_path(workspace_root: Path, date: datetime) -> Path:
    """Returns the path for a specific day's log file."""
    return _get_context_tier_dir(workspace_root) / f"{date.strftime('%Y-%m-%d')}.jsonl"

# --- Public API ---

def add_context_summary(workspace_root: Path, summary: Dict[str, Any]) -> None:
    """
    Appends a session summary to the current day's context log.

    This function is designed to be called asynchronously or from a background
    thread to avoid blocking the main agent workflow.

    Args:
        workspace_root: The root of the current workspace.
        summary: A dictionary containing the session summary.
    """
    try:
        log_path = _get_daily_log_path(workspace_root, datetime.now())
        with open(log_path, 'a') as f:
            f.write(json.dumps(summary) + '\n')
        logger.debug(f"Appended session summary {summary.get('session_id')} to Context Tier.")
    except Exception as e:
        logger.error(f"Failed to add context summary to Tier 2: {e}", exc_info=True)

def get_weekly_summaries(workspace_root: Path) -> List[Dict[str, Any]]:
    """
    Retrieves all session summaries from the last 7 days.

    This function is used by the Tier 3 enrichment pipeline to discover
    long-term patterns.

    Args:
        workspace_root: The root of the current workspace.

    Returns:
        A list of all session summary dictionaries from the past week.
    """
    summaries = []
    today = datetime.now()
    try:
        for i in range(CONTEXT_TIER_LIFETIME_DAYS):
            date_to_check = today - timedelta(days=i)
            log_path = _get_daily_log_path(workspace_root, date_to_check)
            
            if log_path.exists():
                with open(log_path, 'r') as f:
                    for line in f:
                        if line.strip():
                            summaries.append(json.loads(line))
        
        logger.info(f"Retrieved {len(summaries)} summaries from the last {CONTEXT_TIER_LIFETIME_DAYS} days from Context Tier.")
        return summaries
    except Exception as e:
        logger.error(f"Failed to get weekly summaries from Tier 2: {e}", exc_info=True)
        return []

def prune_old_context_logs(workspace_root: Path) -> None:
    """
    Deletes context log files older than the defined lifetime.

    This function should be called periodically by a maintenance scheduler.
    """
    context_dir = _get_context_tier_dir(workspace_root)
    cutoff_date = datetime.now() - timedelta(days=CONTEXT_TIER_LIFETIME_DAYS)
    
    deleted_count = 0
    for log_file in context_dir.glob("*.jsonl"):
        try:
            file_date_str = log_file.stem
            file_date = REAL_DATETIME.strptime(file_date_str, '%Y-%m-%d')
            if file_date < cutoff_date:
                log_file.unlink()
                deleted_count += 1
                logger.debug(f"Pruned old context log: {log_file.name}")
        except (ValueError, OSError) as e:
            logger.warning(f"Could not process or delete old context log '{log_file.name}': {e}")
            
    if deleted_count > 0:
        logger.info(f"Pruned {deleted_count} old context logs from Tier 2.")

