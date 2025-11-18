# -*- mode: python -*-
# vi: set ft=python

"""User information retrieval utilities interface with platform detection."""

from __future__ import annotations

import os

from getuser.error import GetUserError
from getuser.userdata import UserRecord

__all__ = [
    "UserRecord",
    "get_current_username",
    "get_user_info",
    "list_users",
]

if os.name == "posix":
    from getuser.unix import (
        get_current_username_unix,
        get_user_info_unix,
        list_users_unix,
    )

    def get_current_username() -> str:
        """Get the username of the current user.

        Returns:
            str: The username of the current user.

        Raises:
            GetUserError: If unable to retrieve the current username.

        """
        try:
            return get_current_username_unix()
        except Exception as exc:
            raise GetUserError(str(exc)) from exc

    def get_user_info(username: str) -> UserRecord | None:
        """Get user information for the specified username.

        Args:
            username (str): The username to query.

        Returns:
            UserRecord | None: UserRecord if found, None otherwise.

        Raises:
            GetUserError: If unable to retrieve user information.

        """
        try:
            return get_user_info_unix(username)
        except Exception as exc:
            raise GetUserError(str(exc)) from exc

    def list_users() -> list[str]:
        """List all users on the system.

        We don't load all user details here for performance reasons.

        Returns:
            list[str]: A list of all usernames.

        Raises:
            GetUserError: If unable to list users.

        """
        try:
            return list_users_unix()
        except Exception as exc:
            raise GetUserError(str(exc)) from exc

elif os.name == "nt":
    from getuser.win32 import (
        get_current_username_win32,
        get_user_info_win32,
        list_users_win32,
    )

    def get_current_username() -> str:
        """Get the username of the current user.

        Returns:
            str: The username of the current user.

        Raises:
            GetUserError: If unable to retrieve the current username.

        """
        try:
            return get_current_username_win32()
        except Exception as exc:
            raise GetUserError(str(exc)) from exc

    def get_user_info(username: str) -> UserRecord | None:
        """Get user information for the specified username.

        Args:
            username (str): The username to query.

        Returns:
            UserRecord | None: UserRecord if found, None otherwise.

        Raises:
            GetUserError: If unable to retrieve user information.

        """
        try:
            return get_user_info_win32(username)
        except Exception as exc:
            raise GetUserError(str(exc)) from exc

    def list_users() -> list[str]:
        """List all users on the system.

        We don't load all user details here for performance reasons.

        Returns:
            list[str]: A list of all usernames.

        Raises:
            GetUserError: If unable to list users.

        """
        try:
            return list_users_win32()
        except Exception as exc:
            raise GetUserError(str(exc)) from exc

else:
    _MSG = f"Unsupported platform: {os.name}"
    raise NotImplementedError(_MSG)
