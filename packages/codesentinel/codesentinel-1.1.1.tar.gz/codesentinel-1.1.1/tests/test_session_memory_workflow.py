"""Test script to demonstrate session memory workflow."""
from pathlib import Path
from codesentinel.utils.session_memory import SessionMemory

# Initialize fresh session
sm = SessionMemory(Path.cwd())

# Simulate agent task workflow
print("=== SIMULATING AGENT WORKFLOW ===\n")

# Step 1: Cache critical files during analysis
print("Step 1: Caching file contexts during code analysis...")
sm.save_file_context("codesentinel/cli/__init__.py", "Main CLI parser with subcommands for alert, memory, schedule", is_config=False)
sm.save_file_context("codesentinel/utils/config.py", "ConfigManager with dot-notation paths, JSON persistence", is_config=True)
sm.save_file_context("codesentinel/utils/alerts.py", "AlertManager with multi-channel support", is_config=False)
print(f"   ✓ Cached 3 files")

# Step 2: Log important decisions
print("\nStep 2: Logging analysis decisions...")
sm.log_decision("Config structure: alerts.{channel}", "Verified through config.py inspection")
sm.log_decision("Alert send message issue", "Positional 'message' arg parsed as None - subparser routing problem")
sm.log_decision("CLI architecture", "Uses subparsers pattern with alert_action destination")
print(f"   ✓ Logged 3 decisions")

# Step 3: Persist to disk
print("\nStep 3: Persisting session state...")
sm.persist()
print(f"   ✓ State persisted to .agent_session/")

# Step 4: Get statistics
stats = sm.get_cache_stats()
print(f"\nSession Statistics:")
print(f"   Cached files: {stats['cached_files']}")
print(f"   Decisions logged: {stats['logged_decisions']}")
print(f"   Disk usage: {stats['disk_usage_bytes']} bytes")

print("\n=== RESUMING LATER SESSION ===\n")

# Simulate new session - memory is reloaded
sm2 = SessionMemory(Path.cwd())
decisions = sm2.get_recent_decisions()

print("Recent decisions available without re-reading files:")
for i, dec in enumerate(decisions, 1):
    print(f"   {i}. {dec['decision']}")

print("\nAgent can now immediately reference cached context!")
print("✅ Time saved: Eliminated 3 file reads on session resume")
