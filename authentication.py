"""Password verification and database-backed ChurchManager authentication."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import socket

from authorization import UserSession


class AuthenticationError(RuntimeError):
    """Generic authentication failure that does not reveal the failing field."""


class PasswordService:
    """Argon2id password hashing isolated behind a small application interface."""

    def __init__(self, hasher=None):
        if hasher is None:
            try:
                from argon2 import PasswordHasher
            except ImportError as error:
                raise RuntimeError(
                    "ChurchManager password support requires argon2-cffi."
                ) from error
            hasher = PasswordHasher()
        self._hasher = hasher

    def hash(self, password: str) -> str:
        if len(password) < 12:
            raise ValueError("A ChurchManager password must contain at least 12 characters.")
        return self._hasher.hash(password)

    def verify(self, password_hash: str, password: str) -> bool:
        try:
            return bool(self._hasher.verify(password_hash, password))
        except Exception as error:
            if error.__class__.__name__ in {
                "VerifyMismatchError", "VerificationError", "InvalidHashError"
            }:
                return False
            raise

    def needs_rehash(self, password_hash: str) -> bool:
        checker = getattr(self._hasher, "check_needs_rehash", None)
        return bool(checker and checker(password_hash))


@dataclass(frozen=True)
class UserAccount:
    id: int
    username: str
    display_name: str
    password_hash: str
    active: bool
    is_master: bool
    must_change_password: bool
    failed_login_count: int
    locked_until: datetime | None


class MariaDBUserRepository:
    """Parameterized access to ChurchManager identities and permissions."""

    def __init__(self, connection):
        self.connection = connection
        module = connection.__class__.__module__
        self.parameter_marker = "%s" if module.startswith("mysql.connector") else "?"

    def _execute(self, cursor, sql, values=None):
        sql = sql.replace("?", self.parameter_marker)
        if values is None:
            return cursor.execute(sql)
        return cursor.execute(sql, values)

    def _execute_one(self, sql, values=()):
        cursor = self.connection.cursor()
        try:
            self._execute(cursor, sql, values)
            return cursor.fetchone()
        finally:
            cursor.close()

    def find_by_username(self, username: str) -> UserAccount | None:
        row = self._execute_one(
            "SELECT ID, Username, DisplayName, PasswordHash, Active, "
            "MasterAdministrator, MustChangePassword, FailedLoginCount, LockedUntil "
            "FROM tblUser WHERE Username = ?",
            (username,),
        )
        return UserAccount(*row) if row else None

    def has_users(self) -> bool:
        return bool(self._execute_one("SELECT COUNT(*) FROM tblUser")[0])

    def create_initial_master(self, username, display_name, password_hash):
        cursor = self.connection.cursor()
        try:
            self._execute(cursor, "SELECT COUNT(*) FROM tblUser")
            if cursor.fetchone()[0]:
                raise RuntimeError("Initial setup is unavailable after users exist.")
            self._execute(cursor,
                "INSERT INTO tblUser "
                "(Username, DisplayName, PasswordHash, Active, "
                "MasterAdministrator, MustChangePassword) VALUES (?, ?, ?, 1, 1, 0)",
                (username, display_name, password_hash),
            )
            user_id = cursor.lastrowid
            self._execute(cursor, "SELECT ID FROM tblRole WHERE Name='Master Administrator'")
            role = cursor.fetchone()
            if not role:
                raise RuntimeError("The Master Administrator role is not installed.")
            self._execute(cursor,
                "INSERT INTO tblUserRole (UserID, RoleID, AssignedByUserID) "
                "VALUES (?, ?, ?)",
                (user_id, role[0], user_id),
            )
            self._execute(cursor,
                "INSERT INTO tblSecurityAuditEvent "
                "(UserID, Action, EntityType, EntityID, Reason) "
                "VALUES (?, 'MASTER_BOOTSTRAPPED', 'User', ?, 'Initial test setup')",
                (user_id, str(user_id)),
            )
            self.connection.commit()
            return user_id
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def change_password(self, user_id, password_hash, must_change=False):
        cursor = self.connection.cursor()
        try:
            self._execute(cursor,
                "UPDATE tblUser SET PasswordHash=?, MustChangePassword=? WHERE ID=?",
                (password_hash, int(bool(must_change)), user_id),
            )
            self._execute(cursor,
                "INSERT INTO tblSecurityAuditEvent "
                "(UserID, Action, EntityType, EntityID) "
                "VALUES (?, 'PASSWORD_CHANGED', 'User', ?)",
                (user_id, str(user_id)),
            )
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def permissions_for(self, user_id: int) -> tuple[frozenset[int], frozenset[str]]:
        cursor = self.connection.cursor()
        try:
            self._execute(cursor,
                "SELECT DISTINCT r.ID FROM tblUserRole ur "
                "JOIN tblRole r ON r.ID=ur.RoleID AND r.Active=1 "
                "WHERE ur.UserID=? "
                "AND (ur.EffectiveFrom IS NULL OR ur.EffectiveFrom <= CURRENT_TIMESTAMP) "
                "AND (ur.EffectiveUntil IS NULL OR ur.EffectiveUntil > CURRENT_TIMESTAMP)",
                (user_id,),
            )
            role_ids = frozenset(row[0] for row in cursor.fetchall())
            self._execute(cursor,
                "SELECT DISTINCT p.Name FROM tblUserRole ur "
                "JOIN tblRole r ON r.ID=ur.RoleID AND r.Active=1 "
                "JOIN tblRolePermission rp ON rp.RoleID=r.ID "
                "JOIN tblPermission p ON p.ID=rp.PermissionID AND p.Active=1 "
                "WHERE ur.UserID=? "
                "AND (ur.EffectiveFrom IS NULL OR ur.EffectiveFrom <= CURRENT_TIMESTAMP) "
                "AND (ur.EffectiveUntil IS NULL OR ur.EffectiveUntil > CURRENT_TIMESTAMP)",
                (user_id,),
            )
            permissions = frozenset(row[0] for row in cursor.fetchall())
        finally:
            cursor.close()
        return role_ids, permissions

    def record_failed_login(self, user_id: int, failed_count: int, locked_until) -> None:
        cursor = self.connection.cursor()
        try:
            self._execute(cursor,
                "UPDATE tblUser SET FailedLoginCount=?, LockedUntil=? WHERE ID=?",
                (failed_count, locked_until, user_id),
            )
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def record_successful_login(self, user_id: int, login_at, replacement_hash=None) -> None:
        cursor = self.connection.cursor()
        try:
            if replacement_hash:
                self._execute(cursor,
                    "UPDATE tblUser SET FailedLoginCount=0, LockedUntil=NULL, "
                    "LastLoginAt=?, PasswordHash=? WHERE ID=?",
                    (login_at, replacement_hash, user_id),
                )
            else:
                self._execute(cursor,
                    "UPDATE tblUser SET FailedLoginCount=0, LockedUntil=NULL, "
                    "LastLoginAt=? WHERE ID=?",
                    (login_at, user_id),
                )
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def record_auth_event(self, user_id, action, workstation, occurred_at, username=None):
        cursor = self.connection.cursor()
        try:
            self._execute(cursor,
                "INSERT INTO tblSecurityAuditEvent "
                "(UserID, Action, EntityType, EntityID, Workstation, OccurredAt) "
                "VALUES (?, ?, 'User', ?, ?, ?)",
                (user_id, action, username, workstation, occurred_at),
            )
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()


class AuthenticationService:
    MAX_FAILURES = 5
    LOCKOUT = timedelta(minutes=15)
    FAILURE_MESSAGE = "The username or password is incorrect, or the account is unavailable."

    def __init__(self, repository, passwords: PasswordService, clock=None, workstation=None):
        self.repository = repository
        self.passwords = passwords
        self.clock = clock or (lambda: datetime.now(timezone.utc).replace(tzinfo=None))
        self.workstation = workstation or socket.gethostname

    def authenticate(self, username: str, password: str) -> UserSession:
        now = self.clock()
        normalized_username = (username or "").strip()
        account = self.repository.find_by_username(normalized_username)
        if account is None or not account.active:
            self.repository.record_auth_event(
                account.id if account else None, "LOGIN_FAILED", self.workstation(),
                now, normalized_username,
            )
            raise AuthenticationError(self.FAILURE_MESSAGE)
        if account.locked_until and account.locked_until > now:
            self.repository.record_auth_event(
                account.id, "LOGIN_FAILED_LOCKED", self.workstation(), now,
                normalized_username,
            )
            raise AuthenticationError(self.FAILURE_MESSAGE)
        if not self.passwords.verify(account.password_hash, password or ""):
            failures = account.failed_login_count + 1
            locked_until = now + self.LOCKOUT if failures >= self.MAX_FAILURES else None
            self.repository.record_failed_login(account.id, failures, locked_until)
            self.repository.record_auth_event(
                account.id, "LOGIN_FAILED", self.workstation(), now,
                normalized_username,
            )
            raise AuthenticationError(self.FAILURE_MESSAGE)

        replacement = None
        if self.passwords.needs_rehash(account.password_hash):
            replacement = self.passwords.hash(password)
        self.repository.record_successful_login(account.id, now, replacement)
        workstation = self.workstation()
        self.repository.record_auth_event(
            account.id, "LOGIN_SUCCEEDED", workstation, now, None,
        )
        role_ids, permissions = self.repository.permissions_for(account.id)
        return UserSession(
            user_id=account.id,
            username=account.username,
            display_name=account.display_name,
            is_master=bool(account.is_master),
            permissions=permissions,
            role_ids=role_ids,
            login_at=now,
            workstation=workstation,
            must_change_password=bool(account.must_change_password),
        )
