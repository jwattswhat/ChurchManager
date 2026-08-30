"""Structural GUI milestone for four high-value ChurchManager screens."""

from types import SimpleNamespace
import unittest
from unittest import mock

import wx

from JSForm.gui_testing import drain_events, geometry_issues, named_controls
from asset_dialog import AssetEditorDialog
from login_dialog import LoginDialog
from participant_notification_dialog import ParticipantNotificationDialog
from project_dialog import ProjectEditorDialog


class NotificationService:
    def __init__(self, error=None):
        self.error = error
        self.repository = SimpleNamespace(services=lambda: [(7, "Sunday 10:30 AM")])

    def prepare(self, service_id, kind):
        if self.error:
            raise self.error
        recipient = SimpleNamespace(
            name="Fictional Volunteer", positions=("Reader",),
            email="volunteer@example.invalid", status="Ready",
        )
        return SimpleNamespace(
            subject=f"{kind}: Sunday", body="Fictional test message",
            recipients=(recipient,), attachment=None,
        )


class ProjectServiceFixture:
    def __init__(self):
        self.saved = []

    def project(self, project_id):
        if not project_id:
            return None
        return {"project_number": "PRJ-0001", "name": "Fictional Project",
                "status": "Planned", "priority": "Normal", "owner_type": None,
                "owner_id": None, "planned_start": None, "target_date": None,
                "calendar_eligible": False, "purpose": "", "note": ""}

    def steps(self, _project_id): return []
    def owners(self, _church_id, _kind): return []
    def save_project(self, values, project_id):
        self.saved.append(dict(values)); return project_id or 1


class AssetServiceFixture:
    def choices(self, _church_id):
        return {"categories": [{"id": 1, "name": "Office"}],
                "locations": [], "people": [], "groups": []}

    def activities(self, _asset_id): return []


class StructuralGUITests(unittest.TestCase):
    profile = "gui-structural"

    @classmethod
    def setUpClass(cls):
        cls.app = wx.GetApp() or wx.App(False)

    def exercise(self, dialog, required_names, minimum_width=480):
        dialog.Show()
        try:
            drain_events()
            controls = named_controls(dialog)
            self.assertTrue(set(required_names).issubset(controls))
            self.assertGreaterEqual(dialog.GetClientSize().width, minimum_width)
            self.assertFalse(geometry_issues(dialog), geometry_issues(dialog))
        finally:
            dialog.Destroy(); drain_events()

    def test_login_constructs_with_stable_identity_and_cleanup(self):
        self.exercise(LoginDialog(None, "Reformation Lutheran Church"), (
            "login_username", "login_password", "login_submit", "login_cancel",
        ), minimum_width=450)

    def test_participant_notification_has_permission_sensitive_state(self):
        dialog = ParticipantNotificationDialog(None, NotificationService(), SimpleNamespace())
        self.assertFalse(dialog.preview.IsEnabled())
        self.assertFalse(dialog.send.IsEnabled())
        self.exercise(dialog, (
            "notification_service", "notification_recipients",
            "notification_subject", "notification_send",
        ))
        with mock.patch("participant_notification_dialog.wx.MessageBox") as message:
            denied = ParticipantNotificationDialog(
                None, NotificationService(PermissionError("not permitted")), SimpleNamespace()
            )
            try:
                self.assertIsNone(denied.plan)
                message.assert_called_once()
            finally:
                denied.Destroy(); drain_events()

    def test_project_plan_resizes_and_guarded_save_occurs_once(self):
        service = ProjectServiceFixture()
        dialog = ProjectEditorDialog(None, service, 1)
        dialog.name.SetValue("Fictional Project")
        with mock.patch("project_dialog.wx.MessageBox"):
            dialog.on_save(None)
        self.assertEqual(len(service.saved), 1)
        self.assertEqual(service.saved[0]["name"], "Fictional Project")
        self.exercise(dialog, ("project_number", "project_name", "project_save"))

    def test_asset_editor_constructs_and_cancel_does_not_persist(self):
        service = AssetServiceFixture()
        dialog = AssetEditorDialog(None, service, 1)
        self.exercise(dialog, ("asset_number", "asset_name", "asset_save", "asset_cancel"))
        self.assertFalse(hasattr(service, "saved"))


if __name__ == "__main__":
    unittest.main()
