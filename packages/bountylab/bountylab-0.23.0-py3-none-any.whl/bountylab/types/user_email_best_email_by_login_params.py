# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._types import SequenceNotStr
from .._utils import PropertyInfo

__all__ = ["UserEmailBestEmailByLoginParams", "Signals"]


class UserEmailBestEmailByLoginParams(TypedDict, total=False):
    logins: Required[SequenceNotStr[str]]
    """Array of GitHub usernames (1-100)"""

    signals: Signals
    """Optional signal data for tracking email context (body, subject, sender)"""


class Signals(TypedDict, total=False):
    email_body: Annotated[str, PropertyInfo(alias="emailBody")]
    """Email body content for tracking"""

    email_subject: Annotated[str, PropertyInfo(alias="emailSubject")]
    """Email subject for tracking"""

    sender: str
    """Sender identifier for tracking"""
