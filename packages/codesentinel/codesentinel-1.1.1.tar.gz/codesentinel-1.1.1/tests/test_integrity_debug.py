#!/usr/bin/env python
"""Debug integrity command execution."""
import sys
import traceback

try:
    from codesentinel.cli import main
    sys.argv = ["codesentinel", "integrity", "status"]
    main()
except Exception as e:
    print(f"Full error details:")
    traceback.print_exc()
    print(f"\nError type: {type(e).__name__}")
    print(f"Error message: {e}")
