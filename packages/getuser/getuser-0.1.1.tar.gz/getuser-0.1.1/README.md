
# getuser

A small, cross-platform Python library for retrieving system user information.

## Build

We use Rubisco to build GitHub release.

```bash
ru dist
```

We use Hatchling to build PyPI release.

```bash
python -m build
```

## Installation

- Prerequisites: Python 3.8 or newer.
- On Windows, the `pywin32` dependency is required; it is declared conditionally in `pyproject.toml`.

Install locally (recommended inside a virtual environment):

```bash
python -m pip install getuser
```

## Quick Start

Use the library from Python:

```python
from getuser import get_current_username, get_user_info, list_users

print(get_current_username())
for username in list_users():
    info = get_user_info(username)
    print(username, info)
```

Run the package as a module from the command line:

```bash
python -m getuser
```

This prints the list of users, the current user, and a JSON-formatted user record for each user.

## API

- `get_current_username() -> str`
  - Returns the username of the current user.

- `get_user_info(username: str) -> UserRecord | None`
  - Returns a `UserRecord` for the given username, or `None` if the user does not exist.
  - `UserRecord` fields:
    - `username`: :ogin name.
    - `unique_id`: Platform-specific unique identifier. (UID on Unix as a string, SID on Windows)
    - `display_name`: Full name of the user.
    - `home_directory`: User home/profile directory.
    - `primary_group`: Primary group name or id
    - `is_enabled`: Account enabled flag (bool or `None` if unknown)
    - `platform_details`: Raw platform-specific information. (It may be unserializable)

- `list_users() -> list[str]`
  - Returns a list of usernames on the system (strings only).

## Platform Support and Implementation Notes

- Unix-like systems (Linux, macOS): Implementation in `getuser/unix.py` using `pwd`, `grp`, and `getpass`. The GECOS field is parsed to populate display name and related fields.

- Windows: Implementation in `getuser/win32.py` using `pywin32` (`win32api`, `win32net`, `win32security`). The `unique_id` is a SID string. `platform_details` contains the raw dictionary returned by `NetUserGetInfo`.

## Example Output

Running `python -m getuser` produces output similar to the following (example on Windows):

```text
Users:
        Administrator
        ChenPi11
        DefaultAccount
        Guest
Current user: ChenPi11
User record for Administrator:
{
    "username": "Administrator",
    "unique_id": "S-*-*-*-*-*-*-*",
    "display_name": "Administrator",
    "home_directory": "",
    "primary_group": "Administrator",
    "is_enabled": false,
    "platform_details": {
        "name": "Administrator",
        "password": null,
        "password_age": 0,
        "priv": 2,
        "home_dir": "",
        "comment": "***",
        "flags": *,
        "script_path": "",
        "auth_flags": 0,
        "full_name": "",
        "usr_comment": "",
        "parms": "",
        "workstations": "",
        "last_logon": 0,
        "last_logoff": 0,
        "acct_expires": *,
        "max_storage": *,
        "units_per_week": *,
        "logon_hours": "b'*'",
        "bad_pw_count": 0,
        "num_logons": 0,
        "logon_server": "\\\\*",
        "country_code": 0,
        "code_page": 0,
        "user_sid": "<PySID object at 0x0000011CB363EA70>",
        "primary_group_id": *,
        "profile": "",
        "home_dir_drive": "",
        "password_expired": 0
    }
}
User record for ChenPi11:
{
    "username": "ChenPi11",
    "unique_id": "S-*-*-*-*-*-*-*",
    "display_name": "\u9648\u6ea2\u98de",
    "home_directory": "",
    "primary_group": "ChenPi11",
    "is_enabled": true,
    "platform_details": {
        ...
    }
}
```

## Development & Testing

Install development dependencies (optional):

```bash
python -m pip install -e .[dev,ruff]
```

Recommended tools: `ruff`, `pylint`, `pyright` (see `pyproject.toml`).

## License and Author

- License: The Unlicense (See `LICENSE` in the repository root).
- Author: ChenPi11 (<wushengwuxi-msctinoulk@outlook.com>)
