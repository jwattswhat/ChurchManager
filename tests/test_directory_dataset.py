from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT.parent / "JSForm"))

from visual_reports.directory_dataset import (
    DIRECTORY_CONTRACT, DirectoryDatasetProvider, contact_line,
)


class FakeAuthorization:
    def __init__(self, allowed=True):
        self.allowed = allowed
        self.checked = []

    def require(self, permission, operation=None):
        self.checked.append((permission, operation))
        if not self.allowed:
            raise PermissionError(permission)


class FakeCursor:
    def __init__(self):
        self.description = ()
        self.executed = []

    def execute(self, sql, values):
        self.executed.append((sql, values))
        selected = sql.split("FROM", 1)[0].replace("SELECT", "", 1)
        self.description = tuple((part.strip().split(".")[-1],) for part in selected.split(","))

    def fetchall(self):
        return []

    def close(self):
        pass


class FakeConnection:
    __module__ = "mariadb.connections"

    def __init__(self):
        self.last_cursor = None

    def cursor(self):
        self.last_cursor = FakeCursor()
        return self.last_cursor


class TestDirectoryDatasetProvider(unittest.TestCase):
    def test_contact_label_follows_value(self):
        self.assertEqual(
            contact_line({"Contact": "555-0100", "ContactLabel": "Home", "Type": "Phone"}),
            "555-0100 (Home)",
        )
        self.assertEqual(
            contact_line({"Contact": "name@example.com", "ContactLabel": "", "Type": "Email"}),
            "name@example.com (Email)",
        )

    def test_permission_is_required_before_database_access(self):
        connection = FakeConnection()
        with self.assertRaises(PermissionError):
            DirectoryDatasetProvider(connection, FakeAuthorization(False)).build(1)
        self.assertIsNone(connection.last_cursor)

    def test_provider_uses_only_report_views_and_exact_contract(self):
        connection = FakeConnection()
        authorization = FakeAuthorization()
        dataset = DirectoryDatasetProvider(connection, authorization).build(1)
        self.assertEqual(
            authorization.checked[0][0], "reports.membership.contact"
        )
        sql = "\n".join(statement for statement, _ in connection.last_cursor.executed)
        self.assertNotIn("FROM tbl", sql)
        self.assertNotIn("JOIN tbl", sql)
        self.assertIn("rpt_person_contact", sql)
        self.assertEqual(set(dataset.collections), {
            collection.name for collection in DIRECTORY_CONTRACT.collections
        })
        self.assertIn("directory_entries", dataset.collections)


if __name__ == "__main__":
    unittest.main()
