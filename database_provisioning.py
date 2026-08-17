"""Guarded creation of a fresh ChurchManager database and application account."""

from __future__ import annotations

import re
from dataclasses import dataclass


_DATABASE = re.compile(r"^[A-Za-z][A-Za-z0-9_]{2,63}$")
_ACCOUNT = re.compile(r"^[A-Za-z][A-Za-z0-9_]{2,31}$")


class DatabaseProvisioningError(RuntimeError):
    """Raised when fresh database provisioning cannot proceed safely."""


@dataclass(frozen=True)
class ProvisionedDatabase:
    """Non-secret result of successful database and account creation."""

    database_name: str
    application_user: str
    application_host: str


def quote_identifier(value):
    """Quote one previously validated MariaDB identifier."""
    if not _DATABASE.fullmatch(str(value or "")):
        raise DatabaseProvisioningError("The database identifier is unsafe.")
    return "`" + str(value) + "`"


class FreshDatabaseProvisioner:
    """Create only a confirmed, nonexistent database using an admin connection.

    The caller owns the administrative connection and credential. This service
    never opens a connection, stores a password, or operates on an existing
    database.
    """

    def __init__(self, admin_connection, *, database_errors=(Exception,)):
        self.connection = admin_connection
        self.database_errors = database_errors

    @staticmethod
    def _validate(database_name, application_user, application_host, confirmation):
        database_name = str(database_name or "").strip()
        application_user = str(application_user or "").strip()
        application_host = str(application_host or "").strip().casefold()
        if not _DATABASE.fullmatch(database_name):
            raise DatabaseProvisioningError("The database name is invalid.")
        if not _ACCOUNT.fullmatch(application_user):
            raise DatabaseProvisioningError("The application account name is invalid.")
        if application_host not in {"localhost", "127.0.0.1", "::1"}:
            raise DatabaseProvisioningError(
                "Initial installation supports only a local MariaDB application account."
            )
        if str(confirmation or "") != database_name:
            raise DatabaseProvisioningError(
                "Database creation was not confirmed with the exact database name."
            )
        return database_name, application_user, application_host

    def create(
        self, database_name, application_user, application_password, *,
        application_host="localhost", confirmation=None,
    ):
        """Create a new UTF-8 database and database-scoped application account."""
        database_name, application_user, application_host = self._validate(
            database_name, application_user, application_host, confirmation,
        )
        password = str(application_password or "")
        if len(password) < 16:
            raise DatabaseProvisioningError(
                "The generated database account password must contain at least 16 characters."
            )
        database = quote_identifier(database_name)
        account = f"'{application_user}'@'{application_host}'"
        cursor = self.connection.cursor()
        database_created = False
        account_created = False
        try:
            cursor.execute(
                "SELECT COUNT(*) FROM information_schema.SCHEMATA WHERE SCHEMA_NAME=?",
                (database_name,),
            )
            if int(cursor.fetchone()[0]):
                raise DatabaseProvisioningError(
                    "The selected database already exists. Fresh installation will not overwrite it."
                )
            cursor.execute(
                "SELECT COUNT(*) FROM mysql.user WHERE User=? AND Host=?",
                (application_user, application_host),
            )
            if int(cursor.fetchone()[0]):
                raise DatabaseProvisioningError(
                    "The selected application database account already exists."
                )
            cursor.execute(
                f"CREATE DATABASE {database} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
            database_created = True
            cursor.execute(f"CREATE USER {account} IDENTIFIED BY ?", (password,))
            account_created = True
            cursor.execute(f"GRANT ALL PRIVILEGES ON {database}.* TO {account}")
            return ProvisionedDatabase(database_name, application_user, application_host)
        except DatabaseProvisioningError:
            raise
        except self.database_errors as error:
            if account_created:
                try:
                    cursor.execute(f"DROP USER IF EXISTS {account}")
                except self.database_errors:
                    pass
            if database_created:
                try:
                    cursor.execute(f"DROP DATABASE IF EXISTS {database}")
                except self.database_errors:
                    pass
            raise DatabaseProvisioningError(
                "The fresh ChurchManager database could not be created."
            ) from error
        finally:
            password = ""
            cursor.close()
