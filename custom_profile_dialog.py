"""ChurchManager dialogs for authorized Person and Family custom information."""

from __future__ import annotations

import wx

from JSForm.dynamic_fields import DynamicFieldError, DynamicFieldHost

from custom_profile_fields import CustomProfileFieldService, CustomProfileValidationError
from custom_profile_repository import MariaDBCustomProfileRepository


class CustomProfileDialog(wx.Dialog):
    """Edit the application-authorized dynamic fields for one saved profile."""

    def __init__(self, parent, service, church_id, entity_type, profile_id, title):
        super().__init__(parent, title=f"Additional Information - {title}", size=(650, 560))
        self.service = service
        self.church_id = church_id
        self.entity_type = entity_type
        self.profile_id = profile_id
        panel = wx.Panel(self)
        outer = wx.BoxSizer(wx.VERTICAL)
        note = wx.StaticText(panel, label="Additional church-defined information for this profile.")
        note.SetForegroundColour(wx.Colour(0, 82, 170))
        outer.Add(note, 0, wx.ALL, 12)
        descriptors, values = service.profile(church_id, entity_type, profile_id)
        self.host = DynamicFieldHost(panel, descriptors, values)
        if descriptors:
            outer.Add(self.host, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 12)
        else:
            empty = wx.StaticText(panel, label="No custom fields are active for this profile type.")
            outer.Add(empty, 1, wx.EXPAND | wx.ALL, 12)
        buttons = wx.StdDialogButtonSizer()
        save = wx.Button(panel, wx.ID_SAVE, "Save")
        close = wx.Button(panel, wx.ID_CANCEL, "Close")
        buttons.AddButton(save); buttons.AddButton(close); buttons.Realize()
        save.Enable(bool(descriptors))
        save.Bind(wx.EVT_BUTTON, self.on_save)
        outer.Add(buttons, 0, wx.ALIGN_RIGHT | wx.ALL, 12)
        panel.SetSizer(outer)
        self.CentreOnParent()

    def on_save(self, _event):
        try:
            changes = {item.key: item.value for item in self.host.changes()}
            if changes:
                self.service.save_profile_values(
                    self.church_id, self.entity_type, self.profile_id, changes,
                )
        except (CustomProfileValidationError, DynamicFieldError, ValueError) as error:
            wx.MessageBox(str(error), "Unable to Save Additional Information", wx.OK | wx.ICON_ERROR, self)
            return
        self.EndModal(wx.ID_OK)


def show_custom_profile(parent, connection, session, authorization, church_id, entity_type, profile_id, title):
    """Open the custom-profile editor using the current authenticated session."""
    service = CustomProfileFieldService(
        MariaDBCustomProfileRepository(connection), session, authorization,
    )
    dialog = CustomProfileDialog(
        parent, service, church_id, entity_type, profile_id, title,
    )
    try:
        return dialog.ShowModal()
    finally:
        dialog.Destroy()
