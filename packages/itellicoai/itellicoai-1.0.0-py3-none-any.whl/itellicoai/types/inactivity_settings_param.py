# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import TypedDict

__all__ = ["InactivitySettingsParam"]


class InactivitySettingsParam(TypedDict, total=False):
    end_call_timeout_ms: Optional[int]
    """Time in milliseconds of user inactivity before ending the call.

    Only used when reminders are disabled (reminder_timeout_ms is null). Set to null
    to never auto-end calls. Minimum 10000ms (10 seconds), maximum 600000ms (10
    minutes).
    """

    reminder_max_count: int
    """Maximum number of reminder messages to send when reminders are enabled.

    Only used when reminder_timeout_ms is set.
    """

    reminder_timeout_ms: Optional[int]
    """Time in milliseconds to wait before sending a reminder when user is silent.

    Only used when reminder_max_count > 0. Minimum 5000ms (5 seconds), maximum
    300000ms (5 minutes).
    """

    reset_on_activity: bool
    """Whether to reset the reminder count when the user becomes active again.

    When true (default), the counter resets after user activity. When false,
    reminders are cumulative throughout the conversation.
    """
