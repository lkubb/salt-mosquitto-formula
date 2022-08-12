"""
Salt execution module to manage Eclipse Mosquitto installations using mosquitto-go-auth.

This code can actually mostly be used for vanilla Mosquitto as well @TODO resynthesize.
"""

from pathlib import Path

try:
    import sqlite3

    HAS_SQLITE3 = True
except ImportError:
    HAS_SQLITE3 = False

import salt.utils.path
from salt.exceptions import CommandExecutionError, SaltInvocationError

# __utils__ dunder is deprecated
import mosquitto

__virtualname__ = "mosquitto_goauth"

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

        salt '*' mosquitto_goauth.add_user foo 5up3rsE3(ure

    username
        The user's username.

    password
        The password the user should have. Convenience function if you accept
        the defaults, otherwise generate the hash and pass it as password_hash.
        You can generate the hash with ``mosquitto_goauth.get_pw_hash``.

    password_hash
        The hash of the password the user should have. Generate it with
        ``mosquitto_goauth.get_pw_hash``.

    update
        If the user exists, update the password hash to match. Defaults to false.

    pw_file
        Path to the database/file that contains usernames and passwords. Defaults to
        ``/etc/mosquitto/passwd``. SQLite databases will be autodetected and treated as such.
    """

    if password is None and password_hash is None:
        raise SaltInvocationError(
            "You need to specify either password or password_hash."
        )

    users = _get_collection(pw_file)
    password_hash = password_hash or get_pw_hash(password)
    return users.add(username, password_hash, update=update)


def check_password(
    password, username=None, pw_hash=None, pw_file=MOSQUITTO_DEFAULT_PW_PATH
):
    """
    Check a Mosquitto Go Auth password.

    CLI Example:

    .. code-block:: bash

        salt '*' mosquitto_goauth.check_password 5up3rsE3(ure foo

    password
        The password to check.

    username
        The username of the user to check the password for. Overrides pw_hash.

    pw_hash
        The password string to check for equivalency.

    pw_file
        Path to the database/file that contains usernames and passwords. Defaults to
        ``/etc/mosquitto/passwd``. SQLite databases will be autodetected and treated as such.
    """

    if pw_hash is None and (username is None or pw_file is None):
        raise SaltInvocationError(
            "You need to specify either username + pw_file or pw_hash."
        )

    if username is not None and pw_file is not None:
        users = _get_collection(pw_file)
        pw_hash = users.get_password(username)

    return mosquitto.MosquittoGoauthPassword.from_string(pw_hash).check_password(
        password
    )


def get_pw_hash(
    password, iterations=100000, hmac_hash="sha512", keylen=32, salt_size=16
):
    """
    Get a password hash suitable for Mosquitto Go Auth.

    CLI Example:

    .. code-block:: bash

        salt '*' mosquitto_goauth.get_pw_hash hunter1

    password
        The password to hash.

    iterations
        Number of hashing iterations. Defaults 100000 (mosquitto-go-auth default).

    hmac_hash
        Hashing algorithm for PBKDF2. One of ["sha512", "sha256"]. Defaults to sha512 (mosquitto-go-auth default.

    keylen
        Byte count of the resulting hash. Defaults to 32 (mosquitto-go-auth default).

    salt_size
        Byte count of the random salt. Defaults to 16 (mosquitto-go-auth default).
    """

    try:
        pw = mosquitto.MosquittoGoauthPassword.from_password(
            password,
            hmac_hash=hmac_hash,
            iterations=iterations,
            keylen=keylen,
            salt_size=salt_size,
        )
    except ValueError as e:
        raise CommandExecutionError(str(e))

    return pw.to_string()


def list_users(include_pass=False, pw_file=MOSQUITTO_DEFAULT_PW_PATH):
    """
    List all Mosquitto users.

    CLI Example:

    .. code-block:: bash

        salt '*' mosquitto_goauth.list_users

    include_pass
        Whether to include the password hashes. Defaults to false.

    pw_file
        Path to the database/file that contains usernames and passwords. Defaults to
        ``/etc/mosquitto/passwd``. SQLite databases will be autodetected and treated as such.
    """

    users = _get_collection(pw_file)
    return users.ls(include_pass)


def rm_user(username, pw_file=MOSQUITTO_DEFAULT_PW_PATH):
    """
    Remove a Mosquitto user.

    CLI Example:

    .. code-block:: bash

        salt '*' mosquitto_goauth.rm_user foo

    username
        The user's username.

    pw_file
        Path to the database/file that contains usernames and passwords. Defaults to
        ``/etc/mosquitto/passwd``. SQLite databases will be autodetected and treated as such.
    """

    users = _get_collection(pw_file)
    return users.rm(username)


def user_exists(username, pw_file=MOSQUITTO_DEFAULT_PW_PATH):
    """
    Check whether a Mosquitto user exists.

    CLI Example:

    .. code-block:: bash

        salt '*' mosquitto_goauth.user_exists foo

    username
        The user's username.

    pw_file
        Path to the database/file that contains usernames and passwords. Defaults to
        ``/etc/mosquitto/passwd``. SQLite databases will be autodetected and treated as such.
    """

    users = _get_collection(pw_file)
    return users.exists(username)


def _check_sqlite_file(path):
    contextkey = f"mosquitto_goauth._check_sqlite_file.{path}"

    if contextkey not in __context__:
        path = Path(path)

        if not path.exists():
            raise CommandExecutionError(f"Path {path} does not exist.")

        with open(path, "rb") as f:
            header = f.read(16)

        __context__[contextkey] = header == b"SQLite format 3\00"

    return __context__[contextkey]


def _get_collection(path):
    if _check_sqlite_file(path):
        return SQLiteUserCollection(path)
    return FileUserCollection(path)


class UserCollection:
    def __init__(self, pw_file):
        pw_file = Path(pw_file)
        if not pw_file.exists():
            raise CommandExecutionError(f"Path {path} does not exist.")
        self.pw_file = pw_file

    def add(self, username, pw_hash, update=False):
        if self.exists(username) and not update:
            raise CommandExecutionError(
                f"User {username} exists. To update the password, set update=True."
            )
        return self._add(username, pw_hash)

    def exists(self, username):
        raise NotImplementedError

    def get_password(self, username):
        raise NotImplementedError

    def ls(self, include_pass=False):
        raise NotImplementedError

    def rm(self, username):
        if not self.exists(username):
            raise CommandExecutionError(f"Username {username} does not exist.")
        return self._rm(username)


class FileUserCollection(UserCollection):
    def exists(self, username):
        return username in self.ls()

    def get_password(self, username):
        users = self.ls(True)
        if username not in users:
            raise CommandExecutionError(f"User {username} does not exist.")
        return users[username]

    def ls(self, include_pass=False):
        return mosquitto.read_pw_file(self.pw_file, include_pass=include_pass)

    def _add(self, username, pw_hash):
        users = self.ls(include_pass=True)
        users[username] = pw_hash
        return mosquitto.write_pw_file(self.pw_file, users)

    def _rm(self, username):
        users = self.ls(include_pass=True)
        users.pop(username)
        return mosquitto.write_pw_file(self.pw_file, users)


class SQLiteUserCollection(UserCollection):
    def exists(self, username):
        query = "select count(*) from `users` where `username` = ?"
        cur = self._cur()
        cur.execute(query, [username])
        return bool(cur.fetchone()[0])

    def get_password(self, username):
        query = "select `password_hash` from `users` where `username` = ?"
        cur = self._cur()
        cur.execute(query, [username])
        res = cur.fetchone()
        if res is None:
            raise CommandExecutionError(f"User {username} does not exist.")
        return res[0]

    def ls(self, include_pass=False):
        query = "select username"
        if include_pass:
            query += ", password_hash"
        query += " from `users`"
        cur = self._cur()
        cur.execute(query, [])
        users = cur.fetchall()
        if include_pass:
            return dict(users)
        return [x[0] for x in users]

    def _add(self, username, pw_hash):
        if self.exists(username):
            query = "update `users` set `password_hash` = ? where `username` = ?"
            params = [pw_hash, username]
        else:
            query = "insert into `users` (username, password_hash, is_admin) VALUES (?, ?, false)"
            params = [username, pw_hash]
        cur = self._cur()
        cur.execute(query, params)
        return True

    def _rm(self, username):
        query = "delete from `users` where `username` = ?"
        cur = self._cur()
        cur.execute(query, [username])
        return True

    def _cur(self):
        if not HAS_SQLITE3:
            raise SaltInvocationError(
                "Running this function requires sqlite3 library. Make sure it is importable by Salt."
            )
        if not hasattr(self, "connection"):
            self.connection = sqlite3.connect(self.pw_file, isolation_level=None)
        return self.connection.cursor()
