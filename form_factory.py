"""Consistent creation of ChurchManager forms."""

import wx

from liturgical_colors import liturgical_color_hex


class ChurchManagerFormFactory:
    def __init__(self, form_class, connection, default_parent=None,
                 authorization_policy=None, audit_hook=None):
        self.form_class = form_class
        self.connection = connection
        self.default_parent = default_parent
        self.authorization_policy = authorization_policy
        self.audit_hook = audit_hook

    def create(self, form_name, controls=None, parent=None, form_description=None):
        parent = self.default_parent if parent is None else parent
        keyword_arguments = {}
        if self.authorization_policy is not None:
            keyword_arguments["authorization_policy"] = self.authorization_policy
        if self.audit_hook is not None:
            keyword_arguments["audit_hook"] = self.audit_hook
        if form_description is not None:
            keyword_arguments["frmdescription"] = form_description
        if controls is None:
            form = self.form_class(parent, self.connection, form_name, **keyword_arguments)
        else:
            form = self.form_class(
                parent, self.connection, form_name, controls, **keyword_arguments
            )
        if form_name == "frmPropers":
            self._add_proper_color_swatch(form)
        return form

    @staticmethod
    def _add_proper_color_swatch(form):
        """Add the ChurchManager-specific liturgical color preview to Propers."""
        color_field = form.CONTROLID.get("Color")
        if color_field is None:
            return
        position = color_field.GetPosition()
        size = color_field.GetSize()
        swatch = wx.Panel(
            form.FORM,
            pos=(position.x + size.width + 8, position.y + max(0, (size.height - 20) // 2)),
            size=(28, 20),
            style=wx.BORDER_SIMPLE,
        )
        swatch.SetToolTip("Preview of the selected liturgical color.")

        def refresh(_event=None):
            color = liturgical_color_hex(color_field.GetValue())
            swatch.Show(bool(color))
            if color:
                swatch.SetBackgroundColour(wx.Colour(color))
                swatch.Refresh()

        color_field.Bind(wx.EVT_TEXT, refresh)
        color_field.Bind(wx.EVT_COMBOBOX, refresh)
        refresh()
        form.LITURGICAL_COLOR_SWATCH = swatch

    def open(self, form_name, controls=None, parent=None, form_description=None):
        form = self.create(form_name, controls, parent, form_description)
        form.show()
        return form
