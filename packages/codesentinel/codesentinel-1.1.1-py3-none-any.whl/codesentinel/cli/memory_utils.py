"""
CLI utilities for session memory management commands.

Provides handlers for 'codesentinel memory' subcommands:
- memory show: Display current session memory state
- memory clear: Clear session memory cache
- memory stats: Show cache usage statistics
"""

import sys
from typing import Optional


def handle_memory_show(args, session_memory) -> None:
    """
    Display current session memory state.
    
    Shows task summary, recent decisions, and cached files.
    """
    print("\n" + "=" * 70)
    print("SESSION MEMORY STATE")
    print("=" * 70)
    
    # Task summary
    print("\n📋 TASK TRACKING:")
    task_summary = session_memory.get_task_summary()
    if task_summary == "No active tasks":
        print("   No active tasks")
    else:
        for line in task_summary.split('\n'):
            print(f"   {line}")
    
    # Recent decisions
    decisions = session_memory.get_recent_decisions(limit=5)
    print("\n🧠 RECENT DECISIONS:")
    if decisions:
        for i, dec in enumerate(decisions[-5:], 1):
            print(f"   {i}. {dec.get('decision', 'Unknown')}")
            rationale = dec.get('rationale', '')
            if rationale:
                print(f"      └─ {rationale[:60]}...")
    else:
        print("   No decisions logged")
    
    # Cache stats
    stats = session_memory.get_cache_stats()
    print("\n💾 CACHE STATISTICS:")
    print(f"   Cached files: {stats.get('cached_files', 0)}")
    print(f"   Logged decisions: {stats.get('logged_decisions', 0)}")
    print(f"   Tracked tasks: {stats.get('tasks_tracked', 0)}")
    print(f"   Disk usage: {stats.get('disk_usage_bytes', 0) / 1024:.1f} KB")
    print(f"   Cache TTL: {stats.get('ttl_minutes', 0)} minutes")
    
    print("\n" + "=" * 70)


def handle_memory_stats(args, session_memory) -> None:
    """
    Display detailed cache usage statistics.
    """
    stats = session_memory.get_cache_stats()
    
    print("\n" + "=" * 70)
    print("SESSION MEMORY STATISTICS")
    print("=" * 70)
    
    print("\n📊 CACHE CONTENTS:")
    print(f"   Cached file contexts: {stats.get('cached_files', 0)}")
    print(f"   Logged decisions: {stats.get('logged_decisions', 0)}")
    print(f"   Tracked tasks: {stats.get('tasks_tracked', 0)}")
    
    print("\n💾 DISK USAGE:")
    disk_kb = stats.get('disk_usage_bytes', 0) / 1024
    disk_mb = disk_kb / 1024
    if disk_mb > 0:
        print(f"   Total: {disk_mb:.2f} MB ({disk_kb:.1f} KB)")
    else:
        print(f"   Total: {disk_kb:.1f} KB")
    print(f"   Files: {stats.get('cache_files', 0)}")
    print(f"   Location: {stats.get('cache_dir', 'Unknown')}")
    
    print("\n⏱️  CONFIGURATION:")
    print(f"   Cache TTL: {stats.get('ttl_minutes', 0)} minutes")
    print(f"   Max cache entries: {session_memory.MAX_CACHE_ENTRIES}")
    print(f"   Max file size: 1.0 MB")
    
    is_stale = session_memory.invalidate_if_stale()
    print(f"\n🔄 SESSION STATUS:")
    if is_stale:
        print("   Status: ⚠️  STALE (invalidated)")
    else:
        print("   Status: ✓ Active")
    
    print("\n" + "=" * 70)


def handle_memory_clear(args, session_memory) -> None:
    """
    Clear session memory cache.
    
    With --force, clears without confirmation.
    """
    force = getattr(args, 'force', False)
    
    if not force:
        response = input("Clear session memory cache? This will remove all cached context. (y/N): ")
        if response.lower() != 'y':
            print("Cancelled")
            return
    
    try:
        session_memory.cleanup()
        print("✓ Session memory cache cleared")
    except Exception as e:
        print(f"❌ Failed to clear cache: {e}", file=sys.stderr)
        sys.exit(1)


def handle_memory_tasks(args, session_memory) -> None:
    """
    Display tracked tasks.
    """
    if not hasattr(args, 'task_file'):
        print("❌ No task file specified")
        return
    
    # Would integrate with manage_todo_list tool
    # For now, show what's in session memory
    stats = session_memory.get_cache_stats()
    
    print("\n" + "=" * 70)
    print("TRACKED TASKS")
    print("=" * 70)
    
    if stats.get('tasks_tracked', 0) == 0:
        print("\nNo tasks currently tracked in session memory")
    else:
        print(f"\nTracked {stats.get('tasks_tracked', 0)} tasks in session")
    
    print("=" * 70 + "\n")
