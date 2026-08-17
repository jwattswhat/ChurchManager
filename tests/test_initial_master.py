import unittest

from initial_master import InitialMasterBootstrapper, InitialMasterError


class Passwords:
    def __init__(self):
        self.values = []

    def hash(self, value):
        self.values.append(value)
        if len(value) < 12:
            raise ValueError("A ChurchManager password must contain at least 12 characters.")
        return "argon2:" + value


class Repository:
    def __init__(self):
        self.created = []

    def create_initial_master(self, username, display_name, password_hash, email=None, phone=None):
        self.created.append((username, display_name, password_hash, email, phone))
        return 7


class InitialMasterTests(unittest.TestCase):
    def service(self):
        repository = Repository(); passwords = Passwords()
        return InitialMasterBootstrapper(None, passwords, repository), repository, passwords

    def test_creates_master_with_hash_only(self):
        service, repository, passwords = self.service()
        result = service.create(" admin.user ", " Administrator ", "long password value", "long password value")
        self.assertEqual(result, 7)
        self.assertEqual(passwords.values, ["long password value"])
        self.assertEqual(repository.created, [
            ("admin.user", "Administrator", "argon2:long password value", None, None),
        ])

    def test_rejects_invalid_identity_fields(self):
        service, repository, _passwords = self.service()
        with self.assertRaisesRegex(InitialMasterError, "Username"):
            service.create("a", "Administrator", "long password value", "long password value")
        with self.assertRaisesRegex(InitialMasterError, "Display name is required"):
            service.create("admin", "", "long password value", "long password value")
        self.assertFalse(repository.created)

    def test_rejects_mismatched_or_short_passwords(self):
        service, repository, _passwords = self.service()
        with self.assertRaisesRegex(InitialMasterError, "do not match"):
            service.create("admin", "Administrator", "long password value", "other password")
        with self.assertRaisesRegex(InitialMasterError, "at least 12"):
            service.create("admin", "Administrator", "short", "short")
        self.assertFalse(repository.created)

    def test_repository_marks_bootstrap_password_for_change(self):
        source = __import__("pathlib").Path("authentication.py").read_text(encoding="utf-8")
        self.assertIn(
            "MasterAdministrator, MustChangePassword) VALUES (?, ?, ?, ?, ?, 1, 1, 1)",
            source,
        )

    def test_accepts_optional_contact_information(self):
        service, repository, _passwords = self.service()
        service.create(
            "admin", "Administrator", "long password value", "long password value",
            "admin@example.org", "5555550100",
        )
        self.assertEqual(
            repository.created[0][3:], ("admin@example.org", "5555550100"),
        )


if __name__ == "__main__":
    unittest.main()
