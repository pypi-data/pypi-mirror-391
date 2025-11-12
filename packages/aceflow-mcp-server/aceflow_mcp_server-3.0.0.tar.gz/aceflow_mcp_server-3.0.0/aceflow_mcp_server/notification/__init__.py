"""
Notification module for contract updates.

This module provides functionality for:
- Email notifications (SMTP)
- DingTalk notifications (future)
- Notification templates
- Message formatting
"""

from .email import EmailNotifier

__all__ = ['EmailNotifier']
