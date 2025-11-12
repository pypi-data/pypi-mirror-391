#!/usr/bin/env python
"""Test the dev-audit --tools command parsing"""

import sys
import argparse

# Simulate the parser setup
parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest='command')

dev_audit_parser = subparsers.add_parser('dev-audit')
dev_audit_parser.add_argument('--silent', action='store_true')
dev_audit_parser.add_argument('--agent', action='store_true')
dev_audit_parser.add_argument('--export', type=str)
dev_audit_parser.add_argument('--focus', type=str)
dev_audit_parser.add_argument('--tools', action='store_true')

# Parse the test command
test_args = ['dev-audit', '--tools']
args = parser.parse_args(test_args)

print(f"Command: {args.command}")
print(f"Tools flag: {getattr(args, 'tools', 'NOT FOUND')}")
print(f"All args: {args}")
