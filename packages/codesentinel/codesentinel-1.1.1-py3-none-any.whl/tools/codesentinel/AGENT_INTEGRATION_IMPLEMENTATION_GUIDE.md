# CLI Agent Integration Implementation Guide

**Status:** Implementation Plan  
**Created:** November 11, 2025  
**Target:** Complete integration framework for agent-assisted CLI commands

---

## Overview

This guide provides step-by-step instructions for implementing agent integration across CodeSentinel's CLI commands. It builds on the analysis in `CLI_AGENT_INTEGRATION_ANALYSIS.md` with concrete code templates and implementation patterns.

---

## Part 1: Shared Agent Utilities Module

### File: `codesentinel/cli/agent_utils.py`

**Purpose:** Centralized utilities for agent integration across all commands

```python
"""
Shared utilities for agent-assisted CLI command execution.

This module provides standardized patterns for:
- Generating agent-readable context from command analysis
- Exporting agent context to files
- Applying agent recommendations
- Tracking agent decisions
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime


class AgentContext:
    """Standard format for agent-readable analysis context."""
    
    def __init__(self, command: str, analysis_results: Dict[str, Any]):
        self.command = command
        self.timestamp = datetime.utcnow().isoformat() + 'Z'
        self.analysis_results = analysis_results
        self.remediation_opportunities: List[Dict] = []
        self.statistics = {
            'total_findings': 0,
            'critical_count': 0,
            'high_count': 0,
            'medium_count': 0,
            'low_count': 0,
            'automated_fixes_possible': 0,
            'manual_review_required': 0,
        }
    
    def add_opportunity(
        self,
        id: str,
        type: str,  # vulnerability, optimization, inconsistency, etc.
        priority: str,  # critical, high, medium, low
        title: str,
        description: str,
        current_state: Dict[str, Any],
        proposed_action: str,
        agent_decision_required: bool = True,
        safe_to_automate: bool = False,
        risk_level: str = 'medium',  # none, low, medium, high
        estimated_effort: str = 'medium',  # none, low, medium, high
        suggested_actions: Optional[List[str]] = None,
    ) -> None:
        """Add a remediation opportunity to the context."""
        
        opportunity = {
            'id': id,
            'type': type,
            'priority': priority,
            'title': title,
            'description': description,
            'current_state': current_state,
            'proposed_action': proposed_action,
            'agent_decision_required': agent_decision_required,
            'safe_to_automate': safe_to_automate,
            'risk_level': risk_level,
            'estimated_effort': estimated_effort,
            'suggested_actions': suggested_actions or [],
        }
        
        self.remediation_opportunities.append(opportunity)
        
        # Update statistics
        self.statistics['total_findings'] += 1
        if priority == 'critical':
            self.statistics['critical_count'] += 1
        elif priority == 'high':
            self.statistics['high_count'] += 1
        elif priority == 'medium':
            self.statistics['medium_count'] += 1
        elif priority == 'low':
            self.statistics['low_count'] += 1
        
        if safe_to_automate:
            self.statistics['automated_fixes_possible'] += 1
        if agent_decision_required:
            self.statistics['manual_review_required'] += 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'command': self.command,
            'timestamp': self.timestamp,
            'analysis_results': self.analysis_results,
            'remediation_opportunities': self.remediation_opportunities,
            'statistics': self.statistics,
        }
    
    def to_json(self, indent: Optional[int] = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)


def export_agent_context(
    context: AgentContext,
    export_path: Optional[str] = None,
    verbose: bool = False,
) -> str:
    """
    Export agent context to JSON file.
    
    Args:
        context: AgentContext object to export
        export_path: Optional path to save (default: .agent_context/{command}_{timestamp}.json)
        verbose: If True, print export details
    
    Returns:
        Path to exported file
    """
    if export_path:
        output_file = Path(export_path)
    else:
        context_dir = Path.cwd() / '.agent_context'
        context_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        output_file = context_dir / f"{context.command}_{timestamp}.json"
    
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        f.write(context.to_json(indent=2))
    
    if verbose:
        print(f"\n✓ Agent context exported: {output_file}")
        print(f"  Command: {context.command}")
        print(f"  Findings: {context.statistics['total_findings']}")
        print(f"  Safe to automate: {context.statistics['automated_fixes_possible']}")
        print(f"  Requires review: {context.statistics['manual_review_required']}")
    
    return str(output_file)


def display_agent_context(context: AgentContext, verbose: bool = False) -> None:
    """
    Display agent context in human-readable format.
    
    Args:
        context: AgentContext object to display
        verbose: If True, include detailed information
    """
    print("\n" + "=" * 70)
    print(f"AGENT-ASSISTED ANALYSIS: {context.command.upper()}")
    print("=" * 70)
    
    # Statistics
    stats = context.statistics
    print(f"\nFINDINGS SUMMARY:")
    print(f"  Total: {stats['total_findings']}")
    print(f"  Critical: {stats['critical_count']}")
    print(f"  High: {stats['high_count']}")
    print(f"  Medium: {stats['medium_count']}")
    print(f"  Low: {stats['low_count']}")
    print(f"\nREMEDIATION STATUS:")
    print(f"  Safe to automate: {stats['automated_fixes_possible']}")
    print(f"  Require review: {stats['manual_review_required']}")
    
    # Opportunities grouped by priority
    if context.remediation_opportunities:
        print(f"\nREMEDIATION OPPORTUNITIES:")
        for priority in ['critical', 'high', 'medium', 'low']:
            matches = [
                opp for opp in context.remediation_opportunities
                if opp['priority'] == priority
            ]
            if matches:
                print(f"\n  {priority.upper()}:")
                for opp in matches:
                    symbol = "🔴" if priority == "critical" else "🟠" if priority == "high" else "🟡" if priority == "medium" else "🔵"
                    auto = " [AUTO]" if opp['safe_to_automate'] else ""
                    print(f"    {symbol} {opp['title']}{auto}")
                    if verbose:
                        print(f"       {opp['description']}")
                        if opp['suggested_actions']:
                            for action in opp['suggested_actions']:
                                print(f"       → {action}")
    
    print("\n" + "=" * 70 + "\n")


def generate_scan_agent_context(results: Dict[str, Any]) -> AgentContext:
    """
    Generate agent context from security scan results.
    
    Args:
        results: Dictionary with scan findings
    
    Returns:
        AgentContext with vulnerability analysis
    """
    context = AgentContext('scan', results)
    
    # Parse vulnerabilities and create opportunities
    vulnerabilities = results.get('vulnerabilities', [])
    for vuln in vulnerabilities:
        severity = vuln.get('severity', 'medium').lower()
        priority_map = {
            'critical': 'critical',
            'high': 'high',
            'medium': 'medium',
            'low': 'low',
        }
        priority = priority_map.get(severity, 'medium')
        
        context.add_opportunity(
            id=vuln.get('id', 'unknown'),
            type='vulnerability',
            priority=priority,
            title=vuln.get('title', 'Unknown vulnerability'),
            description=vuln.get('description', ''),
            current_state={'file': vuln.get('file'), 'line': vuln.get('line')},
            proposed_action=vuln.get('suggested_fix', 'Review and fix'),
            agent_decision_required=priority in ['critical', 'high'],
            safe_to_automate=vuln.get('auto_fixable', False),
            risk_level='high' if priority == 'critical' else 'medium',
            suggested_actions=vuln.get('suggested_actions', []),
        )
    
    return context


def generate_integrate_agent_context(
    opportunities: List[Dict[str, Any]]
) -> AgentContext:
    """
    Generate agent context from integration analysis.
    
    Args:
        opportunities: List of integration opportunities
    
    Returns:
        AgentContext with workflow optimization suggestions
    """
    context = AgentContext('integrate', {'opportunities': opportunities})
    
    for opp in opportunities:
        context.add_opportunity(
            id=opp.get('id', 'unknown'),
            type='optimization',
            priority=opp.get('priority', 'medium'),
            title=opp.get('title', 'Integration opportunity'),
            description=opp.get('description', ''),
            current_state=opp.get('current_state', {}),
            proposed_action=opp.get('proposed_action', ''),
            agent_decision_required=opp.get('agent_decision_required', True),
            safe_to_automate=opp.get('safe_to_automate', False),
            risk_level=opp.get('risk_level', 'low'),
            estimated_effort=opp.get('effort', 'medium'),
            suggested_actions=opp.get('suggested_actions', []),
        )
    
    return context


class AgentDecisionTracker:
    """Track agent decisions for audit trail."""
    
    def __init__(self, command: str):
        self.command = command
        self.decisions: List[Dict[str, Any]] = []
        self.applied_count = 0
        self.rejected_count = 0
    
    def record_decision(
        self,
        opportunity_id: str,
        agent_recommendation: str,
        user_action: str,  # applied, rejected, deferred
        notes: Optional[str] = None,
    ) -> None:
        """Record an agent decision."""
        self.decisions.append({
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'opportunity_id': opportunity_id,
            'recommendation': agent_recommendation,
            'action': user_action,
            'notes': notes,
        })
        
        if user_action == 'applied':
            self.applied_count += 1
        elif user_action == 'rejected':
            self.rejected_count += 1
    
    def save_log(self, log_path: Optional[str] = None) -> str:
        """Save decision log to file."""
        if log_path:
            output_file = Path(log_path)
        else:
            log_dir = Path.cwd() / '.agent_decisions'
            log_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            output_file = log_dir / f"{self.command}_{timestamp}.json"
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        log_data = {
            'command': self.command,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'summary': {
                'applied': self.applied_count,
                'rejected': self.rejected_count,
                'total': len(self.decisions),
            },
            'decisions': self.decisions,
        }
        
        with open(output_file, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        return str(output_file)
```

---

## Part 2: Integration Pattern Template

### For Commands: `scan`, `integrate`, `dependencies`, etc

```python
# In codesentinel/cli/command_utils.py (or similar)

def perform_command_with_agent(
    args,
    codesentinel,
    command_name: str,
    analysis_func,
    apply_func,
) -> int:
    """
    Standard pattern for agent-integrated commands.
    
    Args:
        args: Parsed arguments
        codesentinel: CodeSentinel instance
        command_name: Name of command (e.g., 'scan', 'integrate')
        analysis_func: Function that performs analysis, returns results
        apply_func: Function that applies recommendations
    
    Returns:
        Exit code (0 = success, 1 = error)
    """
    from .agent_utils import (
        AgentContext, export_agent_context, display_agent_context,
        AgentDecisionTracker
    )
    
    try:
        # Step 1: Perform analysis
        print(f"Analyzing {command_name}...")
        results = analysis_func(codesentinel, args)
        
        # Step 2: Check if agent mode requested
        if not hasattr(args, 'agent') or not args.agent:
            # Standard mode - just return results
            return apply_func(codesentinel, results, args, dry_run=args.dry_run if hasattr(args, 'dry_run') else False)
        
        # Step 3: Generate agent context
        context = AgentContext(command_name, results)
        # (Populate context with opportunities - specific to each command)
        
        # Step 4: Export or display
        if hasattr(args, 'export') and args.export:
            export_agent_context(context, args.export, verbose=True)
            return 0
        
        # Step 5: Display agent analysis
        display_agent_context(context, verbose=args.verbose if hasattr(args, 'verbose') else False)
        
        # Step 6: Apply safe fixes if appropriate
        if hasattr(args, 'force') and args.force:
            print(f"Applying safe automated recommendations...")
            tracker = AgentDecisionTracker(command_name)
            
            # Apply only safe-to-automate opportunities
            for opp in context.remediation_opportunities:
                if opp['safe_to_automate']:
                    print(f"  ✓ {opp['title']}")
                    tracker.record_decision(opp['id'], opp['proposed_action'], 'applied')
                else:
                    print(f"  → {opp['title']} (requires review)")
                    tracker.record_decision(opp['id'], opp['proposed_action'], 'deferred')
            
            # Save decision log
            tracker.save_log()
            
            print(f"\nApplied: {tracker.applied_count} | Deferred: {tracker.rejected_count}")
        
        return 0
        
    except Exception as e:
        print(f"Error in {command_name}: {e}", file=sys.stderr)
        return 1
```

---

## Part 3: Command-Specific Implementation Examples

### Example 1: SCAN Command with Agent Integration

```python
# In codesentinel/cli/__init__.py, scan handler section

def generate_scan_analysis(codesentinel, args):
    """Perform security scan analysis."""
    print("Running security scan...")
    return codesentinel.run_security_scan()

def apply_scan_results(codesentinel, results, args, dry_run=False):
    """Apply scan results (standard mode)."""
    if args.output:
        import json
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Scan results saved to {args.output}")
    else:
        print(f"Scan completed. Found {results['summary']['total_vulnerabilities']} vulnerabilities.")
    return 0

# In handler:
elif args.command == 'scan':
    from .command_utils import perform_command_with_agent
    sys.exit(perform_command_with_agent(
        args,
        codesentinel,
        'scan',
        generate_scan_analysis,
        apply_scan_results,
    ))
```

### Example 2: INTEGRATE Command with Agent Integration

```python
# Similar pattern for integrate command

def generate_integration_analysis(codesentinel, args):
    """Analyze integration opportunities."""
    print("Analyzing integration opportunities...")
    # Return list of integration opportunities
    return []

def apply_integration_results(codesentinel, results, args, dry_run=False):
    """Apply integration results."""
    # Process integration opportunities
    return 0

# In handler:
elif args.command == 'integrate':
    from .command_utils import perform_command_with_agent
    sys.exit(perform_command_with_agent(
        args,
        codesentinel,
        'integrate',
        generate_integration_analysis,
        apply_integration_results,
    ))
```

---

## Part 4: Agent Integration Status Marking System

### Metadata Format for Help Files

Each help file should include an agent integration marker at the top:

```markdown
# [Command Name] - [Agent Status Badge]

**Agent Integration Status:** `ready` | `planned` | `not-applicable`

**Last Updated:** YYYY-MM-DD

## Description
...
```

### Status Values

| Status | Meaning | Icon |
|--------|---------|------|
| `ready` | Fully implemented agent integration with `--agent` flag | 🤖 |
| `planned` | Scheduled for agent integration | 📋 |
| `experimental` | Agent integration in testing/beta | 🧪 |
| `not-applicable` | Command doesn't need agent integration | ✅ |

### Implementation in help-files command

```python
# In codesentinel/cli/update_utils.py

AGENT_STATUS_MAP = {
    'scan': 'ready',
    'integrate': 'ready',
    'dev-audit': 'ready',
    'update-changelog': 'planned',
    'update-dependencies': 'planned',
    'schedule': 'planned',
    'clean': 'experimental',
    'integrity-verify': 'planned',
    'maintenance': 'not-applicable',
    'alert': 'not-applicable',
    'status': 'not-applicable',
    'setup': 'not-applicable',
}

STATUS_ICONS = {
    'ready': '🤖',
    'planned': '📋',
    'experimental': '🧪',
    'not-applicable': '✅',
}

def generate_help_file_with_agent_status(command_name: str, help_text: str) -> str:
    """Add agent integration status to help file header."""
    status = AGENT_STATUS_MAP.get(command_name, 'not-applicable')
    icon = STATUS_ICONS[status]
    
    header = f"""# {command_name.title().replace('-', ' ')} - {icon} {status.upper()}

**Agent Integration Status:** `{status}`

---

"""
    return header + help_text
```

---

## Part 5: Implementation Checklist

### Phase 1: Foundation (Week 1)

- [ ] Create `codesentinel/cli/agent_utils.py` with AgentContext, export/display functions
- [ ] Create `codesentinel/cli/command_utils.py` with `perform_command_with_agent` pattern
- [ ] Update help files to include agent status markers
- [ ] Document agent context schema in README

### Phase 2: TIER 1 Commands (Week 2-3)

- [ ] Implement `scan --agent` with vulnerability analysis
- [ ] Implement `integrate --agent` with workflow optimization
- [ ] Add tests for agent context generation
- [ ] Test --export and --force flags

### Phase 3: TIER 2 Commands (Week 4-5)

- [ ] Implement `update changelog --agent`
- [ ] Implement `update dependencies --agent`
- [ ] Implement `schedule --agent`
- [ ] Implement `integrity verify --agent`

### Phase 4: Polish & Documentation (Week 6)

- [ ] Comprehensive testing across all commands
- [ ] Update CLI help documentation
- [ ] Create agent integration guide for users
- [ ] Release phase-4 update with agent framework

---

## References

- CLI Agent Integration Analysis: `docs/CLI_AGENT_INTEGRATION_ANALYSIS.md`
- Command Handlers: `codesentinel/cli/__init__.py` (lines 1195-3101)
- Existing Agent Implementation: `codesentinel/cli/dev_audit_utils.py`
