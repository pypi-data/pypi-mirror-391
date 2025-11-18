# -*- mode: python -*-
# vi: set ft=python
# pylint: skip-file

"""User information retrieval utilities for Unix-like systems."""

from __future__ import annotations

import os

if os.name == "posix":
    import getpass
    import grp
    import pwd
    from dataclasses import dataclass

    from getuser.userdata import UserRecord

    __all__ = [
        "get_current_username_unix",
        "get_user_info_unix",
        "list_users_unix",
    ]

    @dataclass
    class GECOS:
        """GECOS information structure."""

        full_name: str = ""
        email: str = ""
        phone: str = ""
        department: str = ""
        office: str = ""
        other: str = ""
        original: str = ""

        @classmethod
        def parse(cls, gecos: str) -> GECOS:
            """Parse GECOS string into GECOS object.

            Args:
                gecos (str): GECOS string.

            Returns:
                GECOS: GECOS object.

            """
            parts = gecos.split(",")
            return cls(
                full_name=parts[0] if len(parts) > 0 else "",
                email=parts[1] if len(parts) > 1 else "",
                phone=parts[2] if len(parts) > 2 else "",  # noqa: PLR2004
                department=parts[3] if len(parts) > 3 else "",  # noqa: PLR2004
                office=parts[4] if len(parts) > 4 else "",  # noqa: PLR2004
                other=parts[5] if len(parts) > 5 else "",  # noqa: PLR2004
                original=gecos,
            )

    def get_user_info_unix(username: str) -> UserRecord | None:
        """Get user information for Unix-like systems.

        Args:
            username: The username to query.

        Returns:
            UserRecord | None: The user record or None if user not found.

        """
        try:
            pwnam = pwd.getpwnam(username)
        except KeyError:
            return None

        # 1. Base user information.
        uid_str = str(pwnam.pw_uid)
        gecos = GECOS.parse(pwnam.pw_gecos)
        display_name = gecos.full_name or pwnam.pw_name
        home_directory = pwnam.pw_dir

        # 2. Group information.
        primary_gid = pwnam.pw_gid
        try:
            primary_group_name = grp.getgrgid(primary_gid).gr_name
        except KeyError:
            # Fallback to GID if group name not found.
            primary_group_name = str(primary_gid)

        # 3. Account status.
        # In Unix, typically checked by shell being /sbin/nologin or /bin/false.
        disabled_shells = {"/sbin/nologin", "/usr/sbin/nologin", "/bin/false"}
        is_enabled = pwnam.pw_shell not in disabled_shells

        # 4. Platform-specific details.
        platform_details: dict[str, object] = {
            "uid": pwnam.pw_uid,
            "gid": pwnam.pw_gid,
            "gecos": gecos,
            "shell": pwnam.pw_shell,
        }

        # 5. Construct and return UserRecord.
        return UserRecord(
            username=pwnam.pw_name,
            unique_id=uid_str,
            display_name=display_name,
            home_directory=home_directory,
            primary_group=primary_group_name,
            is_enabled=is_enabled,
            platform_details=platform_details,
        )

    def get_current_username_unix() -> str:
        """Get the username of the current user.

        Returns:
            str: The username of the current user.

        """
        return getpass.getuser()

    def list_users_unix() -> list[str]:
        """List all usernames on the system.

        Returns:
            list[str]: A list of all usernames.

        """
        return [pwnam.pw_name for pwnam in pwd.getpwall()]
