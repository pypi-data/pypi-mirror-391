"""
Archive Index Manager

Manages efficient access to historical archival records for agent decision-making.
Implements in-place and background processing pipelines with intelligent caching.

Author: CodeSentinel
Date: 2025-11-11
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, TYPE_CHECKING
from dataclasses import dataclass, asdict
from threading import RLock
from collections import defaultdict
import logging

if TYPE_CHECKING:
    from .archive_enrichment_pipeline import Pattern

logger = logging.getLogger(__name__)


@dataclass
class QueryMetric:
    """Represents a single query metric."""
    timestamp: str
    query_type: str
    latency_ms: float
    cache_hit: bool
    result_count: int = 0


@dataclass
class ArchiveStats:
    """Archive statistics and metadata."""
    created_timestamp: str
    last_updated: str
    total_files: int
    total_directories: int
    total_size_bytes: int
    file_types: Dict[str, int]


class CacheManager:
    """Manages query result caching with TTL-based expiration."""
    
    DEFAULT_TTL_SECONDS = 3600  # 1 hour
    
    def __init__(self):
        self.cache = {}
        self.timestamps = {}
        self._lock = RLock()
    
    def get(self, key: str, ttl_override_seconds: Optional[int] = None) -> Optional[Any]:
        """
        Retrieve from cache if fresh.
        
        Args:
            key: Cache key
            ttl_override_seconds: Optional TTL override
        
        Returns:
            Cached value or None if missing/expired
        """
        with self._lock:
            if key not in self.cache:
                return None
            
            ttl = ttl_override_seconds or self.DEFAULT_TTL_SECONDS
            age_seconds = (datetime.now() - self.timestamps[key]).total_seconds()
            
            if age_seconds > ttl:
                del self.cache[key]
                del self.timestamps[key]
                return None
            
            return self.cache[key]
    
    def set(self, key: str, value: Any) -> None:
        """Store in cache with timestamp."""
        with self._lock:
            self.cache[key] = value
            self.timestamps[key] = datetime.now()
    
    def prune_expired(self) -> int:
        """Remove all expired entries. Returns count of pruned entries."""
        with self._lock:
            now = datetime.now()
            expired_keys = [
                key for key in self.cache.keys()
                if (now - self.timestamps[key]).total_seconds() > self.DEFAULT_TTL_SECONDS
            ]
            
            for key in expired_keys:
                del self.cache[key]
                del self.timestamps[key]
            
            return len(expired_keys)
    
    def clear(self) -> None:
        """Clear entire cache."""
        with self._lock:
            self.cache.clear()
            self.timestamps.clear()
    
    def stats(self) -> Dict[str, int]:
        """Return cache statistics."""
        with self._lock:
            return {
                "entries": len(self.cache),
                "estimated_size_kb": sum(
                    len(str(v).encode()) for v in self.cache.values()
                ) // 1024
            }


class QueryPerformanceMonitor:
    """Tracks query performance metrics for optimization."""
    
    def __init__(self, max_metrics: int = 10000):
        self.metrics: List[QueryMetric] = []
        self.max_metrics = max_metrics
        self._lock = RLock()
    
    def log_query(
        self,
        query_type: str,
        latency_ms: float,
        cache_hit: bool,
        result_count: int = 0
    ) -> None:
        """Log a query execution."""
        with self._lock:
            metric = QueryMetric(
                timestamp=datetime.now().isoformat(),
                query_type=query_type,
                latency_ms=latency_ms,
                cache_hit=cache_hit,
                result_count=result_count
            )
            self.metrics.append(metric)
            
            # Keep bounded size
            if len(self.metrics) > self.max_metrics:
                self.metrics = self.metrics[-self.max_metrics:]
    
    def analyze(self) -> Dict[str, Any]:
        """Generate performance analysis."""
        with self._lock:
            if not self.metrics:
                return {"status": "no_metrics"}
            
            by_type = defaultdict(list)
            for metric in self.metrics:
                by_type[metric.query_type].append(metric)
            
            analysis = {}
            for query_type, metrics in by_type.items():
                latencies = [m.latency_ms for m in metrics]
                cache_hits = sum(1 for m in metrics if m.cache_hit)
                
                analysis[query_type] = {
                    "query_count": len(metrics),
                    "cache_hit_rate": (cache_hits / len(metrics)) * 100,
                    "avg_latency_ms": sum(latencies) / len(latencies),
                    "p95_latency_ms": sorted(latencies)[int(len(latencies) * 0.95)],
                    "p99_latency_ms": sorted(latencies)[int(len(latencies) * 0.99)],
                    "slow_queries": sum(1 for l in latencies if l > 100)
                }
            
            return analysis
    
    def get_slow_queries(self, threshold_ms: float = 100) -> List[QueryMetric]:
        """Return queries exceeding latency threshold."""
        with self._lock:
            return [m for m in self.metrics if m.latency_ms > threshold_ms]


class ArchiveIndexManager:
    """
    Main manager for archival record indexing and access.
    
    Provides:
    - Fast file/record lookup
    - Query caching
    - Performance monitoring
    - Index maintenance coordination
    """
    
    def __init__(self, archive_root: Path):
        self.archive_root = Path(archive_root)
        self.index_file = self.archive_root / "ARCHIVE_INDEX.json"
        self.metadata_file = self.archive_root / "INDEX_METADATA.json"
        
        self.cache = CacheManager()
        self.performance_monitor = QueryPerformanceMonitor()
        
        self._index: Dict[str, Any] = {}
        self._metadata: Dict[str, Any] = {}
        self._lock = RLock()
        
        self._load_index()
        self._load_metadata()
    
    def _load_index(self) -> None:
        """Load index from disk."""
        if not self.index_file.exists():
            logger.warning(f"Index file not found: {self.index_file}")
            self._index = {}
            return
        
        try:
            with open(self.index_file, 'r') as f:
                self._index = json.load(f)
            logger.info(f"Loaded archive index with {len(self._index)} entries")
        except Exception as e:
            logger.error(f"Failed to load index: {e}")
            self._index = {}
    
    def _load_metadata(self) -> None:
        """Load metadata from disk."""
        if not self.metadata_file.exists():
            self._metadata = self._create_default_metadata()
            return
        
        try:
            with open(self.metadata_file, 'r') as f:
                self._metadata = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load metadata: {e}")
            self._metadata = self._create_default_metadata()
    
    def _create_default_metadata(self) -> Dict[str, Any]:
        """Create default metadata structure."""
        return {
            "version": "1.0",
            "created": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "last_verification": None,
            "last_enrichment": None,
            "maintenance_tasks": {}
        }
    
    def query_files_by_extension(self, extension: str) -> List[str]:
        """
        Get all files with given extension (cached).
        
        Example: query_files_by_extension(".py")
        """
        cache_key = f"ext_{extension}"
        cached = self.cache.get(cache_key)
        
        if cached is not None:
            self.performance_monitor.log_query(
                query_type="query_files_by_extension",
                latency_ms=0.1,
                cache_hit=True,
                result_count=len(cached)
            )
            return cached
        
        start = datetime.now()
        
        # Query index
        result = self._index.get("file_lookup", {}).get("by_extension", {}).get(
            extension, []
        )
        
        # Cache result
        self.cache.set(cache_key, result)
        
        latency_ms = (datetime.now() - start).total_seconds() * 1000
        self.performance_monitor.log_query(
            query_type="query_files_by_extension",
            latency_ms=latency_ms,
            cache_hit=False,
            result_count=len(result)
        )
        
        return result
    
    def query_files_by_category(self, category: str) -> List[str]:
        """
        Get files in given category (cached).
        
        Example categories: "diagnostics", "policy", "development"
        """
        cache_key = f"cat_{category}"
        cached = self.cache.get(cache_key)
        
        if cached is not None:
            self.performance_monitor.log_query(
                query_type="query_files_by_category",
                latency_ms=0.1,
                cache_hit=True,
                result_count=len(cached)
            )
            return cached
        
        start = datetime.now()
        
        result = self._index.get("file_lookup", {}).get("by_category", {}).get(
            category, []
        )
        
        self.cache.set(cache_key, result)
        
        latency_ms = (datetime.now() - start).total_seconds() * 1000
        self.performance_monitor.log_query(
            query_type="query_files_by_category",
            latency_ms=latency_ms,
            cache_hit=False,
            result_count=len(result)
        )
        
        return result
    
    def query_decision_context(
        self,
        context_type: str,
        severity: Optional[str] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Get decision context for agent reasoning.
        
        Args:
            context_type: "violations", "patterns", "recommendations"
            severity: Optional filter by severity level
            limit: Max results to return
        
        Returns:
            Decision context dict suitable for agent reasoning
        """
        cache_key = f"ctx_{context_type}_{severity}_{limit}"
        cached = self.cache.get(cache_key, ttl_override_seconds=1800)  # 30min TTL
        
        if cached is not None:
            self.performance_monitor.log_query(
                query_type="query_decision_context",
                latency_ms=0.1,
                cache_hit=True,
                result_count=len(cached.get("results", []))
            )
            return cached
        
        start = datetime.now()
        
        decision_context = self._index.get("decision_context", {})
        
        result = {
            "context_type": context_type,
            "timestamp": datetime.now().isoformat(),
            "results": []
        }
        
        if context_type == "violations":
            violations = decision_context.get("prior_violations", {}).get(
                severity or "all", []
            )
            result["results"] = violations[:limit]
        
        elif context_type == "patterns":
            patterns = decision_context.get("remediation_patterns", {})
            result["results"] = [
                (pattern, stats)
                for pattern, stats in patterns.items()
            ][:limit]
        
        elif context_type == "recommendations":
            recommendations = decision_context.get("agent_decisions", {})
            result["results"] = list(recommendations.items())[:limit]
        
        self.cache.set(cache_key, result)
        
        latency_ms = (datetime.now() - start).total_seconds() * 1000
        self.performance_monitor.log_query(
            query_type="query_decision_context",
            latency_ms=latency_ms,
            cache_hit=False,
            result_count=len(result["results"])
        )
        
        return result
    
    def add_strategic_insight(self, pattern: 'Pattern') -> None:
        """
        Adds a new strategic insight (a discovered pattern) to the Tier 3 archive.

        This method is called by the enrichment pipeline when a high-confidence
        pattern is discovered and needs to be promoted.

        Args:
            pattern: The Pattern object to add.
        """
        with self._lock:
            # Ensure the decision_context structure exists
            if "decision_context" not in self._index:
                self._index["decision_context"] = {}
            
            # We'll store promoted patterns in a new 'strategic_insights' section
            if "strategic_insights" not in self._index["decision_context"]:
                self._index["decision_context"]["strategic_insights"] = []

            # Avoid duplicates - check if a similar pattern already exists
            # This is a simple check; a more robust version might use a hash of the pattern name and type
            existing_pattern_names = {p.get('name') for p in self._index["decision_context"]["strategic_insights"]}
            if pattern.name in existing_pattern_names:
                logger.debug(f"Pattern '{pattern.name}' already exists in Tier 3. Skipping.")
                return

            # Convert dataclass to dict for JSON serialization
            pattern_dict = asdict(pattern)
            
            # Convert enums to strings
            pattern_dict['pattern_type'] = pattern.pattern_type.value
            
            self._index["decision_context"]["strategic_insights"].append(pattern_dict)
            
            # Invalidate related caches
            self.cache.clear() # Simple invalidation for now
            
            logger.info(f"Added new strategic insight to Tier 3: '{pattern.name}'")

    def get_performance_analysis(self) -> Dict[str, Any]:
        """Get performance metrics for monitoring."""
        return {
            "timestamp": datetime.now().isoformat(),
            "query_analysis": self.performance_monitor.analyze(),
            "cache_stats": self.cache.stats(),
            "slow_queries": [
                asdict(m) for m in self.performance_monitor.get_slow_queries()
            ][:10]
        }
    
    def maintenance_prune_cache(self) -> Dict[str, Any]:
        """Prune expired cache entries (background task)."""
        count = self.cache.prune_expired()
        
        result = {
            "task": "cache_prune",
            "timestamp": datetime.now().isoformat(),
            "entries_pruned": count
        }
        
        logger.info(f"Cache maintenance: pruned {count} expired entries")
        
        return result
    
    def maintenance_verify_index(self) -> Dict[str, Any]:
        """Verify index integrity (background task)."""
        result = {
            "task": "verify_index",
            "timestamp": datetime.now().isoformat(),
            "status": "unknown",
            "issues": []
        }
        
        try:
            # Verify index file exists and is readable
            if not self.index_file.exists():
                result["issues"].append("Index file not found")
                result["status"] = "failed"
                return result
            
            # Verify index is valid JSON
            with open(self.index_file, 'r') as f:
                json.load(f)
            
            # Verify metadata consistency
            file_count = 0
            for ext_files in self._index.get("file_lookup", {}).get(
                "by_extension", {}
            ).values():
                file_count += len(ext_files)
            
            result["verified_file_count"] = file_count
            result["status"] = "verified"
            result["last_verification"] = datetime.now().isoformat()
            
            logger.info(f"Index verification: {file_count} files verified")
            
        except Exception as e:
            result["issues"].append(str(e))
            result["status"] = "failed"
            logger.error(f"Index verification failed: {e}")
        
        return result
    
    def get_archive_stats(self) -> ArchiveStats:
        """Get archive statistics."""
        stats = self._index.get("archive_metadata", {})
        
        return ArchiveStats(
            created_timestamp=stats.get("created", "unknown"),
            last_updated=stats.get("last_updated", "unknown"),
            total_files=stats.get("total_files", 0),
            total_directories=stats.get("total_dirs", 0),
            total_size_bytes=stats.get("total_size_bytes", 0),
            file_types=stats.get("by_extension", {})
        )


# Singleton instance
_manager_instance: Optional[ArchiveIndexManager] = None


def get_archive_manager(archive_root: Optional[Path] = None) -> ArchiveIndexManager:
    """Get or create singleton archive manager."""
    global _manager_instance
    
    if _manager_instance is None:
        if archive_root is None:
            archive_root = Path(__file__).parent.parent.parent / "quarantine_legacy_archive"
        _manager_instance = ArchiveIndexManager(archive_root)
    
    return _manager_instance
