"""Tests for the congregation-branded ChurchManager login presentation."""

import inspect
import unittest

import wx

import login_dialog


class Cursor:
    def __init__(self, row=None, error=None):
        self.row = row
        self.error = error
        self.closed = False

    def execute(self, _sql):
        if self.error:
            raise self.error

    def fetchone(self):
        return self.row

    def close(self):
        self.closed = True


class Connection:
    def __init__(self, cursor):
        self.value = cursor

    def cursor(self):
        return self.value


class LoginIdentityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = wx.GetApp() or wx.App(False)

    def test_congregation_name_comes_from_church_record(self):
        cursor = Cursor(("Reformation Lutheran Church",))
        self.assertEqual(
            login_dialog.congregation_name(Connection(cursor)),
            "Reformation Lutheran Church",
        )
        self.assertTrue(cursor.closed)

    def test_congregation_name_fails_safe_for_login(self):
        cursor = Cursor(error=RuntimeError("database unavailable"))
        self.assertEqual(
            login_dialog.congregation_name(Connection(cursor)),
            "Local Congregation",
        )
        self.assertTrue(cursor.closed)

    def test_login_shows_product_release_and_license_identity(self):
        source = inspect.getsource(login_dialog.LoginDialog)
        self.assertIn("ChurchManager", source)
        self.assertIn("congregation_name", source)
        self.assertIn("__version__", source)
        self.assertIn("COPYRIGHT_NOTICE", source)
        self.assertIn("LICENSE_NOTICE", source)
        self.assertIn("APPLICATION_ICON", source)

    def test_login_dialog_constructs_with_the_ico_asset(self):
        dialog = login_dialog.LoginDialog(None, "Reformation Lutheran Church")
        try:
            labels = [child.GetLabel() for child in dialog.GetChildren()
                      if isinstance(child, wx.StaticText)]
            self.assertIn("ChurchManager", labels)
            self.assertIn("Reformation Lutheran Church", labels)
        finally:
            dialog.Destroy()


if __name__ == "__main__":
    unittest.main()
