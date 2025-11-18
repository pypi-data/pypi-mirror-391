# -*- mode: python -*-
# vi: set ft=python

"""A example main module for getuser package."""

from getuser import get_current_username, get_user_info, list_users

if __name__ == "__main__":
    import json
    from dataclasses import asdict
    from sys import stdout

    stdout.write("Users:\n")
    for user in list_users():
        stdout.write(f"\t{user}\n")
    stdout.write(f"Current user: {get_current_username()}\n")
    for username_ in list_users():
        user_record = get_user_info(username_)
        if user_record:
            # Platform details may contain non-serializable objects; clear it.
            for key, value in user_record.platform_details.items():
                if not isinstance(value, (str, int, float, bool, type(None))):
                    user_record.platform_details[key] = repr(value)
            json_str = json.dumps(asdict(user_record), indent=4)
            stdout.write(f"User record for {username_}:\n{json_str}\n")
        else:
            stdout.write(f"User record for {username_} not found.\n")
        stdout.flush()
