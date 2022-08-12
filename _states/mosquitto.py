"""
Salt state module to manage Eclipse Mosquitto installations.
"""

from salt.exceptions import CommandExecutionError, SaltInvocationError

MOSQUITTO_DEFAULT_PW_PATH = "/etc/mosquitto/passwd"


def user_present(
    name,
    password=None,
    password_pillar=None,
    manage_password=True,
    pw_file=MOSQUITTO_DEFAULT_PW_PATH,
    goauth=False,
    hash_opts=None,
):
    """
    Make sure a user is present. Optionally make sure the password matches.

    name
        The user's username.

    password
        The password the user should have.

    password_pillar
        If password is unspecified, the pillar where to look up the user's password.

    manage_password
        If the user exists, make sure the password matches. Defaults to true.

    pw_file
        Path to the file that contains usernames and passwords. Defaults to "/etc/mosquitto/passwd".
        For goauth, SQLite databases will be autodetected and treated as such.

    goauth
        Whether to use mosquitto-go-auth format and defaults. This allows different backends.
        Currently, only the file and SQLite backends can be managed by this module.
        Defaults to false.

    hash_opts
        Mapping of password hashing parameters to values. They will be passed to the appropriate
        execution module's password hash generation function.

        For vanilla Mosquitto, those are:
        pbkdf2: true
        iterations: 101

        For mosquitto-go-auth, those are:
        iterations: 100000
        hmac_hash: sha512
        keylen: 32
        salt_size: 16

        For parameter descriptions, see the relevant execution module's documentation.
    """
    ret = {"name": name, "result": True, "comment": "", "changes": {}}

    password = password or __salt__["pillar.get"](password_pillar)
    update = False
    hash_opts = hash_opts or {}
    mosquitto = "mosquitto" if not goauth else "mosquitto_goauth"

    if password is None:
        ret["result"] = False
        ret[
            "comment"
        ] = "Found no password. Make sure password or password_pillar is specified. If password_pillar is used, make sure the pillar value exists on this minion."
        return ret

    try:
        if __salt__[f"{mosquitto}.user_exists"](name, pw_file=pw_file):
            if not manage_password:
                ret[
                    "comment"
                ] = f"User {name} already exists. The password was not checked."
                return ret
            if __salt__[f"{mosquitto}.check_password"](
                password, username=name, pw_file=pw_file
            ):
                ret["comment"] = f"The password for existing user {name} matches."
                return ret
            update = True

        if __opts__["test"]:
            ret["result"] = None
            ret["comment"] = f"User {name} would have been " + (
                "updated." if update else "added."
            )
            ret["changes"] = {"updated" if update else "added": name}
            return ret

        pw_hash = __salt__[f"{mosquitto}.get_pw_hash"](password, **hash_opts)

        if __salt__[f"{mosquitto}.add_user"](
            name,
            password_hash=pw_hash,
            update=update,
            pw_file=pw_file,
        ):
            ret["comment"] = f"User {name} has been " + (
                "updated." if update else "added."
            )
            ret["changes"] = {"updated" if update else "added": name}
        else:
            ret["result"] = False
            ret[
                "comment"
            ] = "Something went wrong. This should not happen at all since errors are raised."

    except (CommandExecutionError, SaltInvocationError) as e:
        ret["result"] = False
        ret["comment"] = str(e)
        return ret

    return ret


def user_absent(name, pw_file=MOSQUITTO_DEFAULT_PW_PATH, goauth=False):
    """
    Make sure a user is absent.

    name
        The user's username.

    pw_file
        Path to the file that contains usernames and passwords. Defaults to "/etc/mosquitto/passwd".

    goauth
        Whether to use mosquitto-go-auth format and defaults. This allows different backends.
        Currently, only the file and SQLite backends can be managed by this module.
        Defaults to false.
    """

    ret = {"name": name, "result": True, "comment": "", "changes": {}}
    mosquitto = "mosquitto" if not goauth else "mosquitto_goauth"

    try:
        if not __salt__[f"{mosquitto}.user_exists"](name, pw_file=pw_file):
            ret["comment"] = f"User {name} is already absent."
            return ret

        if __opts__["test"]:
            ret["result"] = None
            ret["comment"] = f"User {name} would have been removed."
            ret["changes"] = {"removed": name}
        elif __salt__[f"{mosquitto}.rm_user"](name, pw_file=pw_file):
            ret["comment"] = f"User {name} has been removed."
            ret["changes"] = {"removed": name}
        else:
            ret["result"] = False
            ret[
                "comment"
            ] = "Something went wrong. This should not happen at all since errors are raised."

    except (CommandExecutionError, SaltInvocationError) as e:
        ret["result"] = False
        ret["comment"] = str(e)
        return ret

    return ret
