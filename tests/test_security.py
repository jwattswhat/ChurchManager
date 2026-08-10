from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import unittest

from authentication import (
    AuthenticationError, AuthenticationService, MariaDBUserRepository,
    PasswordService, UserAccount,
)
from authorization import (
    AuthorizationDenied, ChurchManagerAuthorizationPolicy, UserSession,
)


class FakeHasher:
    def hash(self, password):
        return "hashed:" + password

    def verify(self, password_hash, password):
        if password_hash != "hashed:" + password:
            error = type("VerifyMismatchError", (Exception,), {})
            raise error()
        return True

    def check_needs_rehash(self, password_hash):
        return password_hash.startswith("old:")


class FakeRepository:
    def __init__(self, account=None, permissions=()):
        self.account = account
        self.permissions = frozenset(permissions)
        self.failures = []
        self.successes = []
        self.events = []

    def find_by_username(self, username):
        return self.account if self.account and self.account.username == username else None

    def permissions_for(self, user_id):
        return frozenset({7}), self.permissions

    def record_failed_login(self, user_id, count, locked_until):
        self.failures.append((user_id, count, locked_until))

    def record_successful_login(self, user_id, login_at, replacement_hash=None):
        self.successes.append((user_id, login_at, replacement_hash))

    def record_auth_event(self, user_id, action, workstation, occurred_at, username=None):
        self.events.append((user_id, action, workstation, occurred_at, username))


def account(**overrides):
    values = dict(
        id=1, username="jonathan", display_name="Jonathan Watt",
        password_hash="hashed:correct horse", active=True, is_master=False,
        must_change_password=False, failed_login_count=0, locked_until=None,
    )
    values.update(overrides)
    return UserAccount(**values)


class TestPasswordService(unittest.TestCase):
    def test_passwords_require_twelve_characters(self):
        service = PasswordService(FakeHasher())
        with self.assertRaises(ValueError):
            service.hash("too short")

    def test_hash_and_verify_are_delegated(self):
        service = PasswordService(FakeHasher())
        password_hash = service.hash("a long passphrase")
        self.assertNotEqual(password_hash, "a long passphrase")
        self.assertTrue(service.verify(password_hash, "a long passphrase"))
        self.assertFalse(service.verify(password_hash, "wrong password"))

    def test_installed_argon2_service_creates_argon2id_hash(self):
        service = PasswordService()
        password_hash = service.hash("correct horse battery staple")
        self.assertTrue(password_hash.startswith("$argon2id$"))
        self.assertTrue(service.verify(password_hash, "correct horse battery staple"))
        self.assertFalse(service.verify(password_hash, "incorrect passphrase"))


class TestAuthenticationService(unittest.TestCase):
    NOW = datetime(2026, 8, 10, 18, 0)

    def service(self, repository):
        return AuthenticationService(
            repository, PasswordService(FakeHasher()),
            clock=lambda: self.NOW, workstation=lambda: "TEST-PC",
        )

    def test_success_returns_attributed_session_and_clears_failures(self):
        repository = FakeRepository(account(), {"accounting.transactions.view"})
        session = self.service(repository).authenticate("jonathan", "correct horse")
        self.assertEqual(session.user_id, 1)
        self.assertEqual(session.workstation, "TEST-PC")
        self.assertIn("accounting.transactions.view", session.permissions)
        self.assertEqual(repository.successes, [(1, self.NOW, None)])
        self.assertEqual(repository.events[0][1], "LOGIN_SUCCEEDED")

    def test_unknown_disabled_and_locked_accounts_share_generic_error(self):
        repositories = (
            FakeRepository(None),
            FakeRepository(account(active=False)),
            FakeRepository(account(locked_until=self.NOW + timedelta(minutes=1))),
        )
        messages = []
        for repository in repositories:
            with self.assertRaises(AuthenticationError) as caught:
                self.service(repository).authenticate("jonathan", "correct horse")
            messages.append(str(caught.exception))
        self.assertEqual(len(set(messages)), 1)
        self.assertTrue(all(repository.events for repository in repositories))

    def test_fifth_failure_locks_for_fifteen_minutes(self):
        repository = FakeRepository(account(failed_login_count=4))
        with self.assertRaises(AuthenticationError):
            self.service(repository).authenticate("jonathan", "wrong password")
        self.assertEqual(repository.failures[0][0:2], (1, 5))
        self.assertEqual(repository.failures[0][2], self.NOW + timedelta(minutes=15))
        self.assertEqual(repository.events[0][1], "LOGIN_FAILED")


class TestDatabaseConnectorCompatibility(unittest.TestCase):
    def test_mysql_connector_uses_percent_s_parameters(self):
        connection_type = type("CMySQLConnection", (), {})
        connection_type.__module__ = "mysql.connector.connection_cext"
        repository = MariaDBUserRepository(connection_type())
        calls = []
        cursor = type(
            "Cursor", (), {"execute": lambda self, sql, values: calls.append((sql, values))}
        )()
        repository._execute(cursor, "SELECT ?", (1,))
        self.assertEqual(calls, [("SELECT %s", (1,))])

    def test_mariadb_connector_keeps_question_mark_parameters(self):
        connection_type = type("Connection", (), {})
        connection_type.__module__ = "mariadb.connections"
        repository = MariaDBUserRepository(connection_type())
        calls = []
        cursor = type(
            "Cursor", (), {"execute": lambda self, sql, values: calls.append((sql, values))}
        )()
        repository._execute(cursor, "SELECT ?", (1,))
        self.assertEqual(calls, [("SELECT ?", (1,))])


class TestAuthorizationPolicy(unittest.TestCase):
    def test_permission_is_required_for_ordinary_user(self):
        session = UserSession(1, "user", "User", False, frozenset({"person.view"}))
        policy = ChurchManagerAuthorizationPolicy(session)
        self.assertTrue(policy.can_open("person.view"))
        self.assertFalse(policy.can_update("person.edit"))
        with self.assertRaises(AuthorizationDenied):
            policy.require("person.edit", "edit people")

    def test_master_has_every_named_permission_but_missing_declarations_fail_closed(self):
        policy = ChurchManagerAuthorizationPolicy(
            UserSession(1, "master", "Master", True)
        )
        self.assertTrue(policy.can_invoke("new.permission"))
        self.assertFalse(policy.can_open(None))

    def test_session_is_required(self):
        with self.assertRaises(ValueError):
            ChurchManagerAuthorizationPolicy(None)

    def test_session_records_required_password_change(self):
        session = UserSession(
            1, "user", "User", False, must_change_password=True
        )
        self.assertTrue(session.must_change_password)


class TestUserAdministrationRules(unittest.TestCase):
    def test_last_active_master_cannot_be_disabled(self):
        from user_admin import UserAdministrationService

        with self.assertRaisesRegex(ValueError, "last active master"):
            UserAdministrationService.ensure_can_disable(True, 1)

    def test_ordinary_or_redundant_master_accounts_can_be_disabled(self):
        from user_admin import UserAdministrationService

        UserAdministrationService.ensure_can_disable(False, 1)
        UserAdministrationService.ensure_can_disable(True, 2)

    def test_role_permission_editor_preserves_inherent_master_access(self):
        source = (Path(__file__).parents[1] / "user_admin.py").read_text(
            encoding="utf-8-sig"
        )
        self.assertIn("Master Administrator permissions are inherent", source)
        self.assertIn("ROLE_PERMISSIONS_CHANGED", source)
        self.assertIn('"security.roles.manage"', source)

    def test_security_audit_viewer_is_read_only_and_permission_protected(self):
        source = (Path(__file__).parents[1] / "user_admin.py").read_text(
            encoding="utf-8-sig"
        )
        self.assertIn('"security.audit.view"', source)
        self.assertIn("class SecurityAuditDialog", source)
        audit_dialog = source.split("class SecurityAuditDialog", 1)[1].split(
            "class UserAdministrationDialog", 1
        )[0]
        self.assertNotIn("DELETE FROM", audit_dialog)
        self.assertNotIn("UPDATE ", audit_dialog)


if __name__ == "__main__":
    unittest.main()
