"""
Archive Enrichment Pipeline

Implements background enrichment of archival records including:
- Pattern discovery (recurring violation patterns)
- Remediation analysis (success/failure rates by violation type)
- Context clustering (grouping similar decisions)
- Insight extraction (actionable patterns for agents)

Runs asynchronously without blocking queries or operations.

Author: CodeSentinel
Date: 2025-11-11
"""

import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, asdict, field
from threading import Thread, RLock, Event
import time
from collections import Counter, defaultdict
from enum import Enum

from codesentinel.utils.archive_decision_provider import get_archive_manager
from codesentinel.utils.oracl_context_tier import get_weekly_summaries

logger = logging.getLogger(__name__)


class PatternType(Enum):
    """Types of patterns that can be discovered."""
    RECURRING_VIOLATION = "recurring_violation"
    REMEDIATION_SUCCESS = "remediation_success"
    REMEDIATION_FAILURE = "remediation_failure"
    DECISION_CLUSTER = "decision_cluster"
    TEMPORAL_TREND = "temporal_trend"


@dataclass
class Pattern:
    """Represents a discovered pattern."""
    pattern_type: PatternType
    name: str
    frequency: int
    confidence: float  # 0-1, based on sample size and consistency
    examples: List[Dict[str, Any]] = field(default_factory=list)
    extracted_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EnrichmentResult:
    """Result of enrichment operation."""
    timestamp: datetime
    patterns_discovered: List[Pattern]
    items_processed: int
    processing_time_seconds: float
    new_insights: int
    status: str


class PatternDiscoveryEngine:
    """
    Discovers patterns in archival records.
    
    Supports:
    - Recurring violation detection
    - Remediation success/failure analysis
    - Temporal trend detection
    - Similarity-based clustering
    """
    
    def __init__(self, archive_index_manager):
        """
        Initialize discovery engine.
        
        Args:
            archive_index_manager: ArchiveIndexManager instance
        """
        self.index_manager = archive_index_manager
        self._lock = RLock()
    
    def discover_patterns(
        self,
        sample_size: int = 1000,
        days_back: int = 90
    ) -> List[Pattern]:
        """
        Discover patterns in archival records.
        
        Args:
            sample_size: Number of records to analyze
            days_back: How many days back to analyze
        
        Returns:
            List of discovered patterns with confidence scores
        """
        patterns = []
        
        # Get decision context from archive
        context_results = self.index_manager.query_decision_context(
            context_type="violations",
            limit=sample_size
        )
        
        records = context_results.get("results", [])
        
        if not records:
            logger.info("No archival records found for pattern discovery")
            return patterns
        
        # Discover different pattern types
        patterns.extend(self._discover_violation_patterns(records))
        patterns.extend(self._discover_remediation_patterns(records))
        patterns.extend(self._discover_temporal_patterns(records))
        patterns.extend(self._discover_clusters(records))
        
        return patterns
    
    def _discover_violation_patterns(
        self,
        records: List[Dict[str, Any]]
    ) -> List[Pattern]:
        """Discover recurring violation patterns."""
        patterns = []
        
        # Count violation types
        violation_counts: Counter = Counter()
        violation_examples: Dict[str, List] = defaultdict(list)
        
        for record in records:
            violation_type = record.get("type", "unknown")
            violation_counts[violation_type] += 1
            
            if len(violation_examples[violation_type]) < 3:
                violation_examples[violation_type].append(record)
        
        # Create patterns for frequent violations
        total_records = len(records)
        
        for violation_type, count in violation_counts.most_common(10):
            frequency_ratio = count / total_records if total_records > 0 else 0
            
            # Confidence based on frequency and sample size
            confidence = min(frequency_ratio * (count / 50), 1.0)
            
            pattern = Pattern(
                pattern_type=PatternType.RECURRING_VIOLATION,
                name=f"Recurring: {violation_type}",
                frequency=count,
                confidence=confidence,
                examples=violation_examples[violation_type],
                metadata={
                    "violation_type": violation_type,
                    "percentage": f"{frequency_ratio*100:.1f}%",
                    "sample_size": total_records
                }
            )
            
            patterns.append(pattern)
        
        return patterns
    
    def _discover_remediation_patterns(
        self,
        records: List[Dict[str, Any]]
    ) -> List[Pattern]:
        """Discover remediation success/failure patterns."""
        patterns = []
        
        # Analyze outcomes by remediation action
        action_outcomes: Dict[str, Dict[str, int]] = defaultdict(lambda: {"success": 0, "failure": 0})
        action_examples: Dict[str, List] = defaultdict(list)
        
        for record in records:
            action = record.get("action", "unknown")
            outcome = record.get("outcome", "unknown")
            
            if outcome in action_outcomes[action]:
                action_outcomes[action][outcome] += 1
            
            if len(action_examples[action]) < 2:
                action_examples[action].append(record)
        
        # Create patterns for high-confidence remediation strategies
        for action, outcomes in action_outcomes.items():
            total = sum(outcomes.values())
            if total < 5:  # Skip low-frequency actions
                continue
            
            success_rate = outcomes.get("success", 0) / total if total > 0 else 0
            
            if success_rate > 0.7:
                pattern_type = PatternType.REMEDIATION_SUCCESS
                name = f"Successful: {action}"
            elif success_rate < 0.3:
                pattern_type = PatternType.REMEDIATION_FAILURE
                name = f"Problematic: {action}"
            else:
                continue  # Skip moderate patterns
            
            # Confidence based on success consistency and sample size
            consistency = abs(success_rate - 0.5) * 2  # 0-1, high for extreme ratios
            sample_confidence = min(total / 20, 1.0)
            confidence = (consistency * 0.6) + (sample_confidence * 0.4)
            
            pattern = Pattern(
                pattern_type=pattern_type,
                name=name,
                frequency=total,
                confidence=confidence,
                examples=action_examples[action],
                metadata={
                    "action": action,
                    "success_count": outcomes.get("success", 0),
                    "failure_count": outcomes.get("failure", 0),
                    "success_rate": f"{success_rate*100:.1f}%"
                }
            )
            
            patterns.append(pattern)
        
        return patterns
    
    def _discover_temporal_patterns(
        self,
        records: List[Dict[str, Any]]
    ) -> List[Pattern]:
        """Discover temporal trends."""
        patterns = []
        
        # Parse timestamps and group by time period
        daily_counts = defaultdict(int)
        
        for record in records:
            try:
                timestamp = datetime.fromisoformat(
                    record.get("timestamp", "")
                )
                date_key = timestamp.date().isoformat()
                daily_counts[date_key] += 1
            except (ValueError, AttributeError):
                pass
        
        if len(daily_counts) < 5:
            return patterns
        
        # Detect trends
        dates = sorted(daily_counts.keys())
        recent_avg = sum(daily_counts[d] for d in dates[-7:]) / 7 if dates[-7:] else 0
        earlier_avg = sum(daily_counts[d] for d in dates[:7]) / 7 if dates[:7] else 0
        
        if recent_avg > 0 and earlier_avg > 0:
            trend_ratio = recent_avg / earlier_avg
            
            if trend_ratio > 1.5:
                trend = "increasing"
            elif trend_ratio < 0.67:
                trend = "decreasing"
            else:
                trend = None
            
            if trend:
                pattern = Pattern(
                    pattern_type=PatternType.TEMPORAL_TREND,
                    name=f"Trend: {trend} violations",
                    frequency=int(recent_avg),
                    confidence=0.5,  # Moderate confidence for trends
                    metadata={
                        "trend": trend,
                        "recent_avg": f"{recent_avg:.1f}",
                        "earlier_avg": f"{earlier_avg:.1f}",
                        "ratio": f"{trend_ratio:.2f}x"
                    }
                )
                
                patterns.append(pattern)
        
        return patterns
    
    def _discover_clusters(
        self,
        records: List[Dict[str, Any]]
    ) -> List[Pattern]:
        """Discover decision clusters (similar decisions grouped)."""
        patterns = []
        
        # Simple clustering: group by violation type and outcome
        clusters = defaultdict(list)
        
        for record in records:
            key = (
                record.get("type", "unknown"),
                record.get("outcome", "unknown")
            )
            clusters[key].append(record)
        
        # Create patterns for large, homogeneous clusters
        for (violation_type, outcome), cluster_records in clusters.items():
            if len(cluster_records) < 5:
                continue
            
            # Confidence based on cluster size and homogeneity
            size_confidence = min(len(cluster_records) / 20, 1.0)
            homogeneity = 0.8  # Assumed for same type/outcome
            confidence = (size_confidence * 0.5) + (homogeneity * 0.5)
            
            pattern = Pattern(
                pattern_type=PatternType.DECISION_CLUSTER,
                name=f"Cluster: {violation_type} → {outcome}",
                frequency=len(cluster_records),
                confidence=confidence,
                examples=cluster_records[:3],
                metadata={
                    "violation_type": violation_type,
                    "outcome": outcome,
                    "cluster_size": len(cluster_records)
                }
            )
            
            patterns.append(pattern)
        
        return patterns


def enrich_from_context_tier(workspace_root: Path) -> Dict[str, Any]:
    """
    Analyzes the last 7 days of session summaries from Tier 2 to discover
    and promote new patterns to Tier 3.

    This is the core logic for the Tier 2 -> Tier 3 promotion task.

    Args:
        workspace_root: The root of the current workspace.

    Returns:
        A dictionary summarizing the enrichment results.
    """
    start_time = time.time()
    logger.info("Starting enrichment from Tier 2 context.")

    # 1. Get weekly summaries from Tier 2
    weekly_summaries = get_weekly_summaries(workspace_root)
    if not weekly_summaries:
        logger.info("No weekly summaries found in Tier 2. Nothing to promote.")
        return {"status": "completed", "patterns_promoted": 0, "items_processed": 0}

    # 2. Transform summaries into a format the discovery engine can use
    # This is a simplified transformation. A real implementation might be more complex.
    records_for_discovery = []
    for summary in weekly_summaries:
        for decision in summary.get("key_decisions", []):
            records_for_discovery.append({
                "type": decision.get("decision", "unknown"),
                "action": "analysis", # Placeholder
                "outcome": summary.get("outcome", "unknown"),
                "timestamp": summary.get("timestamp")
            })

    # 3. Discover patterns using a temporary discovery engine instance
    # We create a temporary one to avoid state conflicts with the main pipeline.
    temp_discovery_engine = PatternDiscoveryEngine(get_archive_manager())
    discovered_patterns = temp_discovery_engine._discover_remediation_patterns(records_for_discovery)

    # 4. Promote high-confidence patterns to the ORACL™ archive (Tier 3)
    patterns_promoted = 0
    archive_manager = get_archive_manager()
    for pattern in discovered_patterns:
        if pattern.confidence >= 0.75: # Stricter confidence for promotion
            # The `add_strategic_insight` method needs to be implemented in the archive manager
            # For now, we assume it exists.
            if hasattr(archive_manager, 'add_strategic_insight'):
                archive_manager.add_strategic_insight(pattern)
                patterns_promoted += 1
                logger.debug(f"Promoted pattern '{pattern.name}' to Tier 3 with confidence {pattern.confidence:.2f}.")

    end_time = time.time()
    result = {
        "status": "completed",
        "patterns_promoted": patterns_promoted,
        "items_processed": len(weekly_summaries),
        "processing_time_seconds": end_time - start_time,
    }
    logger.info(f"Enrichment from Tier 2 completed. Promoted {patterns_promoted} patterns.")
    return result


class ArchiveEnrichmentPipeline:
    """
    Background enrichment pipeline for archival records.
    
    Runs asynchronously, enriching archive with:
    - Discovered patterns
    - Success/failure analysis
    - Similarity clustering
    - Actionable insights
    """
    
    def __init__(self, archive_index_manager):
        """Initialize pipeline."""
        self.index_manager = archive_index_manager
        self.discovery_engine = PatternDiscoveryEngine(archive_index_manager)
        
        self._lock = RLock()
        self._running = False
        self._stop_event = Event()
        self._pipeline_thread: Optional[Thread] = None
        
        self.last_enrichment: Optional[EnrichmentResult] = None
        self.enrichment_history: List[EnrichmentResult] = []
    
    def start(self) -> None:
        """Start background enrichment pipeline."""
        if self._running:
            logger.warning("Enrichment pipeline already running")
            return
        
        self._running = True
        self._stop_event.clear()
        
        self._pipeline_thread = Thread(
            target=self._pipeline_loop,
            name="ArchiveEnrichmentPipeline",
            daemon=True
        )
        self._pipeline_thread.start()
        
        logger.info("Archive enrichment pipeline started")
    
    def stop(self, timeout_seconds: int = 10) -> None:
        """Stop enrichment pipeline."""
        if not self._running:
            return
        
        self._stop_event.set()
        
        if self._pipeline_thread:
            self._pipeline_thread.join(timeout=timeout_seconds)
        
        self._running = False
        logger.info("Archive enrichment pipeline stopped")
    
    def _pipeline_loop(self) -> None:
        """Main pipeline loop (runs in background)."""
        
        # First run after 5 minutes, then every 30 minutes
        first_run = datetime.now() + timedelta(minutes=5)
        
        while not self._stop_event.is_set():
            try:
                now = datetime.now()
                
                # Check if it's time to enrich
                if self.last_enrichment is None:
                    should_enrich = now >= first_run
                else:
                    should_enrich = (
                        now >= self.last_enrichment.timestamp + timedelta(minutes=30)
                    )
                
                if should_enrich:
                    self._run_enrichment()
                
                # Sleep before checking again
                time.sleep(60)
                
            except Exception as e:
                logger.error(f"Enrichment pipeline error: {e}")
                time.sleep(60)
    
    def _run_enrichment(self) -> None:
        """Execute enrichment operation."""
        start_time = time.time()
        
        try:
            logger.info("Starting archive enrichment cycle")
            
            # Discover patterns
            patterns = self.discovery_engine.discover_patterns(
                sample_size=1000,
                days_back=90
            )
            
            # Process and store patterns
            new_insights = self._process_patterns(patterns)
            
            elapsed = time.time() - start_time
            
            result = EnrichmentResult(
                timestamp=datetime.now(),
                patterns_discovered=patterns,
                items_processed=1000,
                processing_time_seconds=elapsed,
                new_insights=new_insights,
                status="success"
            )
            
            with self._lock:
                self.last_enrichment = result
                self.enrichment_history.append(result)
                
                # Keep history manageable
                if len(self.enrichment_history) > 100:
                    self.enrichment_history = self.enrichment_history[-100:]
            
            logger.info(
                f"Enrichment cycle complete: "
                f"discovered {len(patterns)} patterns, "
                f"{new_insights} new insights, "
                f"elapsed {elapsed:.1f}s"
            )
            
        except Exception as e:
            logger.error(f"Enrichment operation failed: {e}")
    
    def _process_patterns(self, patterns: List[Pattern]) -> int:
        """
        Process discovered patterns.
        
        Returns:
            Number of new insights added
        """
        new_insights = 0
        
        for pattern in patterns:
            # Here you would typically:
            # 1. Store pattern metadata to archive
            # 2. Generate recommendations
            # 3. Alert on critical patterns
            
            logger.info(
                f"Pattern discovered: {pattern.name} "
                f"(confidence: {pattern.confidence:.2f}, "
                f"frequency: {pattern.frequency})"
            )
            
            # Count as new insight
            if pattern.confidence >= 0.7:
                new_insights += 1
        
        return new_insights
    
    def get_recent_patterns(self, limit: int = 10) -> List[Pattern]:
        """Get most recent discovered patterns."""
        if self.last_enrichment is None:
            return []
        
        # Sort by confidence descending
        patterns = sorted(
            self.last_enrichment.patterns_discovered,
            key=lambda p: p.confidence,
            reverse=True
        )
        
        return patterns[:limit]
    
    def get_enrichment_status(self) -> Dict[str, Any]:
        """Get enrichment pipeline status."""
        with self._lock:
            if self.last_enrichment is None:
                return {
                    "running": self._running,
                    "status": "not_yet_enriched",
                    "enrichment_history_size": len(self.enrichment_history)
                }
            
            return {
                "running": self._running,
                "last_enrichment": {
                    "timestamp": self.last_enrichment.timestamp.isoformat(),
                    "patterns_discovered": len(self.last_enrichment.patterns_discovered),
                    "new_insights": self.last_enrichment.new_insights,
                    "processing_time_seconds": self.last_enrichment.processing_time_seconds
                },
                "enrichment_history_size": len(self.enrichment_history),
                "recent_patterns": [
                    {
                        "name": p.name,
                        "confidence": p.confidence,
                        "frequency": p.frequency
                    }
                    for p in self.get_recent_patterns(5)
                ]
            }


# Singleton instance
_pipeline_instance: Optional[ArchiveEnrichmentPipeline] = None


def get_enrichment_pipeline(
    archive_index_manager=None
) -> ArchiveEnrichmentPipeline:
    """Get or create singleton enrichment pipeline."""
    global _pipeline_instance
    
    if _pipeline_instance is None:
        if archive_index_manager is None:
            from .archive_index_manager import get_archive_manager
            archive_index_manager = get_archive_manager()
        
        _pipeline_instance = ArchiveEnrichmentPipeline(archive_index_manager)
    
    return _pipeline_instance
