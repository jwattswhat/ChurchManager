"""Run the explicit rollback-only GUI database persistence profile."""

from __future__ import annotations

import json
import os
from pathlib import Path
from types import SimpleNamespace

import mariadb
import wx

from churchmanager_mode import load_config, resolve_database
from project_dialog import ProjectEditorDialog
from project_repository import MariaDBProjectRepository
from project_service import ProjectService


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / ".gui-test-artifacts" / "database-profile.json"
OPT_IN = "CHURCHMANAGER_GUI_DATABASE"


def validate_target(settings):
    """Reject every non-local or non-test database target before connection."""
    host = str(settings.get("server") or "").casefold()
    database = str(settings.get("database") or "")
    if host not in {"127.0.0.1", "localhost", "::1"}:
        raise RuntimeError("Safety stop: gui-database requires a local server.")
    if database.casefold() != "churchdbtest":
        raise RuntimeError("Safety stop: gui-database requires ChurchDBTest.")
    if not settings.get("credential_target", "").endswith("LocalTestAdmin"):
        raise RuntimeError("Safety stop: gui-database requires the test credential target.")


class RollbackConnection:
    """Suppress repository commits so the complete scenario can be rolled back."""
    def __init__(self, connection): self.connection = connection
    def cursor(self, *args, **kwargs): return self.connection.cursor(*args, **kwargs)
    def commit(self): return None
    def rollback(self): return self.connection.rollback()


class AllowProjects:
    """Permit only the project operations exercised by this bounded profile."""
    def require(self, permission, operation=None):
        if permission not in {"projects.view", "projects.manage"}:
            raise PermissionError(operation or permission)


def main():
    """Create through the GUI service, read back, and roll back one fictional row."""
    if os.environ.get(OPT_IN) != "1":
        print(f"SKIP: set {OPT_IN}=1 to run the guarded gui-database profile.")
        return 0
    config = load_config()
    try:
        settings = resolve_database(
            {"server": None, "database": None, "user": None, "password": None,
             "test_mode": True}, config,
        )
    except KeyError:
        result = {
            "profile": "gui-database", "status": "skipped",
            "reason": "The configured LocalTestAdmin credential is unavailable.",
        }
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(result, indent=2))
        return 0
    validate_target(settings)
    connection = mariadb.connect(
        host=settings["server"], port=settings["port"], database=settings["database"],
        user=settings["user"], password=settings["password"], autocommit=False,
    )
    app = wx.GetApp() or wx.App(False)
    original_message = wx.MessageBox
    result = {"profile": "gui-database", "target": "localhost/ChurchDBTest",
              "fictional": True, "persistence": "rollback-only"}
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT ID FROM tblChurch ORDER BY ID LIMIT 1")
        church = cursor.fetchone()
        cursor.execute("SELECT ID FROM tblUser WHERE Active=1 ORDER BY ID LIMIT 1")
        user = cursor.fetchone()
        cursor.close()
        if not church or not user:
            raise RuntimeError("ChurchDBTest needs one church and active test user.")
        repository = MariaDBProjectRepository(RollbackConnection(connection))
        service = ProjectService(repository, SimpleNamespace(user_id=user[0]), AllowProjects())
        dialog = ProjectEditorDialog(None, service, church[0])
        try:
            dialog.name.SetValue("GUI Database Fictional Rollback Project")
            wx.MessageBox = lambda *args, **kwargs: wx.OK
            dialog.on_save(None)
            saved = service.project(dialog.project_id)
            if saved["name"] != "GUI Database Fictional Rollback Project":
                raise AssertionError("The project service readback did not match the GUI value.")
            result.update({"status": "passed", "readback_verified": True})
        finally:
            wx.MessageBox = original_message
            dialog.Destroy()
            connection.rollback()
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(result, indent=2))
        return 0
    finally:
        wx.MessageBox = original_message
        connection.rollback()
        connection.close()


if __name__ == "__main__":
    raise SystemExit(main())
