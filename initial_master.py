"""Create the first ChurchManager master administrator during installation."""

from __future__ import annotations

import re

from authentication import MariaDBUserRepository, PasswordService


_USERNAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{2,99}$")


class InitialMasterError(ValueError):
    """Raised when the initial administrator details are not acceptable."""


class InitialMasterBootstrapper:
    """Validate, hash, and atomically create exactly one initial master user."""

    def __init__(self, connection, password_service=None, repository=None):
        self.passwords = password_service or PasswordService()
        self.repository = repository or MariaDBUserRepository(connection)

    def create(
        self, username, display_name, password, confirmation,
        email=None, phone=None,
    ):
        """Create the first master without retaining or returning its password."""
        username = str(username or "").strip()
        display_name = str(display_name or "").strip()
        if not _USERNAME.fullmatch(username):
            raise InitialMasterError(
                "Username must contain at least three letters, numbers, periods, "
                "hyphens, or underscores."
            )
        if not display_name:
            raise InitialMasterError("Display name is required.")
        if len(display_name) > 255:
            raise InitialMasterError("Display name is too long.")
        email = str(email or "").strip() or None
        phone = str(phone or "").strip() or None
        if email and (len(email) > 254 or "@" not in email):
            raise InitialMasterError("Email address is invalid.")
        if phone and len(phone) > 50:
            raise InitialMasterError("Phone number is too long.")
        if password != confirmation:
            raise InitialMasterError("The passwords do not match.")
        try:
            password_hash = self.passwords.hash(password)
            return self.repository.create_initial_master(
                username, display_name, password_hash, email, phone,
            )
        except ValueError as error:
            raise InitialMasterError(str(error)) from error
        finally:
            password = ""
            confirmation = ""
