# -*- mode: python -*-
# vi: set ft=python

"""Cross-platform user data retrieval utilities.

This package provides functions to list system users, get the current
username, and retrieve detailed user information in a platform-agnostic way.

"""

from getuser.error import GetUserError
from getuser.get import (
    UserRecord,
    get_current_username,
    get_user_info,
    list_users,
)

__version__ = "0.1.1"

__all__ = [
    "GetUserError",
    "UserRecord",
    "get_current_username",
    "get_user_info",
    "list_users",
]
