"""
Helper for Mosquitto password modules.
"""

import base64
import hashlib
import hmac
import secrets
from pathlib import Path

from salt.exceptions import CommandExecutionError


def read_pw_file(pw_file, include_pass=False):
    pw = _check_pw_file(pw_file)
    ret = []

    for line in pw.read_text().splitlines():
        if not line:
            continue

        parts = line.split(":")
        if not 2 == len(parts):
            raise CommandExecutionError(f"Could not parse {pw_file}.")
        user, userpass = parts
        if include_pass:
            ret.append((user, userpass))
        else:
            ret.append(user)

    if include_pass:
        return dict(ret)
    return ret


def _check_pw_file(pw_file):
    pw = Path(pw_file)

    if not pw.exists():
        raise CommandExecutionError(f"Password file {pw_file} does not exist.")
    return pw


def write_pw_file(pw_file, data):
    pw = _check_pw_file(pw_file)

    with open(pw, "w") as f:
        for user in sorted(data):
            f.write(f"{user}:{data[user]}\n")
    return True


class MosquittoPasswordBase:
    def __init__(
        self,
        salt,
        algo,
        hmac_hash,
        iterations,
        keylen,
        password=None,
        digest=None,
    ):
        self.salt = salt

        if algo not in ["sha512", "pbkdf2"]:
            raise ValueError("Supported hashing algorithms are sha512 and pbkdf2.")
        self.algo = algo

        if iterations < 1:
            raise ValueError("Need at least one iteration.")
        self.iterations = iterations
        self.keylen = keylen

        if hmac_hash not in ["sha256", "sha512"]:
            raise ValueError(
                "Hmac hashing function needs to be either sha256 or sha512."
            )
        self.hmac_hash = hmac_hash

        if password is None and digest is None:
            raise ValueError("Need at least either password or digest.")

        self.password = password if not isinstance(password, str) else password.encode()

        if digest is not None and not isinstance(digest, bytes):
            raise ValueError("Need digest as raw bytes.")
        self.digest = digest

    def check_password(self, password):
        # For testing purposes. Password should be always set.
        if not self.digest:
            self.digest = self._hash()
        pw_digest = self._hash(password)
        return hmac.compare_digest(pw_digest, self.digest)

    def to_string(self):
        if not self.digest:
            self.digest = self._hash()

        fmt_str = self._get_fmt()

        return fmt_str.format(
            algo=self._get_algo(),
            hmac_hash=self.hmac_hash,
            salt=self._get_salt_str(),
            digest=self._get_digest_str(),
            iterations=self.iterations,
            keylen=self.keylen,
        )

    def _get_fmt(self):
        raise NotImplementedError

    def _get_algo(self):
        raise NotImplementedError

    def _get_salt_str(self):
        return base64.b64encode(self.salt).decode()

    def _get_digest_str(self):
        return base64.b64encode(self.digest).decode()

    def _hash(self, password=None):
        if "pbkdf2" == self.algo:
            return self._hash_pbkdf2(password)
        return self._hash_sha512(password)

    def _hash_pbkdf2(self, password=None):
        password = password or self.password
        password = password.encode() if isinstance(password, str) else password
        return hashlib.pbkdf2_hmac(
            self.hmac_hash, password, self.salt, self.iterations, self.keylen
        )

    def _hash_sha512(self, password=None):
        password = password or self.password
        password = password.encode() if isinstance(password, str) else password

        h = hashlib.sha512()
        h.update(password)
        h.update(self.salt)
        return h.digest()


MOSQUITTO_ALGO = {"sha512": 6, "pbkdf2": 7}


class MosquittoPassword(MosquittoPasswordBase):
    def __init__(
        self,
        salt,
        algo,
        iterations,
        password=None,
        digest=None,
    ):
        if not 12 == len(salt):
            raise ValueError(
                "Password salt has to consist of exactly 12 (random) bytes."
            )
        if password is not None and len(password) > 65500:
            raise ValueError(
                "Password should have at most 65500 bytes. How has your day been?"
            )
        super().__init__(
            salt,
            algo,
            hmac_hash="sha512",
            iterations=iterations,
            keylen=64,
            password=password,
            digest=digest,
        )

    def _get_fmt(self):
        if "pbkdf2" == self.algo:
            return "${algo}${iterations}${salt}${digest}"
        return "${algo}${salt}${digest}"

    def _get_algo(self):
        return MOSQUITTO_ALGO[self.algo]

    @staticmethod
    def from_password(password, algo="pbkdf2", iterations=101):
        salt = secrets.token_bytes(12)
        return MosquittoPassword(
            salt, password=password, algo=algo, iterations=iterations
        )

    @staticmethod
    def from_string(s):
        s = s.split(":")[-1]
        s = s.strip("$")
        parts = s.split("$")

        if 3 == len(parts) and int(parts[0]) == MOSQUITTO_ALGO["sha512"]:
            _, salt, digest = parts
            algo = "sha512"
            # iterations are always 1 with sha512, not that it makes a difference
            iterations = 1
        elif 4 == len(parts) and int(parts[0]) == MOSQUITTO_ALGO["pbkdf2"]:
            _, iterations, salt, digest = parts
            algo = "pbkdf2"
        else:
            raise ValueError("Could not parse input string.")

        salt = base64.b64decode(salt)
        digest = base64.b64decode(digest)

        return MosquittoPassword(
            salt, digest=digest, algo=algo, iterations=int(iterations)
        )


class MosquittoGoauthPassword(MosquittoPasswordBase):
    def __init__(
        self,
        salt,
        hmac_hash="sha512",
        iterations=100000,
        keylen=32,
        password=None,
        digest=None,
    ):
        super().__init__(
            salt, "pbkdf2", hmac_hash, iterations, keylen, password, digest
        )

    def _get_fmt(self):
        return "{algo}${hmac_hash}${iterations}${salt}${digest}"

    def _get_algo(self):
        # currently, only PBKDF2 is supported
        return "PBKDF2"

    @staticmethod
    def from_password(
        password, hmac_hash="sha512", iterations=100000, keylen=32, salt_size=16
    ):
        salt = secrets.token_bytes(salt_size)
        return MosquittoGoauthPassword(
            salt,
            password=password,
            iterations=iterations,
            keylen=keylen,
            hmac_hash=hmac_hash,
        )

    @staticmethod
    def from_string(s):
        s = s.split(":")[-1]
        parts = s.split("$")

        if not 5 == len(parts):
            raise ValueError("Could not parse input string.")

        # currently, only PBKDF2 is supported
        algo, hmac_hash, iterations, salt, digest = parts

        salt = base64.b64decode(salt)
        digest = base64.b64decode(digest)
        keylen = len(digest)

        return MosquittoGoauthPassword(
            salt,
            digest=digest,
            iterations=int(iterations),
            hmac_hash=hmac_hash,
            keylen=keylen,
        )
