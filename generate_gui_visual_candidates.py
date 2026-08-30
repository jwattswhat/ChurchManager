"""Capture unapproved GUI visual candidates using fictional structural fixtures."""

from __future__ import annotations

import argparse
import json
import locale
from pathlib import Path
import time
from types import SimpleNamespace

import wx

from JSForm.gui_testing import GUITestError, capture_client, drain_events
from asset_dialog import AssetEditorDialog
from login_dialog import LoginDialog
from participant_notification_dialog import ParticipantNotificationDialog
from project_dialog import ProjectEditorDialog


class NotificationService:
    """Supply deterministic fictional notification data without external effects."""
    def __init__(self):
        self.repository = SimpleNamespace(services=lambda: [(7, "Sunday 10:30 AM")])

    def prepare(self, _service_id, kind):
        recipient = SimpleNamespace(
            name="Fictional Volunteer", positions=("Reader",),
            email="volunteer@example.invalid", status="Ready",
        )
        return SimpleNamespace(subject=f"{kind}: Sunday", body="Fictional test message",
                               recipients=(recipient,), attachment=None)


class ProjectServiceFixture:
    """Supply a blank project editor without database access."""
    def project(self, _project_id): return None
    def steps(self, _project_id): return []
    def owners(self, _church_id, _kind): return []


class AssetServiceFixture:
    """Supply a blank asset editor without database access."""
    def choices(self, _church_id):
        return {"categories": [{"id": 1, "name": "Office"}],
                "locations": [], "people": [], "groups": []}
    def activities(self, _asset_id): return []


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / ".gui-test-artifacts" / "visual-candidates"
CANONICAL_PPI = (96, 96)
WINDOWS = (
    ("login", lambda: LoginDialog(None, "Reformation Lutheran Church"), (520, 430)),
    ("participant-notifications", lambda: ParticipantNotificationDialog(
        None, NotificationService(), object()), (1050, 720)),
    ("project-plan", lambda: ProjectEditorDialog(
        None, ProjectServiceFixture(), 1), (970, 740)),
    ("asset-editor", lambda: AssetEditorDialog(
        None, AssetServiceFixture(), 1), (920, 720)),
)


def apply_review_size(window, requested):
    """Grow a candidate to the review size without shrinking its fitted layout."""
    fitted = window.GetSize()
    window.SetSize((max(requested[0], fitted.width),
                    max(requested[1], fitted.height)))


def display_profile():
    """Return the actual display facts required to interpret visual evidence."""
    app = wx.GetApp() or wx.App(False)
    dc = wx.ScreenDC()
    return {
        "profile": "gui-visual",
        "platform": wx.PlatformInfo[0],
        "ppi": list(dc.GetPPI()),
        "display_pixels": list(wx.GetDisplaySize()),
        "locale": list(locale.getlocale()),
        "timezone": list(time.tzname),
        "theme": "churchmanager",
        "baseline_status": "candidate-unapproved",
    }


def review_interactively():
    """Present each fictional-data candidate for human review without approving it."""
    app = wx.GetApp() or wx.App(False)
    reviewed = []
    for name, factory, size in WINDOWS:
        window = factory()
        try:
            apply_review_size(window, size)
            window.CentreOnScreen()
            window.ShowModal()
            reviewed.append(name)
        finally:
            window.Destroy()
            drain_events()
    result = {
        "profile": "gui-visual-manual-review",
        "reviewed": reviewed,
        "baseline_status": "awaiting-human-decision",
    }
    print(json.dumps(result, indent=2))
    return 0


def main(review=False):
    """Capture candidates, or present them sequentially for human inspection."""
    if review:
        return review_interactively()
    app = wx.GetApp() or wx.App(False)
    profile = display_profile()
    if tuple(profile["ppi"]) != CANONICAL_PPI:
        raise RuntimeError(
            f"Visual profile unavailable: expected {CANONICAL_PPI}, got {profile['ppi']}."
        )
    OUTPUT.mkdir(parents=True, exist_ok=True)
    captures = []
    try:
        for name, factory, size in WINDOWS:
            window = factory()
            try:
                apply_review_size(window, size)
                window.CentreOnScreen()
                window.Show()
                drain_events()
                path = capture_client(window, OUTPUT / f"{name}.actual.png")
                captures.append(str(path.relative_to(ROOT)))
            finally:
                window.Destroy()
                drain_events()
    except GUITestError as error:
        profile["baseline_status"] = "environment-incompatible"
        profile["reason"] = str(error)
    profile["captures"] = captures
    (OUTPUT / "profile.json").write_text(
        json.dumps(profile, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(profile, indent=2))
    return 0 if profile["baseline_status"] == "candidate-unapproved" else 2


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--review", action="store_true",
        help="show each fictional-data screen for manual visual review",
    )
    raise SystemExit(main(review=parser.parse_args().review))
