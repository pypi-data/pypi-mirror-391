# -*- mode: python -*-
# vi: set ft=python

# pylint: skip-file

"""User information retrieval utilities for Windows."""

from __future__ import annotations

import os

if os.name == "nt":
    import warnings
    from typing import Any, cast

    import win32api
    import win32net
    import win32netcon
    import win32security
    from pywintypes import (  # pylint: disable=no-name-in-module
        error as PyWinTypeError,  # noqa: N812
    )

    from getuser.userdata import UserRecord

    __all__ = [
        "get_current_username_win32",
        "get_user_info_win32",
        "list_users_win32",
    ]

    # See https://learn.microsoft.com/en-us/windows/win32/netmgmt/network-management-error-codes
    NERR_USERNOTFOUND = 2221

    def get_user_info_win32(
        username: str,
        server: str = "",
    ) -> UserRecord | None:
        """Retrieve user information on a Windows system.

        Args:
            username (str): The name of the user to look up.
            server (str, optional): The server name. If None, the local machine
                is used. Defaults to "".

        Returns:
            A UserRecord object populated with the user's information,
            or None if the user is not found.

        """
        try:
            # See: https://docs.microsoft.com/en-us/windows/win32/api/lmaccess/ns-lmaccess-user_info_4
            user_info = cast(
                "dict[str, Any]",
                win32net.NetUserGetInfo(  # type: ignore[reportUnknownMemberType]
                    server,
                    username,
                    4,
                ),
            )

            # 1. Basic fields.
            sid_obj: Any = user_info["user_sid"]
            unique_id_str = win32security.ConvertSidToStringSid(sid_obj)

            display_name: str = user_info.get("full_name") or username
            home_directory = user_info.get("home_dir") or user_info.get(
                "profile",
            )

            # 2. Check account status.
            flags = user_info["flags"]
            is_enabled = not bool(flags & win32netcon.UF_ACCOUNTDISABLE)

            # 4. Get group information.
            primary_group_id = user_info["primary_group_id"]

            # 5. Look up primary group name.
            primary_group_name = str(primary_group_id)
            try:
                # Convert primary group ID to group name.
                group_name, _, _ = win32security.LookupAccountSid(
                    server,
                    win32security.GetBinarySid(unique_id_str),
                )
                primary_group_name = group_name
            except (PyWinTypeError, ValueError, OSError) as exc:
                warnings.warn(
                    "Could not look up primary group name for GID "
                    f"{primary_group_id}. Falling back to GID as name: {exc}",
                    RuntimeWarning,
                    1,
                )

            # 6. Fill platform_details.
            platform_details = user_info

            return UserRecord(
                username=user_info["name"],
                unique_id=unique_id_str,
                display_name=display_name,
                home_directory=home_directory,
                primary_group=primary_group_name,
                is_enabled=is_enabled,
                platform_details=platform_details,
            )

        except PyWinTypeError as exc:
            if exc.winerror == NERR_USERNOTFOUND:
                return None
            raise

    def get_current_username_win32() -> str:
        """Get the username of the current user.

        Returns:
            str: The username of the current user.

        """
        return win32api.GetUserName()

    def list_users_win32(
        server: str = "",
    ) -> list[str]:
        """List all users on a Windows system.

        Args:
            server (str, optional): The server name. If None, the local machine
                is used. Defaults to "".

        Returns:
            list[str]: A list of usernames for all users on the system.

        """
        # See: https://docs.microsoft.com/en-us/windows/win32/api/lmaccess/ns-lmaccess-user_info_4
        user_enum = cast(
            "list[dict[str, str]]",
            win32net.NetUserEnum(  # type: ignore[reportUnknownMemberType]
                server,
                0,
            )[0],
        )
        return [user["name"] for user in user_enum]
