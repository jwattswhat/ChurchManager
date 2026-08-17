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

    def create_initial_master(self, username, display_name, password_hash):
        self.created.append((username, display_name, password_hash))
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
        self.assertEqual(repository.created, [("admin.user", "Administrator", "argon2:long password value")])

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


if __name__ == "__main__":
    unittest.main()
