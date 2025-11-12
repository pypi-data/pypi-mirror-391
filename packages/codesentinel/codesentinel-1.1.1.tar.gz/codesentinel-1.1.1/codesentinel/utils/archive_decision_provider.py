"""
Archive Decision Context Provider

Provides historical context to agents for intelligent, historically-aware decision-making.
Enables agents to access patterns, success rates, and recommendations from archived records.

Author: CodeSentinel
Date: 2025-11-11
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging

from .archive_index_manager import get_archive_manager

logger = logging.getLogger(__name__)


@dataclass
class DecisionContext:
    """Context for an agent decision."""
    decision_type: str
    context_timestamp: str
    similar_past_cases: List[Dict[str, Any]]
    pattern_analysis: Dict[str, Any]
    success_rate: float
    confidence_score: float
    recommended_actions: List[str]
    metadata: Dict[str, Any]


class ArchiveDecisionContextProvider:
    """
    Provides decision context from historical archival records.
    
    Enables agents to make intelligent decisions by understanding:
    - Similar situations in the past
    - Success/failure patterns
    - Recommended actions based on history
    - Confidence scores for recommendations
    """
    
    # Decision type definitions and their attributes
    DECISION_TYPES = {
        "policy_violation_handling": {
            "search_fields": ["violation_type", "severity"],
            "pattern_key": "remediation_patterns",
            "context_key": "violation_contexts"
        },
        "cleanup_strategy": {
            "search_fields": ["item_type", "size_range"],
            "pattern_key": "cleanup_patterns",
            "context_key": "cleanup_contexts"
        },
        "dependency_update": {
            "search_fields": ["package_name", "severity"],
            "pattern_key": "update_patterns",
            "context_key": "update_contexts"
        },
        "archive_operation": {
            "search_fields": ["item_count", "item_type"],
            "pattern_key": "archive_patterns",
            "context_key": "archive_contexts"
        }
    }
    
    def __init__(self, archive_manager=None):
        """
        Initialize provider.
        
        Args:
            archive_manager: Optional ArchiveIndexManager instance
        """
        self.archive_manager = archive_manager or get_archive_manager()
    
    def get_decision_context(
        self,
        decision_type: str,
        current_state: Dict[str, Any],
        search_radius_days: int = 30
    ) -> DecisionContext:
        """
        Get historical context for a decision.
        
        Args:
            decision_type: Type of decision ("policy_violation_handling", etc.)
            current_state: Current situation parameters
            search_radius_days: Look back N days for similar decisions
        
        Returns:
            DecisionContext with historical patterns and recommendations
        
        Example:
            context = provider.get_decision_context(
                decision_type="policy_violation_handling",
                current_state={
                    "violation_type": "unauthorized_file_in_root",
                    "severity": "medium",
                    "file": ".agent_session"
                },
                search_radius_days=30
            )
            
            if context.success_rate > 0.8:
                agent.apply(context.recommended_actions[0])
        """
        
        # Validate decision type
        if decision_type not in self.DECISION_TYPES:
            logger.warning(f"Unknown decision type: {decision_type}")
            return self._create_empty_context(decision_type)
        
        # Find similar past cases
        similar_cases = self._find_similar_past_cases(
            decision_type=decision_type,
            current_state=current_state,
            search_radius_days=search_radius_days
        )
        
        if not similar_cases:
            logger.info(f"No similar past cases found for {decision_type}")
            return self._create_empty_context(decision_type)
        
        # Analyze patterns
        pattern_analysis = self._analyze_patterns(similar_cases)
        
        # Calculate success rate
        success_rate = self._calculate_success_rate(similar_cases)
        
        # Generate recommendations
        recommended_actions = self._generate_recommendations(
            decision_type=decision_type,
            pattern_analysis=pattern_analysis,
            success_rate=success_rate
        )
        
        # Calculate confidence
        confidence_score = self._calculate_confidence(
            similar_cases=similar_cases,
            success_rate=success_rate
        )
        
        return DecisionContext(
            decision_type=decision_type,
            context_timestamp=datetime.now().isoformat(),
            similar_past_cases=similar_cases[:5],  # Top 5 similar cases
            pattern_analysis=pattern_analysis,
            success_rate=success_rate,
            confidence_score=confidence_score,
            recommended_actions=recommended_actions,
            metadata={
                "search_radius_days": search_radius_days,
                "total_similar_cases": len(similar_cases),
                "query_timestamp": datetime.now().isoformat()
            }
        )
    
    def _find_similar_past_cases(
        self,
        decision_type: str,
        current_state: Dict[str, Any],
        search_radius_days: int
    ) -> List[Dict[str, Any]]:
        """
        Find past cases similar to current situation.
        
        Future enhancement: Use semantic similarity/embeddings for better matching.
        """
        
        # Get decision context from archive
        context_data = self.archive_manager.query_decision_context(
            context_type="violations" if "violation" in decision_type else "recommendations",
            limit=100  # Get many candidates, we'll filter
        )
        
        similar_cases = []
        
        for case in context_data.get("results", []):
            # Skip if case is too old
            if "timestamp" in case:
                case_age_days = (
                    datetime.now() - datetime.fromisoformat(case["timestamp"])
                ).days
                if case_age_days > search_radius_days:
                    continue
            
            # Check if case matches on key fields
            match_score = self._calculate_case_match_score(
                decision_type=decision_type,
                current_state=current_state,
                case=case
            )
            
            if match_score > 0.5:  # Must have > 50% match
                similar_cases.append({
                    **case,
                    "match_score": match_score
                })
        
        # Sort by match score
        similar_cases.sort(key=lambda x: x.get("match_score", 0), reverse=True)
        
        return similar_cases
    
    def _calculate_case_match_score(
        self,
        decision_type: str,
        current_state: Dict[str, Any],
        case: Dict[str, Any]
    ) -> float:
        """
        Calculate how similar a past case is to current situation.
        
        Returns: Score from 0.0 to 1.0
        """
        
        score = 0.0
        match_count = 0
        total_fields = 0
        
        # Get search fields for this decision type
        search_fields = self.DECISION_TYPES[decision_type]["search_fields"]
        
        for field in search_fields:
            total_fields += 1
            current_value = current_state.get(field)
            case_value = case.get(field)
            
            if current_value is None or case_value is None:
                continue
            
            # Exact match
            if current_value == case_value:
                match_count += 1
            
            # Partial match (for string fields with common prefix)
            elif isinstance(current_value, str) and isinstance(case_value, str):
                if current_value.lower() in case_value.lower() or \
                   case_value.lower() in current_value.lower():
                    match_count += 0.5
        
        if total_fields > 0:
            score = match_count / total_fields
        
        return score
    
    def _analyze_patterns(self, cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract patterns from similar past cases."""
        
        if not cases:
            return {"pattern_count": 0, "status": "no_cases"}
        
        outcomes = {"success": [], "failure": [], "neutral": []}
        
        for case in cases:
            outcome = case.get("outcome", "neutral")
            if outcome in outcomes:
                outcomes[outcome].append(case)
        
        return {
            "pattern_count": len(cases),
            "success_count": len(outcomes["success"]),
            "failure_count": len(outcomes["failure"]),
            "neutral_count": len(outcomes["neutral"]),
            "success_patterns": [
                {
                    "action": c.get("action"),
                    "outcome": c.get("outcome"),
                    "timestamp": c.get("timestamp")
                }
                for c in outcomes["success"]
            ][:3],  # Top 3 success patterns
            "failure_patterns": [
                {
                    "action": c.get("action"),
                    "reason": c.get("failure_reason"),
                    "timestamp": c.get("timestamp")
                }
                for c in outcomes["failure"]
            ][:3]  # Top 3 failure patterns
        }
    
    def _calculate_success_rate(self, cases: List[Dict[str, Any]]) -> float:
        """Calculate success rate from past cases."""
        
        if not cases:
            return 0.0
        
        success_count = sum(
            1 for case in cases
            if case.get("outcome") == "success"
        )
        
        return success_count / len(cases)
    
    def _generate_recommendations(
        self,
        decision_type: str,
        pattern_analysis: Dict[str, Any],
        success_rate: float
    ) -> List[str]:
        """Generate recommendations based on historical patterns."""
        
        recommendations = []
        
        # Success rate-based recommendations
        if success_rate >= 0.9:
            recommendations.append(
                "Very high success rate with similar approach (90%+); apply proven action"
            )
        elif success_rate >= 0.7:
            recommendations.append(
                "Good success rate with similar approach (70%+); apply with moderate confidence"
            )
        elif success_rate >= 0.5:
            recommendations.append(
                "Moderate success rate (50-70%); consider alternatives if available"
            )
        else:
            recommendations.append(
                "Low success rate with similar approach (< 50%); recommend different strategy"
            )
        
        # Pattern-based recommendations
        success_patterns = pattern_analysis.get("success_patterns", [])
        if success_patterns:
            most_common_action = success_patterns[0].get("action")
            if most_common_action:
                recommendations.append(
                    f"Most successful past action: {most_common_action}"
                )
        
        failure_patterns = pattern_analysis.get("failure_patterns", [])
        if failure_patterns:
            recommendations.append(
                f"Avoid: {failure_patterns[0].get('reason', 'previous failure pattern')}"
            )
        
        return recommendations
    
    def _calculate_confidence(
        self,
        similar_cases: List[Dict[str, Any]],
        success_rate: float
    ) -> float:
        """
        Calculate confidence score for recommendations.
        
        Returns: Score from 0.0 to 1.0
        
        Factors:
        - Number of similar cases (more = higher confidence)
        - Success rate (higher = higher confidence)
        - Case recency (recent = higher confidence)
        """
        
        # Factor 1: Sample size (cap at 20)
        sample_size_factor = min(len(similar_cases) / 20, 1.0)
        
        # Factor 2: Success rate consistency
        success_consistency_factor = abs(success_rate - 0.5) * 2  # Range: 0-1
        
        # Factor 3: Case recency
        if similar_cases:
            most_recent = similar_cases[0]
            if "timestamp" in most_recent:
                age_days = (
                    datetime.now() - datetime.fromisoformat(most_recent["timestamp"])
                ).days
                # Full confidence if < 7 days old, decays to 0 at 90 days
                recency_factor = max(1.0 - (age_days / 90), 0.0)
            else:
                recency_factor = 0.5
        else:
            recency_factor = 0.0
        
        # Weighted average
        confidence = (
            (sample_size_factor * 0.3) +
            (success_consistency_factor * 0.4) +
            (recency_factor * 0.3)
        )
        
        return min(confidence, 1.0)
    
    def _create_empty_context(self, decision_type: str) -> DecisionContext:
        """Create context when no historical data available."""
        return DecisionContext(
            decision_type=decision_type,
            context_timestamp=datetime.now().isoformat(),
            similar_past_cases=[],
            pattern_analysis={"status": "no_data"},
            success_rate=0.0,
            confidence_score=0.0,
            recommended_actions=[
                "No historical context available; use default decision criteria"
            ],
            metadata={
                "no_historical_data": True,
                "query_timestamp": datetime.now().isoformat()
            }
        )
    
    def report_decision_outcome(
        self,
        decision_type: str,
        state: Dict[str, Any],
        action: str,
        outcome: str,
        reason: Optional[str] = None
    ) -> None:
        """
        Report the outcome of an agent decision (for feedback loop).
        
        This is called AFTER the agent executes an action to record:
        - What decision was made
        - What action was taken
        - What the outcome was (success/failure/neutral)
        - Why the outcome occurred
        
        This data feeds back into the archive for future decisions.
        
        Args:
            decision_type: Type of decision
            state: State when decision was made
            action: Action that was taken
            outcome: Result ("success", "failure", "neutral")
            reason: Optional explanation
        """
        
        record = {
            "timestamp": datetime.now().isoformat(),
            "decision_type": decision_type,
            "state": state,
            "action": action,
            "outcome": outcome,
            "reason": reason
        }
        
        logger.info(
            f"Decision outcome recorded: {decision_type} -> {action} = {outcome}"
        )
        
        # TODO: Write to decision log for batch import into archive
        # This implements the feedback loop for agent learning


# Singleton instance
_provider_instance = None


def get_decision_context_provider(
    archive_manager=None
) -> ArchiveDecisionContextProvider:
    """Get or create singleton decision context provider."""
    global _provider_instance
    
    if _provider_instance is None:
        _provider_instance = ArchiveDecisionContextProvider(archive_manager)
    
    return _provider_instance
