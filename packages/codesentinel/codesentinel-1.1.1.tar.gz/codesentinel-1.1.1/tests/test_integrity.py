#!/usr/bin/env python3
import sys
import traceback
sys.path.insert(0, '.')

# Patch sys.exit to see traceback
original_exit = sys.exit
def patched_exit(code=0):
    print(f"\nsys.exit called with code: {code}")
    traceback.print_stack()
    original_exit(code)

sys.exit = patched_exit

try:
    from codesentinel.cli import main
    sys.argv = ['codesentinel', 'integrity', 'status']
    main()
except Exception as e:
    print("Exception caught:")
    traceback.print_exc()
