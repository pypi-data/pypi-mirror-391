"""
Utility functions for the 'alert' command in the CodeSentinel CLI.

This module provides alert configuration management and sending capabilities.
"""

import json
import sys
from pathlib import Path


def handle_alert_config(args, config_manager):
    """
    Handle alert configuration operations.
    
    Args:
        args: Parsed command-line arguments
        config_manager: Configuration manager instance
    """
    from codesentinel.utils.config import ConfigManager
    
    if args.show:
        _show_alert_config(config_manager)
        return
    
    changes_made = False
    
    # Channel enable/disable
    if args.enable_channel:
        _enable_channel(config_manager, args.enable_channel)
        changes_made = True
    
    if args.disable_channel:
        _disable_channel(config_manager, args.disable_channel)
        changes_made = True
    
    # Email settings
    if args.set_email:
        _set_email_config(config_manager, 'email', args.set_email)
        changes_made = True
    
    if args.set_smtp_server:
        _set_email_config(config_manager, 'smtp_server', args.set_smtp_server)
        changes_made = True
    
    if args.set_smtp_port:
        _set_email_config(config_manager, 'smtp_port', args.set_smtp_port)
        changes_made = True
    
    # Slack settings
    if args.set_slack_webhook:
        _set_slack_config(config_manager, args.set_slack_webhook)
        changes_made = True
    
    # Severity filter
    if args.set_severity_filter:
        _set_severity_filter(config_manager, args.set_severity_filter)
        changes_made = True
    
    if changes_made:
        print("\n✓ Alert configuration updated successfully")
        _show_alert_config(config_manager)
    elif not args.show:
        print("❌ No configuration changes specified")
        print("   Use --show to view current settings or other flags to modify configuration")


def _show_alert_config(config_manager):
    """Display current alert configuration."""
    print("\n" + "=" * 70)
    print("ALERT CONFIGURATION")
    print("=" * 70)
    
    # Get alert config - the structure is alerts -> {console, email, slack, file}
    # NOT alerts -> channels -> {console, email, etc}
    alerts_config = config_manager.get('alerts', {})
    
    if not alerts_config:
        print("\n⚠️  No alert configuration found")
        print("   Run with configuration flags to set up alerts")
        print("=" * 70)
        return
    
    print("\nEnabled Channels:")
    
    # The channels are directly under 'alerts', not 'alerts.channels'
    for channel_name in ['console', 'file', 'email', 'slack']:
        channel_config = alerts_config.get(channel_name, {})
        if not isinstance(channel_config, dict):
            continue
            
        status = "✓ ENABLED" if channel_config.get('enabled', False) else "✗ DISABLED"
        print(f"  {status:12} {channel_name}")
        
        # Show channel-specific settings
        if channel_name == 'email' and channel_config.get('enabled'):
            email = channel_config.get('email', 'Not set')
            server = channel_config.get('smtp_server', 'Not set')
            port = channel_config.get('smtp_port', 'Not set')
            print(f"               Email: {email}")
            print(f"               SMTP: {server}:{port}")
        
        elif channel_name == 'slack' and channel_config.get('enabled'):
            webhook = channel_config.get('webhook_url', 'Not set')
            webhook_display = webhook[:40] + '...' if len(webhook) > 40 else webhook
            print(f"               Webhook: {webhook_display}")
        
        elif channel_name == 'file' and channel_config.get('enabled'):
            log_file = channel_config.get('log_file', 'logs/alerts.log')
            print(f"               Log File: {log_file}")
    
    # Show severity filter
    severity_filter = config_manager.get('alerts.severity_filter', 'info')
    print(f"\nMinimum Severity: {severity_filter.upper()}")
    
    print("=" * 70)


def _enable_channel(config_manager, channel):
    """Enable an alert channel."""
    key = f'alerts.{channel}.enabled'
    config_manager.set(key, True)
    print(f"✓ Enabled {channel} channel")


def _disable_channel(config_manager, channel):
    """Disable an alert channel."""
    key = f'alerts.{channel}.enabled'
    config_manager.set(key, False)
    print(f"✓ Disabled {channel} channel")


def _set_email_config(config_manager, setting, value):
    """Set email configuration."""
    key = f'alerts.email.{setting}'
    config_manager.set(key, value)
    print(f"✓ Set email {setting}: {value}")


def _set_slack_config(config_manager, webhook_url):
    """Set Slack webhook URL."""
    key = 'alerts.slack.webhook_url'
    config_manager.set(key, webhook_url)
    print(f"✓ Set Slack webhook URL")


def _set_severity_filter(config_manager, severity):
    """Set minimum severity filter."""
    key = 'alerts.severity_filter'
    config_manager.set(key, severity)
    print(f"✓ Set minimum severity to: {severity.upper()}")


def handle_alert_send(args, config_manager):
    """
    Handle sending an alert.
    
    Args:
        args: Parsed command-line arguments
        config_manager: Configuration manager instance
    """
    from codesentinel.utils.alerts import AlertManager
    
    alert_manager = AlertManager(config_manager)
    
    # Determine if this is a subcommand call or legacy direct call
    message = args.message if hasattr(args, 'message') and args.message else None
    
    if not message:
        print("❌ No alert message provided")
        return
    
    title = args.title if hasattr(args, 'title') else 'Manual Alert'
    severity = args.severity if hasattr(args, 'severity') else 'info'
    channels = args.channels if hasattr(args, 'channels') and args.channels else None
    
    print(f"\n📢 Sending {severity.upper()} alert...")
    print(f"   Title: {title}")
    print(f"   Message: {message}")
    if channels:
        print(f"   Channels: {', '.join(channels)}")
    
    try:
        alert_manager.send_alert(
            title=title,
            message=message,
            severity=severity,
            channels=channels
        )
        print("✓ Alert sent successfully")
    except Exception as e:
        print(f"❌ Failed to send alert: {e}")
