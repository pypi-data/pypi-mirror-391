# -*- mode: python -*-
# vi: set ft=python

"""Cross-platform user data retrieval utilities.

This package provides functions to list system users, get the current
username, and retrieve detailed user information in a platform-agnostic way.

"""

from getuser.get import (
    UserRecord,
    get_current_username,
    get_user_info,
    list_users,
)

__all__ = [
    "UserRecord",
    "get_current_username",
    "get_user_info",
    "list_users",
]
