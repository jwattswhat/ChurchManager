"""Confidential contributor and dated-envelope maintenance for ChurchManager."""

from datetime import date

import wx
import wx.adv

from bulletin_orders import portable_connection
from giving.annual_envelopes import show_annual_envelope_assignment
from giving.validation import (
    GivingValidationError,
    validate_contributor_links,
    validate_envelope_assignment,
)


def _date_value(control):
    value = control.GetValue()
    return date(value.GetYear(), value.GetMonth() + 1, value.GetDay())


class ContributorRepository:
    """Store contributor identities and envelope assignments transactionally."""

    def __init__(self, connection):
        self.connection = portable_connection(connection)

    def all(self, sql, values=()):
        cursor = self.connection.cursor()
        try:
            cursor.execute(sql, values)
            return cursor.fetchall()
        finally:
            cursor.close()

    def church_id(self):
        row = self.all("SELECT ID FROM tblChurch ORDER BY ID LIMIT 1")
        if not row:
            raise GivingValidationError("Church information must be created first.")
        return row[0][0]

    def contributors(self):
        return self.all(
            "SELECT ID,DisplayName,ContributorType,IsActive FROM tblContributionContributor "
            "WHERE ChurchID=? ORDER BY IsActive DESC,DisplayName,ID", (self.church_id(),)
        )

    def contributor(self, contributor_id):
        rows = self.all(
            "SELECT ID,ContributorType,PersonID,FamilyID,DisplayName,"
            "COALESCE(StatementName,''),COALESCE(Address,''),COALESCE(Address2,''),"
            "COALESCE(City,''),COALESCE(State,''),COALESCE(PostalCode,''),"
            "COALESCE(Email,''),IsActive,StatementEnabled,COALESCE(Note,'') "
            "FROM tblContributionContributor WHERE ID=? AND ChurchID=?",
            (contributor_id, self.church_id()),
        )
        return rows[0] if rows else None

    def people(self):
        return self.all(
            "SELECT ID,TRIM(CONCAT_WS(' ',NULLIF(Title,''),FirstName,MiddleName,LastName)) "
            "FROM tblPerson ORDER BY LastName,FirstName,ID"
        )

    def families(self):
        return self.all("SELECT ID,FamilyName FROM tblFamily ORDER BY FamilyName,ID")

    def link_details(self, contributor_type, record_id):
        """Return statement defaults for a selected directory record."""
        if contributor_type == "PERSON":
            rows = self.all(
                "SELECT TRIM(CONCAT_WS(' ',NULLIF(Title,''),FirstName,MiddleName,LastName)),FamilyID "
                "FROM tblPerson WHERE ID=?", (record_id,),
            )
            if not rows:
                return None
            display_name, family_id = rows[0]
            address = self._address("tblPersonAddress", "PersonID", record_id)
            email = self._email("tblPersonContact", "PersonID", record_id)
            if not address and family_id:
                address = self._address("tblFamilyAddress", "FamilyID", family_id)
            if not email and family_id:
                email = self._email("tblFamilyContact", "FamilyID", family_id)
        else:
            rows = self.all("SELECT FamilyName FROM tblFamily WHERE ID=?", (record_id,))
            if not rows:
                return None
            display_name = rows[0][0]
            address = self._address("tblFamilyAddress", "FamilyID", record_id)
            email = self._email("tblFamilyContact", "FamilyID", record_id)
        fields = address[0] if address else (None, None, None, None, None)
        return (display_name,) + tuple(value or "" for value in fields) + (
            (email[0][0] or "") if email else "",
        )

    def _address(self, table, owner_field, owner_id):
        return self.all(
            f"SELECT Address,Address2,City,State,Zip FROM {table} "
            f"WHERE {owner_field}=? AND (StartDate IS NULL OR StartDate<=CURRENT_DATE) "
            "AND (EndDate IS NULL OR EndDate>=CURRENT_DATE) "
            "ORDER BY COALESCE(StartDate,'1000-01-01') DESC,ID DESC LIMIT 1",
            (owner_id,),
        )

    def _email(self, table, owner_field, owner_id):
        return self.all(
            f"SELECT Contact FROM {table} WHERE {owner_field}=? "
            "AND LOWER(Type) LIKE '%mail%' ORDER BY ID LIMIT 1", (owner_id,),
        )

    def envelopes(self, contributor_id):
        return self.all(
            "SELECT ID,EnvelopeNumber,EffectiveFrom,EffectiveThrough,COALESCE(Note,'') "
            "FROM tblContributionEnvelopeAssignment WHERE ContributorID=? "
            "ORDER BY EffectiveFrom DESC,EnvelopeNumber", (contributor_id,)
        )

    def save_contributor(self, contributor_id, values):
        contributor_type, person_id, family_id = values[:3]
        validate_contributor_links(contributor_type, person_id, family_id)
        cursor = self.connection.cursor()
        try:
            if contributor_id is None:
                cursor.execute(
                    "INSERT INTO tblContributionContributor "
                    "(ChurchID,ContributorType,PersonID,FamilyID,DisplayName,StatementName,"
                    "Address,Address2,City,State,PostalCode,Email,IsActive,StatementEnabled,Note) "
                    "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (self.church_id(),) + values,
                )
                contributor_id = cursor.lastrowid
            else:
                cursor.execute(
                    "UPDATE tblContributionContributor SET ContributorType=?,PersonID=?,FamilyID=?,"
                    "DisplayName=?,StatementName=?,Address=?,Address2=?,City=?,State=?,PostalCode=?,"
                    "Email=?,IsActive=?,StatementEnabled=?,Note=? WHERE ID=? AND ChurchID=?",
                    values + (contributor_id, self.church_id()),
                )
            self.connection.commit()
            return contributor_id
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def save_envelope(self, assignment_id, contributor_id, number, start, through, note):
        number = validate_envelope_assignment(number, start, through)
        if number.isdecimal():
            identity_sql = (
                "EnvelopeNumber REGEXP '^[0-9]+$' "
                "AND CAST(EnvelopeNumber AS UNSIGNED)=?"
            )
            identity_value = int(number)
        else:
            identity_sql = "EnvelopeNumber=?"
            identity_value = number
        overlap = self.all(
            "SELECT ID FROM tblContributionEnvelopeAssignment WHERE ChurchID=? AND "
            + identity_sql
            + " AND ID<>? AND EffectiveFrom<=COALESCE(?, '9999-12-31') "
              "AND COALESCE(EffectiveThrough,'9999-12-31')>=? LIMIT 1",
            (self.church_id(), identity_value, assignment_id or 0, through, start),
        )
        if overlap:
            raise GivingValidationError(
                "That envelope number is already assigned during part of this date range."
            )
        cursor = self.connection.cursor()
        try:
            if assignment_id is None:
                cursor.execute(
                    "INSERT INTO tblContributionEnvelopeAssignment "
                    "(ChurchID,ContributorID,EnvelopeNumber,EffectiveFrom,EffectiveThrough,Note) "
                    "VALUES (?,?,?,?,?,?)",
                    (self.church_id(), contributor_id, number, start, through, note or None),
                )
            else:
                cursor.execute(
                    "UPDATE tblContributionEnvelopeAssignment SET EnvelopeNumber=?,EffectiveFrom=?,"
                    "EffectiveThrough=?,Note=? WHERE ID=? AND ContributorID=?",
                    (number, start, through, note or None, assignment_id, contributor_id),
                )
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def delete_envelope(self, assignment_id, contributor_id):
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "DELETE FROM tblContributionEnvelopeAssignment WHERE ID=? AND ContributorID=?",
                (assignment_id, contributor_id),
            )
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()


class EnvelopeDialog(wx.Dialog):
    """Edit one time-bounded envelope assignment."""

    def __init__(self, parent, row=None):
        super().__init__(parent, title="Envelope Assignment", size=(470, 300))
        panel = wx.Panel(self)
        form = wx.FlexGridSizer(0, 2, 8, 10); form.AddGrowableCol(1, 1)
        self.number = wx.TextCtrl(panel)
        self.start = wx.adv.DatePickerCtrl(panel)
        self.has_end = wx.CheckBox(panel, label="Assignment has an ending date")
        self.through = wx.adv.DatePickerCtrl(panel)
        self.note = wx.TextCtrl(panel, style=wx.TE_MULTILINE)
        for label, control in (("Envelope number", self.number), ("Effective from", self.start),
                               ("", self.has_end), ("Effective through", self.through),
                               ("Note", self.note)):
            form.Add(wx.StaticText(panel, label=label), 0, wx.ALIGN_CENTER_VERTICAL)
            form.Add(control, 1, wx.EXPAND)
        self.has_end.Bind(wx.EVT_CHECKBOX, lambda _e: self.through.Enable(self.has_end.GetValue()))
        buttons = wx.StdDialogButtonSizer()
        ok = wx.Button(panel, wx.ID_OK); cancel = wx.Button(panel, wx.ID_CANCEL)
        buttons.AddButton(ok); buttons.AddButton(cancel); buttons.Realize()
        outer = wx.BoxSizer(wx.VERTICAL); outer.Add(form, 1, wx.EXPAND | wx.ALL, 12)
        outer.Add(buttons, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 12); panel.SetSizer(outer)
        self.assignment_id = row[0] if row else None
        if row:
            self.number.SetValue(str(row[1])); self.start.SetValue(wx.DateTime.FromDMY(row[2].day, row[2].month - 1, row[2].year))
            self.has_end.SetValue(row[3] is not None)
            if row[3]: self.through.SetValue(wx.DateTime.FromDMY(row[3].day, row[3].month - 1, row[3].year))
            self.note.SetValue(row[4] or "")
        self.through.Enable(self.has_end.GetValue())

    def values(self):
        return (self.number.GetValue(), _date_value(self.start),
                _date_value(self.through) if self.has_end.GetValue() else None,
                self.note.GetValue().strip())


class ContributorDialog(wx.Dialog):
    """Maintain confidential giving identities and their envelope history."""

    TYPES = (("Person", "PERSON"), ("Family", "FAMILY"), ("Outside contributor", "EXTERNAL"))

    def __init__(self, parent, connection, user_id=None):
        super().__init__(parent, title="Contributors and Envelopes", size=(1120, 720),
                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.repository = ContributorRepository(connection)
        self.connection = connection
        self.user_id = user_id
        self.rows = []; self.envelope_rows = []; self.current_id = None
        self.people = self.repository.people(); self.families = self.repository.families()
        panel = wx.Panel(self); outer = wx.BoxSizer(wx.VERTICAL)
        heading = wx.StaticText(panel, label="Giving Contributors")
        heading.SetFont(heading.GetFont().Bold().Larger())
        outer.Add(heading, 0, wx.LEFT | wx.TOP, 12)
        outer.Add(wx.StaticText(panel, label="Contributor identity is confidential. Envelope numbers may be reassigned only in non-overlapping date ranges."), 0, wx.LEFT | wx.TOP | wx.BOTTOM, 12)
        body = wx.BoxSizer(wx.HORIZONTAL)
        left = wx.BoxSizer(wx.VERTICAL)
        self.list = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        for i, (label, width) in enumerate((("Contributor", 255), ("Type", 90), ("Active", 65))): self.list.InsertColumn(i, label, width=width)
        self.list.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_select)
        left.Add(self.list, 1, wx.EXPAND)
        left_buttons = wx.BoxSizer(wx.HORIZONTAL)
        for label, handler in (("New", self.on_new), ("Save", self.on_save)):
            button = wx.Button(panel, label=label); button.Bind(wx.EVT_BUTTON, handler); left_buttons.Add(button, 0, wx.RIGHT, 6)
        left.Add(left_buttons, 0, wx.TOP, 8); body.Add(left, 0, wx.EXPAND | wx.RIGHT, 14)
        right = wx.BoxSizer(wx.VERTICAL); form = wx.FlexGridSizer(0, 2, 7, 10); form.AddGrowableCol(1, 1)
        self.kind = wx.Choice(panel, choices=[x[0] for x in self.TYPES]); self.kind.SetSelection(0)
        self.link = wx.Choice(panel); self.display = wx.TextCtrl(panel); self.statement = wx.TextCtrl(panel)
        self.address = wx.TextCtrl(panel); self.address2 = wx.TextCtrl(panel); self.city = wx.TextCtrl(panel)
        self.state = wx.TextCtrl(panel); self.postal = wx.TextCtrl(panel); self.email = wx.TextCtrl(panel)
        self.active = wx.CheckBox(panel, label="Active"); self.statements = wx.CheckBox(panel, label="Include on statements")
        self.note = wx.TextCtrl(panel, style=wx.TE_MULTILINE)
        for label, control in (("Contributor type", self.kind), ("Linked record", self.link),
                               ("Display name", self.display), ("Statement name", self.statement),
                               ("Address", self.address), ("Address 2", self.address2), ("City", self.city),
                               ("State", self.state), ("Postal code", self.postal), ("Email", self.email),
                               ("", self.active), ("", self.statements), ("Note", self.note)):
            form.Add(wx.StaticText(panel, label=label), 0, wx.ALIGN_CENTER_VERTICAL); form.Add(control, 1, wx.EXPAND)
        self.kind.Bind(wx.EVT_CHOICE, self.on_kind); self.link.Bind(wx.EVT_CHOICE, self.on_link)
        right.Add(form, 0, wx.EXPAND)
        right.Add(wx.StaticText(panel, label="Envelope history"), 0, wx.TOP | wx.BOTTOM, 10)
        self.envelopes = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        for i, (label, width) in enumerate((("Envelope", 100), ("From", 105), ("Through", 105), ("Note", 260))): self.envelopes.InsertColumn(i, label, width=width)
        self.envelopes.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_edit_envelope); right.Add(self.envelopes, 1, wx.EXPAND)
        env_buttons = wx.BoxSizer(wx.HORIZONTAL)
        for label, handler in (("Assign Envelope", self.on_add_envelope), ("Edit", self.on_edit_envelope), ("Delete", self.on_delete_envelope),
                               ("Annual Assignment...", self.on_annual_assignment)):
            button = wx.Button(panel, label=label); button.Bind(wx.EVT_BUTTON, handler); env_buttons.Add(button, 0, wx.RIGHT, 6)
        right.Add(env_buttons, 0, wx.TOP, 8); body.Add(right, 1, wx.EXPAND)
        outer.Add(body, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 12)
        close = wx.Button(panel, wx.ID_CLOSE); close.Bind(wx.EVT_BUTTON, lambda _e: self.EndModal(wx.ID_CLOSE))
        outer.Add(close, 0, wx.ALIGN_RIGHT | wx.ALL, 12); panel.SetSizer(outer)
        self.on_new(); self.refresh()

    def on_kind(self, _event=None):
        code = self.TYPES[self.kind.GetSelection()][1]
        rows = self.people if code == "PERSON" else self.families if code == "FAMILY" else []
        self.link.Set([row[1] for row in rows]); self.link.Enable(bool(rows))
        self.link.SetSelection(wx.NOT_FOUND)

    def on_link(self, _event=None):
        if not self.link.IsEnabled() or self.link.GetSelection() == wx.NOT_FOUND:
            return
        code = self.TYPES[self.kind.GetSelection()][1]
        source = self.people if code == "PERSON" else self.families
        details = self.repository.link_details(code, source[self.link.GetSelection()][0])
        if not details:
            return
        display, address, address2, city, state, postal, email = details
        self.display.SetValue(display); self.statement.SetValue(display)
        for control, value in zip(
            (self.address,self.address2,self.city,self.state,self.postal,self.email),
            (address,address2,city,state,postal,email),
        ):
            control.SetValue(value)

    def on_new(self, _event=None):
        self.current_id = None
        for control in (self.display,self.statement,self.address,self.address2,self.city,self.state,self.postal,self.email,self.note): control.SetValue("")
        self.kind.SetSelection(0); self.active.SetValue(True); self.statements.SetValue(True); self.on_kind(); self.refresh_envelopes()

    def refresh(self):
        self.rows = self.repository.contributors(); self.list.DeleteAllItems()
        for index, row in enumerate(self.rows):
            self.list.InsertItem(index, row[1]); self.list.SetItem(index, 1, row[2].title()); self.list.SetItem(index, 2, "Yes" if row[3] else "No")

    def on_select(self, _event=None):
        selected = self.list.GetFirstSelected()
        if selected < 0: return
        row = self.repository.contributor(self.rows[selected][0]); self.current_id = row[0]
        code = row[1]; self.kind.SetSelection([x[1] for x in self.TYPES].index(code)); self.on_kind()
        link_id = row[2] if code == "PERSON" else row[3]
        source = self.people if code == "PERSON" else self.families
        for index, item in enumerate(source):
            if item[0] == link_id: self.link.SetSelection(index); break
        for control, value in zip((self.display,self.statement,self.address,self.address2,self.city,self.state,self.postal,self.email), row[4:12]): control.SetValue(value or "")
        self.active.SetValue(bool(row[12])); self.statements.SetValue(bool(row[13])); self.note.SetValue(row[14] or ""); self.refresh_envelopes()

    def values(self):
        code = self.TYPES[self.kind.GetSelection()][1]; selection = self.link.GetSelection()
        link_id = None
        if selection != wx.NOT_FOUND:
            source = self.people if code == "PERSON" else self.families if code == "FAMILY" else []
            if source: link_id = source[selection][0]
        return (code, link_id if code == "PERSON" else None, link_id if code == "FAMILY" else None,
                self.display.GetValue().strip(), self.statement.GetValue().strip() or None,
                self.address.GetValue().strip() or None, self.address2.GetValue().strip() or None,
                self.city.GetValue().strip() or None, self.state.GetValue().strip() or None,
                self.postal.GetValue().strip() or None, self.email.GetValue().strip() or None,
                int(self.active.GetValue()), int(self.statements.GetValue()), self.note.GetValue().strip() or None)

    def on_save(self, _event=None):
        try:
            values = self.values()
            if not values[3]: raise GivingValidationError("Display name is required.")
            self.current_id = self.repository.save_contributor(self.current_id, values); self.refresh()
        except Exception as error: wx.MessageBox(str(error), "Unable to Save Contributor", wx.OK | wx.ICON_ERROR, self)

    def refresh_envelopes(self):
        self.envelope_rows = self.repository.envelopes(self.current_id) if self.current_id else []
        self.envelopes.DeleteAllItems()
        for index, row in enumerate(self.envelope_rows):
            self.envelopes.InsertItem(index, row[1]); self.envelopes.SetItem(index, 1, str(row[2])); self.envelopes.SetItem(index, 2, str(row[3] or "Open")); self.envelopes.SetItem(index, 3, row[4])

    def on_add_envelope(self, _event=None):
        if not self.current_id:
            wx.MessageBox("Save the contributor before assigning an envelope.", "Envelope Assignment", wx.OK | wx.ICON_INFORMATION, self); return
        self._edit_envelope(None)

    def on_edit_envelope(self, _event=None):
        selected = self.envelopes.GetFirstSelected()
        if selected >= 0: self._edit_envelope(self.envelope_rows[selected])

    def _edit_envelope(self, row):
        dialog = EnvelopeDialog(self, row)
        try:
            if dialog.ShowModal() == wx.ID_OK:
                self.repository.save_envelope(dialog.assignment_id, self.current_id, *dialog.values()); self.refresh_envelopes()
        except Exception as error: wx.MessageBox(str(error), "Unable to Save Envelope", wx.OK | wx.ICON_ERROR, self)
        finally: dialog.Destroy()

    def on_delete_envelope(self, _event=None):
        selected = self.envelopes.GetFirstSelected()
        if selected < 0: return
        if wx.MessageBox("Delete this envelope assignment?", "Delete Envelope", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING, self) == wx.YES:
            self.repository.delete_envelope(self.envelope_rows[selected][0], self.current_id); self.refresh_envelopes()

    def on_annual_assignment(self, _event=None):
        """Create a previewed annual assignment sequence for active contributors."""
        if show_annual_envelope_assignment(self, self.connection, self.user_id) == wx.ID_OK:
            self.refresh_envelopes()


def show_contributors(parent, connection, session=None):
    """Open confidential contributor and envelope maintenance."""
    dialog = ContributorDialog(parent, connection, getattr(session, "user_id", None))
    try:
        dialog.ShowModal()
    finally:
        dialog.Destroy()
