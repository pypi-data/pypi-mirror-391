"""Helper utilities for CLI commands with agent integration."""

from __future__ import annotations

import sys
from typing import Any, Callable, Dict, Optional

from .agent_utils import AgentContext, display_agent_context, export_agent_context

AnalysisFn = Callable[[], Any]
StandardHandler = Callable[[Any], None]
ContextBuilder = Callable[[Any], AgentContext]
ApplySafeFn = Callable[[AgentContext, Any, Any], Dict[str, Any]]


def run_agent_enabled_command(
    command_name: str,
    args: Any,
    analysis_fn: AnalysisFn,
    standard_handler: StandardHandler,
    context_builder: ContextBuilder,
    apply_safe_fn: Optional[ApplySafeFn] = None,
) -> Dict[str, Any]:
    """Execute a command that optionally supports agent integration.

    The command is executed in two modes:
    - Standard: when ``--agent`` is not supplied, run ``analysis_fn`` and pass
      results to ``standard_handler``.
    - Agent: when ``--agent`` is supplied, build an :class:`AgentContext` using
      ``context_builder`` and either export or display it. Optional safe
      automation logic can be provided via ``apply_safe_fn``.

    Returns a dictionary describing the execution mode and results.
    """
    try:
        results = analysis_fn()
    except Exception as exc:  # pragma: no cover - pass through unexpected errors
        print(f"Error while running {command_name}: {exc}", file=sys.stderr)
        raise

    if not getattr(args, "agent", False):
        standard_handler(results)
        return {"mode": "standard", "results": results}

    context = context_builder(results)

    export_path = getattr(args, "export", None)
    if export_path:
        export_agent_context(context, export_path, verbose=True)
        return {
            "mode": "agent",
            "results": results,
            "context": context,
            "applied_actions": None,
        }
    
    # Display context first
    verbose = getattr(args, "verbose", False)
    display_agent_context(context, verbose=verbose)

    # Apply safe automated fixes when in agent mode (unless export-only)
    applied_actions: Optional[Dict[str, Any]] = None
    if apply_safe_fn is not None:
        print("\n" + "=" * 60)
        print("APPLYING SAFE AUTOMATED FIXES")
        print("=" * 60)
        applied_actions = apply_safe_fn(context, results, args)
    else:
        print("\nNo safe automated actions are available for this command yet.")

    # Check if there are manual review items remaining
    manual_review_count = len([
        opp for opp in context.opportunities
        if opp.agent_decision_required
    ])
    
    if manual_review_count > 0:
        print(f"\n[!] {manual_review_count} issue(s) require manual review")
        response = input("\nLaunch interactive review mode? (y/N): ").strip().lower()
        if response == 'y':
            # Import here to avoid circular dependency
            from codesentinel.cli.dev_audit_review import run_interactive_review
            run_interactive_review(context)

    return {
        "mode": "agent",
        "results": results,
        "context": context,
        "applied_actions": applied_actions,
    }
