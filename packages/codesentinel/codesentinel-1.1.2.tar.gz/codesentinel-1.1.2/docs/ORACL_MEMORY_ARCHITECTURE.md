# ORACL™ Memory Architecture: A 3-Tier Ecosystem

**ORACL™** (Omniscient Recommendation Archive & Curation Ledger) — *Intelligent Decision Support*

**Status**: Draft  
**Date**: November 11, 2025  
**Author**: GitHub Copilot

---

## 1. Overview

This document outlines the 3-tier memory architecture for the ORACL™ ecosystem. This architecture unifies the existing short-term session cache with new mid-term and long-term memory tiers, creating a cohesive system for agent intelligence, from immediate task context to deep historical patterns.

The primary goals of this architecture are:

- **Efficiency**: Reduce redundant work by caching data at different temporal granularities.
- **Intelligence**: Enable the agent to learn from past operations, from the last hour to the last year.
- **Scalability**: Ensure the system remains performant as the volume of historical data grows.
- **Simplicity**: Maintain clear boundaries and a simple, one-way data flow between tiers.

---

## 2. The 3-Tier Model

The ORACL™ Memory Ecosystem is composed of three distinct tiers, each serving a specific purpose with a defined data lifetime.

![ORACL™ 3-Tier Memory Architecture](https://i.imgur.com/3-Tier-Diagram.png)

### Tier 1: ORACL™ Session Tier (Short-Term Cache)

- **Component**: The existing `session_memory.py` module.
- **Purpose**: High-speed, ephemeral cache for the agent's **current, active task**. It stores raw operational context to prevent re-reading files and re-analyzing decisions within a single work session.
- **Data Scope**: File summaries, task lists, and analysis decisions relevant to the immediate task.
- **Lifetime**: **0-60 minutes**. Data is considered stale after one hour and is automatically invalidated.
- **Key Attribute**: **Speed**.

### Tier 2: ORACL™ Context Tier (Mid-Term Aggregates)

- **Component**: A new module, `oracl_context_tier.py`.
- **Purpose**: To store curated, high-value summaries from **recently completed sessions**. It provides context on what the agent has successfully accomplished and learned in the recent past.
- **Data Scope**: Aggregated summaries, including the final outcome of a task, the key decisions made, and the core files involved. It does **not** store the raw, noisy data from the session.
- **Lifetime**: **7 days** (rolling window).
- **Key Attribute**: **Relevance**.

### Tier 3: ORACL™ Intelligence Tier (Long-Term Archive)

- **Component**: The existing ORACL™ system (`archive_index_manager.py`, `archive_decision_provider.py`).
- **Purpose**: Permanent, long-term storage for identifying significant, **historical patterns and strategies**. It provides deep wisdom derived from months of operations.
- **Data Scope**: High-level, strategic insights, such as recurring policy violation patterns, successful remediation workflows, and the evolution of the codebase structure.
- **Lifetime**: **Permanent** (with data compression and archival policies).
- **Key Attribute**: **Wisdom**.

---

## 3. Data Flow and Promotion

The data flow is designed to be **one-way and non-blocking**, ensuring that higher-speed tiers remain lean and focused.

`Tier 1 (Session)` → `Tier 2 (Context)` → `Tier 3 (Intelligence)`

### Promotion Mechanism

1. **Session-to-Context Promotion (Tier 1 → Tier 2)**:
    - **Trigger**: Occurs when a Tier 1 session is successfully completed or expires.
    - **Process**: A lightweight function, `promote_session_to_context_tier()`, is invoked.
    - **Logic**: This function extracts a concise summary of the session, including the final task status, key decisions, and a list of critical files. This summary is then appended to the Tier 2 store (e.g., a daily JSON log). This operation is asynchronous and non-blocking.

2. **Context-to-Intelligence Promotion (Tier 2 → Tier 3)**:
    - **Trigger**: A scheduled weekly task.
    - **Process**: The existing `archive_enrichment_pipeline` is used.
    - **Logic**: The pipeline analyzes the past seven days of session summaries from Tier 2 to identify significant, recurring patterns. For example, if a specific type of cleanup action has been successful multiple times, that strategy is promoted as a high-confidence recommendation into the permanent Tier 3 archive.

---

## 4. Querying Strategy

The agent will query the appropriate tier based on the context of its needs, ensuring optimal performance.

- **For immediate task context**:
  > "What was the summary of `config.py` that I just read?"
  - **Action**: Query **Tier 1**. The answer is retrieved instantly from the in-memory cache.

- **For recent project context**:
  > "What were the key files involved in the 'alerting system refactor' I completed yesterday?"
  - **Action**: Query **Tier 2**. The agent retrieves the summary for that completed task.

- **For strategic decisions**:
  > "What is the historically most successful way to resolve an 'unauthorized file in root' violation?"
  - **Action**: Query **Tier 3**. The agent retrieves a high-confidence recommendation from the ORACL™ decision provider, based on months of data.

---

## 5. Implementation Details

- **Tier 1**: Requires minimal changes. The `SessionMemory` class will be conceptually rebranded to `ORACL™ SessionCache` in documentation. A hook will be added to call the promotion function upon session completion.
- **Tier 2**: A new module, `oracl_context_tier.py`, will be created. It will manage a simple, file-based data store (e.g., a directory with daily JSON files) and expose functions for adding new summaries and querying recent entries.
- **Tier 3**: The existing ORACL™ modules will be used as-is. The `archive_enrichment_pipeline`'s configuration will be updated to use Tier 2 as a data source.

This architecture provides a clear and scalable path for evolving the agent's intelligence, building from immediate operational memory to deep, strategic wisdom.

---

## 6. Validation Governance (Beta Directive)

**Directive ID**: ORACL-T1-VALIDATION-20251111-BETA  
**Scope**: Tier 0, Tier 1, Tier 2 artifacts (critical release, governance, and policy documents)  
**Status**: Active beta (monitored for efficacy)

To reduce the risk of silent regressions in foundational artifacts, every edit that touches Tier 0-2 content must execute **redundant validation** immediately after the change. Redundant validation means running at least two complementary verification steps covering formatting, policy compliance, and behavioral integrity. Examples include:

- Running `codesentinel update docs --validate` followed by targeted pytest modules (e.g., `tests/test_docs_formatting.py`).
- Running policy enforcement scripts (root cleanup, governance linters) in tandem with unit or integration tests that cover the modified surface area.
- Executing documentation format checks together with SEAM Protection compliance scans.

Agents must log the validation pair used in the session report so ORACL™ can track adherence and success metrics. During the beta window, deviations require explicit justification and are flagged for review during weekly Tier 2 promotions. Once the directive proves effective, it will be promoted to permanent Tier 0 governance policy.
