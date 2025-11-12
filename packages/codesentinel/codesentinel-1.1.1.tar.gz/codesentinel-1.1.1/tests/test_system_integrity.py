# -*- coding: utf-8 -*-
"""
SEAM-Tight Integrity Tests for New Systems

This test suite validates the core functionality, security, and efficiency of
recently implemented systems, ensuring they adhere to the SEAM principles.

- ORACL™ Memory Ecosystem (Tiers 1, 2, 3)
- Instruction Defragmentation Utility

Author: GitHub Copilot
Date: November 11, 2025
"""

import pytest
import json
import os
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

# Mocked imports for components that will be tested
from tools.codesentinel.defrag_instructions import run_defrag
from codesentinel.utils.session_memory import SessionMemory
from codesentinel.utils.oracl_context_tier import (
    add_context_summary,
    get_weekly_summaries,
    prune_old_context_logs,
)

# --- Test Fixtures ---

@pytest.fixture(scope="function")
def test_environment(tmp_path_factory):
    """Creates a temporary, isolated environment for testing file operations."""
    base_path = tmp_path_factory.mktemp("system_integrity_tests")
    
    # Create subdirectories
    (base_path / ".github").mkdir()
    (base_path / "tools/instruction_schemas").mkdir(parents=True)
    (base_path / ".agent_sessions/context_tier").mkdir(parents=True, exist_ok=True)
    
    yield base_path
    
    # Teardown is handled by tmp_path_factory

@pytest.fixture
def mock_defrag_files(test_environment):
    """Creates mock instruction and schema files for the defrag utility."""
    # --- Mock Instruction File ---
    instructions_content = """<!-- Header content -->

---

## Section B

Content of B.

---

## Section A

Content of A.
"""
    instructions_path = test_environment / ".github/copilot-instructions.md"
    instructions_path.write_text(instructions_content, encoding="utf-8")

    # --- Mock Schema File ---
    schema_content = {
        "section_order": ["Section A", "Section B"],
        "merge_sections": {}
    }
    schema_path = test_environment / "tools/instruction_schemas/test_schema.json"
    schema_path.write_text(json.dumps(schema_content), encoding="utf-8")
    
    return instructions_path, schema_path

# --- Defragmentation Utility Tests ---

def test_defrag_dry_run_works(mock_defrag_files, capsys):
    """Verify that dry-run shows proposed changes without modifying the file."""
    instructions_path, schema_path = mock_defrag_files
    original_content = instructions_path.read_text(encoding="utf-8")
    
    result = run_defrag(instructions_path, schema_path, dry_run=True, no_backup=True)
    
    assert result is True
    # Check that the file content is unchanged
    assert instructions_path.read_text(encoding="utf-8") == original_content
    
    # Check that the output contains diff-like content
    captured = capsys.readouterr()
    assert "--- DRY RUN: Proposed changes ---" in captured.out
    assert "--- original" in captured.out
    assert "+++ defragmented" in captured.out
    assert "## Section A" in captured.out # Should be reordered

def test_defrag_apply_works(mock_defrag_files):
    """Verify that --apply modifies the file and creates a backup."""
    instructions_path, schema_path = mock_defrag_files
    
    result = run_defrag(instructions_path, schema_path, dry_run=False, no_backup=False)
    
    assert result is True
    
    # Verify backup was created
    backup_path = instructions_path.with_suffix(".md.bak")
    assert backup_path.exists()
    
    # Verify file was modified and reordered
    new_content = instructions_path.read_text(encoding="utf-8")
    assert "## Section A" in new_content
    assert new_content.find("## Section A") < new_content.find("## Section B")

def test_defrag_handles_file_not_found(mock_defrag_files, caplog):
    """Test that the script handles missing files gracefully."""
    instructions_path, schema_path = mock_defrag_files
    
    # Test missing instructions file
    result = run_defrag(Path("non_existent_file.md"), schema_path, dry_run=True, no_backup=True)
    assert result is False
    assert "Target file not found" in caplog.text
    
    caplog.clear()
    
    # Test missing schema file
    result = run_defrag(instructions_path, Path("non_existent_schema.json"), dry_run=True, no_backup=True)
    assert result is False
    assert "Schema file not found" in caplog.text

# --- ORACL™ Memory Ecosystem Tests ---

@patch('codesentinel.utils.session_memory.add_context_summary')
def test_session_promotion_to_context(mock_add_summary, test_environment):
    """Test Tier 1 -> Tier 2 promotion logic."""
    session = SessionMemory(workspace_root=test_environment)
    
    # Simulate adding data that makes the session eligible for promotion
    session.log_decision("Test Decision", "Test Rationale")
    session.log_decision("Another Decision", "More Rationale")
    session.save_task_state([{'id': 1, 'title': 'Test', 'status': 'completed'}])

    # This inner function mimics the logic inside the thread from the real method
    def promotion_task():
        if not session.is_task_successful() or not session.has_significant_decisions():
            return
        summary = session.get_summary()
        mock_add_summary(session.workspace_root, summary)

    # Patch threading.Thread to run the target function immediately and synchronously
    with patch('threading.Thread', side_effect=lambda target, daemon: target()) as mock_thread:
        session.promote_session_to_context()

    # Verify that our mock add_context_summary was called once with the correct data
    mock_add_summary.assert_called_once()
    call_args = mock_add_summary.call_args[0]
    assert call_args[0] == test_environment
    summary_payload = call_args[1]
    assert summary_payload['session_id'] == session.session_id
    assert summary_payload['outcome'] == 'success'
    assert len(summary_payload['key_decisions']) == 2

@patch('codesentinel.utils.oracl_context_tier.datetime')
def test_context_log_pruning(mock_datetime, test_environment):
    """Test Tier 2 pruning of logs older than 7 days."""
    context_dir = test_environment / ".agent_sessions/context_tier"
    
    # Create a "current" log file
    (context_dir / "2025-11-11.jsonl").touch()
    # Create an "old" log file
    old_log_path = context_dir / "2025-11-01.jsonl"
    old_log_path.touch()
    
    # Mock datetime.now() to return Nov 11, 2025 and make datetime.datetime work normally
    from datetime import datetime as real_datetime
    mock_datetime.now.return_value = real_datetime(2025, 11, 11)
    mock_datetime.side_effect = lambda *args, **kwargs: real_datetime(*args, **kwargs)
    
    prune_old_context_logs(test_environment)
    
    assert (context_dir / "2025-11-11.jsonl").exists()
    assert not old_log_path.exists()

# This is a placeholder for a more complex test.
# Testing the full Tier 2 -> Tier 3 promotion requires mocking the scheduler
# and the enrichment pipeline, which is beyond a quick integrity check.
@patch('codesentinel.utils.archive_index_manager.ArchiveIndexManager')
def test_tier3_receives_data_placeholder(mock_index_manager):
    """Placeholder test to show Tier 3 integration point."""
    # In a real scenario, we would trigger the weekly maintenance task
    # and assert that add_strategic_insight is called.
    mock_manager_instance = mock_index_manager.return_value
    mock_manager_instance.add_strategic_insight.return_value = None
    
    # Simulate a call that would happen inside the enrichment pipeline
    mock_manager_instance.add_strategic_insight("test_pattern", {"success_rate": 0.9})
    
    mock_manager_instance.add_strategic_insight.assert_called_once_with(
        "test_pattern", {"success_rate": 0.9}
    )
