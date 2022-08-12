"""
Salt execution module to manage Eclipse Mosquitto installations.
"""

import re
from pathlib import Path

import salt.utils.path
from salt.exceptions import CommandExecutionError, SaltInvocationError

# __utils__ dunder is deprecated
import mosquitto

__virtualname__ = "mosquitto"

MOSQUITTO_DEFAULT_PW_PATH = "/etc/mosquitto/passwd"


def __virtual__():
    return True


def add_user(
    username,
    password=None,
    password_hash=None,
    update=False,
    pw_file=MOSQUITTO_DEFAULT_PW_PATH,
):
    """
    Add or update a Mosquitto user.

    CLI Example:

    .. code-block:: bash

        salt '*' mosquitto.add_user foo 5up3rsE3(ure

    username
        The user's username.

    password
        The password the user should have. Convenience function if you accept
        the defaults, otherwise generate the hash and pass it as password_hash.
        You can generate the hash with ``mosquitto.get_pw_hash``.

    password_hash
        The hash of the password the user should have. Generate it with
        ``mosquitto.get_pw_hash``.

    update
        If the user exists, update the password to match. Defaults to false.

    pw_file
        Path to the file that contains usernames and passwords. Defaults to "/etc/mosquitto/passwd".
    """

    if password is None and password_hash is None:
        raise SaltInvocationError(
            "You need to specify either password or password_hash."
        )

    users = list_users(include_pass=True, pw_file=pw_file)

    if username in users and not update:
        raise CommandExecutionError(
            f"User {username} exists. To update the password, set update=True."
        )

    if not _validate_username(username):
        raise CommandExecutionError(
            f"Username is invalid. Make sure it does not contain a colon or control characters."
        )

    password_hash = password_hash or get_pw_hash(password)
    users[username] = password_hash
    return mosquitto.write_pw_file(pw_file, users)


def check_password(
    password, username=None, pw_hash=None, pw_file=MOSQUITTO_DEFAULT_PW_PATH
):
    """
    Check a Mosquitto password.

    CLI Example:

    .. code-block:: bash

        salt '*' mosquitto.check_password 5up3rsE3(ure foo

    password
        The password to check.

    username
        The username of the user to check the password for. Overrides pw_hash.

    pw_hash
        The password string to check for equivalency.

    pw_file
        Path to the file that contains usernames and passwords. Defaults to "/etc/mosquitto/passwd".
    """

    if username is None and pw_hash is None:
        raise SaltInvocationError(
            "You need to specify either username (+ pw_file) or pw_hash."
        )

    if username is not None:
        users = list_users(include_pass=True, pw_file=pw_file)
        if username not in users:
            raise CommandExecutionError(f"User {username} does not exist.")
        pw_hash = users[username]

    return mosquitto.MosquittoPassword.from_string(pw_hash).check_password(password)


def get_pw_hash(password, pbkdf2=True, iterations=101):
    """
    Get a password hash suitable for Mosquitto.

    CLI Example:

    .. code-block:: bash

        salt '*' mosquitto.get_pw_hash hunter1

    password
        The password to hash.

    pbkdf2
        Whether to use pbkdf2_sha512 hashing algorithm. For versions 1.6 and below, this should be false.
        Defaults to true.

    iterations
        If pbkdf2 is true, number of hashing iterations. Defaults to 101 (mosquitto default).
    """

    try:
        pw = mosquitto.MosquittoPassword.from_password(
            password,
            algo="pbkdf2" if pbkdf2 else "sha512",
            iterations=iterations,
        )
    except ValueError as e:
        raise CommandExecutionError(str(e))

    return pw.to_string()


def list_users(include_pass=False, pw_file=MOSQUITTO_DEFAULT_PW_PATH):
    """
    List all Mosquitto users.

    CLI Example:

    .. code-block:: bash

        salt '*' mosquitto.list_users

    include_pass
        Whether to include the hashed passwords. Defaults to false.

    pw_file
        Path to the file that contains usernames and passwords. Defaults to "/etc/mosquitto/passwd".
    """

    return mosquitto.read_pw_file(pw_file, include_pass=include_pass)


def rm_user(username, pw_file=MOSQUITTO_DEFAULT_PW_PATH):
    """
    Remove a Mosquitto user.

    CLI Example:

    .. code-block:: bash

        salt '*' mosquitto.rm_user foo

    username
        The user's username.

    pw_file
        Path to the file that contains usernames and passwords. Defaults to "/etc/mosquitto/passwd".
    """

    users = list_users(include_pass=True, pw_file=pw_file)

    if username not in users:
        raise CommandExecutionError(f"User {username} does not exist.")
    users.pop(username)
    return mosquitto.write_pw_file(pw_file, users)


def user_exists(username, pw_file=MOSQUITTO_DEFAULT_PW_PATH):
    """
    Check whether a Mosquitto user exists.

    CLI Example:

    .. code-block:: bash

        salt '*' mosquitto.user_exists foo

    username
        The user's username.

    pw_file
        Path to the file that contains usernames and passwords. Defaults to "/etc/mosquitto/passwd".
    """

    return username in list_users(pw_file=pw_file)


def _validate_username(username):
    """
    Mosquitto usernames must not contain control characters, colons or be longer than 2**16 bytes.
    """

    if len(str(username)) > 65536:
        return False
    if not re.match(r"^((?=[^\x00-\x1F\x7F\u2028\u2029]).)*$", username):
        return False
    return True
