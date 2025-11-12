"""
Event utilities for EventBridge-based async communication.

Provides a unified way to emit events for:
- Domain events (OrderCreated, ProductUpdated, etc.)
- Notification events (UserInvitationRequested, etc.)
- Metrics events (trigger pre-computation)
"""

from .emitter import emit_event, emit_notification_event, EventSource, NotificationEventType

__all__ = [
    'emit_event',
    'emit_notification_event',
    'EventSource',
    'NotificationEventType'
]
