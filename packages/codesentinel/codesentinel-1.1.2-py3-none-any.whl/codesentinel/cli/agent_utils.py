"""Utilities for building and presenting agent-integration context."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

PRIORITY_LEVELS = ("critical", "high", "medium", "low")


def _normalise_priority(priority: Optional[str]) -> str:
    """Normalise priority strings to the expected vocabulary."""
    if not priority:
        return "medium"
    lower = str(priority).lower()
    if lower in PRIORITY_LEVELS:
        return lower
    return "medium"


@dataclass
class RemediationOpportunity:
    """Represents a single remediation opportunity detected by an agent analysis."""

    id: str
    type: str
    priority: str
    title: str
    description: str
    current_state: Dict[str, Any] = field(default_factory=dict)
    proposed_action: str = "Review and remediate"
    agent_decision_required: bool = True
    safe_to_automate: bool = False
    risk_level: str = "medium"
    estimated_effort: str = "medium"
    suggested_actions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Return the opportunity as a serialisable dictionary."""
        data = asdict(self)
        data["priority"] = _normalise_priority(self.priority)
        data["risk_level"] = _normalise_priority(self.risk_level)
        data["estimated_effort"] = _normalise_priority(self.estimated_effort)
        return data


class AgentContext:
    """Container describing the outcome of an agent-assisted analysis."""

    def __init__(
        self,
        command: str,
        analysis_results: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.command = command
        self.timestamp = datetime.utcnow()
        self.analysis_results = analysis_results or {}
        self.metadata = metadata or {}
        self._opportunities: List[RemediationOpportunity] = []
        self.statistics: Dict[str, int] = {
            "total_findings": 0,
            "critical_count": 0,
            "high_count": 0,
            "medium_count": 0,
            "low_count": 0,
            "automated_fixes_possible": 0,
            "manual_review_required": 0,
        }

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------
    @property
    def opportunities(self) -> List[RemediationOpportunity]:
        """Return the remediation opportunities."""
        return list(self._opportunities)

    # ------------------------------------------------------------------
    # Mutation helpers
    # ------------------------------------------------------------------
    def add_opportunity(self, opportunity: RemediationOpportunity) -> None:
        """Register a remediation opportunity and update statistics."""
        priority = _normalise_priority(opportunity.priority)
        opportunity.priority = priority

        self._opportunities.append(opportunity)
        self.statistics["total_findings"] += 1
        if priority in self.statistics:
            key = f"{priority}_count"
            self.statistics[key] += 1
        if opportunity.safe_to_automate:
            self.statistics["automated_fixes_possible"] += 1
        if opportunity.agent_decision_required:
            self.statistics["manual_review_required"] += 1

    # ------------------------------------------------------------------
    # Serialisation helpers
    # ------------------------------------------------------------------
    def to_dict(self) -> Dict[str, Any]:
        """Serialise the context to a dictionary."""
        return {
            "command": self.command,
            "timestamp": self.timestamp.isoformat() + "Z",
            "analysis_results": self.analysis_results,
            "metadata": self.metadata,
            "remediation_opportunities": [opp.to_dict() for opp in self._opportunities],
            "statistics": self.statistics,
        }

    def to_json(self, *, indent: int = 2) -> str:
        """Serialise the context to JSON."""
        return json.dumps(self.to_dict(), indent=indent)


def _resolve_export_path(command: str, export_path: Optional[str]) -> Path:
    """Compute the output path for exported agent context."""
    if export_path:
        return Path(export_path).expanduser().resolve()
    context_dir = Path.cwd() / ".agent_context"
    context_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"{command}_{timestamp}.json"
    return (context_dir / filename).resolve()


def export_agent_context(
    context: AgentContext,
    export_path: Optional[str] = None,
    *,
    verbose: bool = False,
) -> Path:
    """Persist an AgentContext to disk."""
    resolved_path = _resolve_export_path(context.command, export_path)
    resolved_path.parent.mkdir(parents=True, exist_ok=True)
    resolved_path.write_text(context.to_json(indent=2), encoding="utf-8")
    if verbose:
        rel = _format_relative(resolved_path)
        print(f"✓ Agent context exported: {rel}")
    return resolved_path


def display_agent_context(context: AgentContext, *, verbose: bool = False) -> None:
    """Pretty-print an AgentContext to stdout."""
    header = f"AGENT-ASSISTED ANALYSIS :: {context.command.upper()}"
    divider = "=" * len(header)
    print(divider)
    print(header)
    print(divider)

    stats = context.statistics
    print("Findings Summary:")
    print(f"  Total findings     : {stats['total_findings']}")
    print(f"  Critical / High    : {stats['critical_count']} / {stats['high_count']}")
    print(f"  Medium / Low       : {stats['medium_count']} / {stats['low_count']}")
    print(f"  Safe automations   : {stats['automated_fixes_possible']}")
    print(f"  Needs review       : {stats['manual_review_required']}")

    if not context.opportunities:
        print("\nNo remediation opportunities detected.")
        print(divider)
        return

    print("\nRemediation Opportunities:")
    for opp in context.opportunities:
        label = _format_priority_label(opp.priority, opp.safe_to_automate)
        print(f"- {label} {opp.title}")
        if verbose:
            print(f"    Description  : {opp.description}")
            if opp.current_state:
                print(f"    Current state: {opp.current_state}")
            print(f"    Proposed     : {opp.proposed_action}")
            if opp.suggested_actions:
                for suggestion in opp.suggested_actions:
                    print(f"      → {suggestion}")
            print(f"    Requires decision: {opp.agent_decision_required}")
            print(f"    Safe to automate : {opp.safe_to_automate}")

    print(divider)


def _format_priority_label(priority: str, safe: bool) -> str:
    """Format a human-friendly label for an opportunity priority."""
    safe_marker = " (auto)" if safe else ""
    if priority == "critical":
        return f"[CRITICAL{safe_marker}]"
    if priority == "high":
        return f"[HIGH{safe_marker}]"
    if priority == "medium":
        return f"[MEDIUM{safe_marker}]"
    return f"[LOW{safe_marker}]"


def _format_relative(path: Path) -> str:
    """Return a repository-relative representation of a path, if possible."""
    try:
        rel = path.relative_to(Path.cwd())
    except ValueError:
        return str(path)
    return str(rel).replace("\\", "/")