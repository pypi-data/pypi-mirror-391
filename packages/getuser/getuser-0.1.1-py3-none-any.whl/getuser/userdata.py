# -*- mode: python -*-
# vi: set ft=python

"""A data class representing user information across platforms."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

__all__ = ["UserRecord"]


@dataclass
class UserRecord:  # pylint: disable=too-many-instance-attributes
    """Rser record representing the common intersection of fields.

    from Unix, Windows and macOS user entries.

    Field mapping notes:
      - username: login name / short name (Unix: pw_name,
            Windows: sAMAccountName / local user name, macOS: RecordName)
      - unique_id: platform-specific unique id as string:
          Unix/macOS -> UID (e.g. "1000")
          Windows    -> SID (e.g. "S-1-5-21-...") or AD objectSid as string
      - display_name: human-readable full name (GECOS/RealName/displayName)
      - home_directory: user's home/profile directory (path string)
      - primary_group: name or id of primary group (string)
      - is_enabled: account enabled/active flag when available (None if unknown)
      - platform_details: free-form dict for platform-specific extra attributes

    """

    username: str
    unique_id: str | None = None
    display_name: str | None = None
    home_directory: str | None = None
    primary_group: str | None = None
    is_enabled: bool | None = None
    platform_details: dict[str, Any] = field(default_factory=dict)  # type: ignore[misc]
