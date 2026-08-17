import unittest

from database_provisioning import (
    DatabaseProvisioningError,
    FreshDatabaseProvisioner,
)


class DatabaseFailure(Exception):
    pass


class Cursor:
    def __init__(self, database_exists=0, account_exists=0, fail_on=None):
        self.responses = iter(((database_exists,), (account_exists,)))
        self.response = None
        self.fail_on = fail_on
        self.executed = []
        self.closed = False

    def execute(self, sql, values=None):
        self.executed.append((sql, values))
        if self.fail_on and self.fail_on in sql:
            raise DatabaseFailure("failure")
        if sql.startswith("SELECT COUNT"):
            self.response = next(self.responses)

    def fetchone(self):
        return self.response

    def close(self):
        self.closed = True


class Connection:
    def __init__(self, cursor):
        self.value = cursor

    def cursor(self):
        return self.value


class DatabaseProvisioningTests(unittest.TestCase):
    def create(self, cursor=None, **changes):
        cursor = cursor or Cursor()
        values = {
            "database_name": "ChurchManager_Grace",
            "application_user": "churchmanager_grace",
            "application_password": "long-random-password-value",
            "confirmation": "ChurchManager_Grace",
        }
        values.update(changes)
        result = FreshDatabaseProvisioner(
            Connection(cursor), database_errors=(DatabaseFailure,),
        ).create(**values)
        return result, cursor

    def test_creates_utf8_database_and_scoped_account(self):
        result, cursor = self.create()
        statements = [sql for sql, _values in cursor.executed]
        self.assertEqual(result.database_name, "ChurchManager_Grace")
        self.assertTrue(any("CREATE DATABASE `ChurchManager_Grace`" in sql for sql in statements))
        self.assertTrue(any("GRANT ALL PRIVILEGES ON `ChurchManager_Grace`.*" in sql for sql in statements))
        password_calls = [values for sql, values in cursor.executed if "IDENTIFIED BY" in sql]
        self.assertEqual(password_calls, [("long-random-password-value",)])
        self.assertFalse(any("long-random-password-value" in sql for sql in statements))
        self.assertTrue(cursor.closed)

    def test_refuses_existing_database(self):
        with self.assertRaisesRegex(DatabaseProvisioningError, "already exists"):
            self.create(Cursor(database_exists=1))

    def test_requires_exact_confirmation(self):
        with self.assertRaisesRegex(DatabaseProvisioningError, "exact database name"):
            self.create(confirmation="wrong")

    def test_rejects_remote_account_host(self):
        with self.assertRaisesRegex(DatabaseProvisioningError, "only a local"):
            self.create(application_host="%")

    def test_failure_removes_only_new_resources(self):
        cursor = Cursor(fail_on="GRANT ALL")
        with self.assertRaisesRegex(DatabaseProvisioningError, "could not be created"):
            self.create(cursor)
        statements = [sql for sql, _values in cursor.executed]
        self.assertTrue(any(sql.startswith("DROP USER IF EXISTS") for sql in statements))
        self.assertTrue(any(sql == "DROP DATABASE IF EXISTS `ChurchManager_Grace`" for sql in statements))


if __name__ == "__main__":
    unittest.main()
