"""Protected ChurchManager user and role administration."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

import wx
import JSForm

from authentication import MariaDBUserRepository, PasswordService
from participant_notifications import configured_mail_service


_PERSON_UNCHANGED = object()


def _format_phone_control(event):
    control = event.GetEventObject()
    control.ChangeValue(JSForm.phone_display(control.GetValue()))
    event.Skip()


@dataclass(frozen=True)
class UserSummary:
    id: int
    username: str
    display_name: str
    email: str
    phone: str
    person_id: int | None
    person_name: str
    active: bool
    is_master: bool
    failed_login_count: int
    locked_until: object
    roles: tuple[str, ...]


@dataclass(frozen=True)
class SecurityAuditSummary:
    occurred_at: object
    username: str
    action: str
    entity_type: str
    entity_id: str
    reason: str


@dataclass(frozen=True)
class PersonChoice:
    id: int
    display: str
    first_name: str


class UserAdministrationService:
    def __init__(self, connection, acting_user_id, passwords=None):
        self.connection = connection
        self.acting_user_id = acting_user_id
        self.passwords = passwords or PasswordService()
        self.repository = MariaDBUserRepository(connection)

    def _cursor(self):
        return self.connection.cursor()

    @staticmethod
    def ensure_can_disable(is_master, active_master_count):
        if is_master and active_master_count <= 1:
            raise ValueError("The last active master administrator cannot be disabled.")

    def list_users(self):
        cursor = self._cursor()
        try:
            self.repository._execute(
                cursor,
                "SELECT u.ID, u.Username, u.DisplayName, COALESCE(u.Email, ''), "
                "COALESCE(u.Phone, ''), u.PersonID, "
                "COALESCE(NULLIF(TRIM(CONCAT(COALESCE(p.LastName,''), "
                "CASE WHEN COALESCE(p.LastName,'')<>'' AND COALESCE(p.FirstName,'')<>'' "
                "THEN ', ' ELSE '' END, COALESCE(p.FirstName,''))),''), ''), u.Active, "
                "u.MasterAdministrator, u.FailedLoginCount, u.LockedUntil, "
                "GROUP_CONCAT(r.Name ORDER BY r.Name SEPARATOR ', ') "
                "FROM tblUser u LEFT JOIN tblUserRole ur ON ur.UserID=u.ID "
                "LEFT JOIN tblRole r ON r.ID=ur.RoleID "
                "LEFT JOIN tblPerson p ON p.ID=u.PersonID "
                "GROUP BY u.ID, u.Username, u.DisplayName, u.Email, u.Phone, u.PersonID, "
                "p.LastName, p.FirstName, u.Active, "
                "u.MasterAdministrator, u.FailedLoginCount, u.LockedUntil "
                "ORDER BY u.DisplayName, u.Username",
            )
            rows = cursor.fetchall()
        finally:
            cursor.close()
        return [
            UserSummary(
                row[0], row[1], row[2], row[3], row[4], row[5], row[6],
                bool(row[7]), bool(row[8]), row[9], row[10],
                tuple(filter(None, (row[11] or "").split(", "))),
            )
            for row in rows
        ]

    def list_available_people(self, user_id=None):
        """Return people not linked to another application user."""
        cursor = self._cursor()
        try:
            self.repository._execute(
                cursor,
                "SELECT p.ID,CONCAT(TRIM(CONCAT(COALESCE(p.LastName,''), "
                "CASE WHEN COALESCE(p.LastName,'')<>'' AND COALESCE(p.FirstName,'')<>'' "
                "THEN ', ' ELSE '' END,COALESCE(p.FirstName,''))), "
                "CASE WHEN COALESCE(c.Church,'')<>'' THEN CONCAT(' - ',c.Church) ELSE '' END), "
                "COALESCE(p.FirstName,'') "
                "FROM tblPerson p LEFT JOIN tblChurch c ON c.ID=p.ChurchID "
                "LEFT JOIN tblUser u ON u.PersonID=p.ID "
                "WHERE u.ID IS NULL OR u.ID=? "
                "ORDER BY p.LastName,p.FirstName,p.ID",
                (user_id,),
            )
            return [PersonChoice(row[0], row[1], row[2]) for row in cursor.fetchall()]
        finally:
            cursor.close()

    def list_assignable_roles(self):
        cursor = self._cursor()
        try:
            self.repository._execute(
                cursor,
                "SELECT ID, Name FROM tblRole "
                "WHERE Active=1 AND Name <> 'Master Administrator' ORDER BY Name",
            )
            return cursor.fetchall()
        finally:
            cursor.close()

    def role_ids_for(self, user_id):
        cursor = self._cursor()
        try:
            self.repository._execute(
                cursor,
                "SELECT RoleID FROM tblUserRole WHERE UserID=?",
                (user_id,),
            )
            return {row[0] for row in cursor.fetchall()}
        finally:
            cursor.close()

    def list_editable_roles(self):
        cursor = self._cursor()
        try:
            self.repository._execute(
                cursor,
                "SELECT ID, Name, Description FROM tblRole "
                "WHERE Active=1 AND Name <> 'Master Administrator' ORDER BY Name",
            )
            return cursor.fetchall()
        finally:
            cursor.close()

    def list_permissions(self):
        cursor = self._cursor()
        try:
            self.repository._execute(
                cursor,
                "SELECT ID, Name, Description, IsSensitive FROM tblPermission "
                "WHERE Active=1 ORDER BY Name",
            )
            return cursor.fetchall()
        finally:
            cursor.close()

    def permission_ids_for_role(self, role_id):
        cursor = self._cursor()
        try:
            self.repository._execute(
                cursor, "SELECT PermissionID FROM tblRolePermission WHERE RoleID=?",
                (role_id,),
            )
            return {row[0] for row in cursor.fetchall()}
        finally:
            cursor.close()

    def set_role_permissions(self, role_id, permission_ids):
        cursor = self._cursor()
        try:
            self.repository._execute(
                cursor, "SELECT Name FROM tblRole WHERE ID=? AND Active=1", (role_id,)
            )
            row = cursor.fetchone()
            if not row:
                raise ValueError("The selected role no longer exists.")
            if row[0] == "Master Administrator":
                raise ValueError("Master Administrator permissions are inherent and cannot be edited.")
            before = sorted(self.permission_ids_for_role(role_id))
            requested = sorted(set(permission_ids))
            self.repository._execute(
                cursor, "DELETE FROM tblRolePermission WHERE RoleID=?", (role_id,)
            )
            for permission_id in requested:
                self.repository._execute(
                    cursor,
                    "INSERT INTO tblRolePermission "
                    "(RoleID, PermissionID, AssignedByUserID) "
                    "SELECT ?, ID, ? FROM tblPermission WHERE ID=? AND Active=1",
                    (role_id, self.acting_user_id, permission_id),
                )
            self.repository._execute(
                cursor,
                "INSERT INTO tblSecurityAuditEvent "
                "(UserID, Action, EntityType, EntityID, BeforeJSON, AfterJSON) "
                "VALUES (?, 'ROLE_PERMISSIONS_CHANGED', 'Role', ?, ?, ?)",
                (
                    self.acting_user_id, str(role_id), json.dumps(before),
                    json.dumps(requested),
                ),
            )
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def list_security_audit(self, limit=500):
        limit = max(1, min(int(limit), 1000))
        cursor = self._cursor()
        try:
            self.repository._execute(
                cursor,
                "SELECT a.OccurredAt, COALESCE(u.Username, '[system]'), a.Action, "
                "COALESCE(a.EntityType, ''), COALESCE(a.EntityID, ''), "
                "COALESCE(a.Reason, '') "
                "FROM tblSecurityAuditEvent a "
                "LEFT JOIN tblUser u ON u.ID=a.UserID "
                "ORDER BY a.OccurredAt DESC, a.ID DESC LIMIT {}".format(limit),
            )
            return [SecurityAuditSummary(*row) for row in cursor.fetchall()]
        finally:
            cursor.close()

    @staticmethod
    def normalize_contact(display_name, email=None, phone=None):
        display_name = " ".join(str(display_name or "").split())
        email = str(email or "").strip() or None
        phone = JSForm.phone_storage(phone)
        if not display_name:
            raise ValueError("Display name is required.")
        if len(display_name) > 255:
            raise ValueError("Display name cannot exceed 255 characters.")
        if email:
            if len(email) > 254:
                raise ValueError("Email address cannot exceed 254 characters.")
            local, separator, domain = email.partition("@")
            if not separator or not local or not domain or "@" in domain or any(c.isspace() for c in email):
                raise ValueError("Enter a valid email address, such as name@example.org.")
        if phone:
            if len(phone) > 50:
                raise ValueError("Phone number cannot exceed 50 characters.")
            if not re.fullmatch(r"[0-9A-Za-z+().\- ]+", phone) or sum(c.isdigit() for c in phone) < 4:
                raise ValueError("Enter a valid phone number with at least four digits.")
        return display_name, email, phone

    def _ensure_person_available(self, cursor, person_id, user_id=None):
        if person_id is None:
            return
        self.repository._execute(cursor, "SELECT COUNT(*) FROM tblPerson WHERE ID=?", (person_id,))
        if not cursor.fetchone()[0]:
            raise ValueError("The selected person no longer exists.")
        self.repository._execute(
            cursor, "SELECT COUNT(*) FROM tblUser WHERE PersonID=? AND ID<>?",
            (person_id, user_id or 0),
        )
        if cursor.fetchone()[0]:
            raise ValueError("That person is already linked to another user.")

    def create_user(self, username, display_name, temporary_password, role_ids=(),
                    email=None, phone=None, person_id=None):
        username = username.strip()
        display_name, email, phone = self.normalize_contact(display_name, email, phone)
        if not username:
            raise ValueError("Username is required.")
        password_hash = self.passwords.hash(temporary_password)
        cursor = self._cursor()
        try:
            self.repository._execute(
                cursor, "SELECT COUNT(*) FROM tblUser WHERE Username=?", (username,)
            )
            if cursor.fetchone()[0]:
                raise ValueError("That username already exists.")
            self._ensure_person_available(cursor, person_id)
            self.repository._execute(
                cursor,
                "INSERT INTO tblUser "
                "(Username, DisplayName, Email, Phone, PersonID, PasswordHash, Active, MustChangePassword) "
                "VALUES (?, ?, ?, ?, ?, ?, 1, 1)",
                (username, display_name, email, phone, person_id, password_hash),
            )
            user_id = cursor.lastrowid
            self._replace_roles(cursor, user_id, role_ids)
            self._audit(cursor, "USER_CREATED", user_id, "Created {}".format(username))
            if person_id is not None:
                self.repository._execute(
                    cursor,
                    "INSERT INTO tblSecurityAuditEvent "
                    "(UserID, Action, EntityType, EntityID, AfterJSON) "
                    "VALUES (?, 'USER_PERSON_LINK_CHANGED', 'User', ?, ?)",
                    (
                        self.acting_user_id, str(user_id),
                        json.dumps({"linked": True}),
                    ),
                )
            self.connection.commit()
            return user_id
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def update_contact(self, user_id, display_name, email=None, phone=None,
                       person_id=_PERSON_UNCHANGED):
        display_name, email, phone = self.normalize_contact(display_name, email, phone)
        cursor = self._cursor()
        try:
            fields = "DisplayName, Email, Phone"
            if person_id is not _PERSON_UNCHANGED:
                fields += ", PersonID"
            self.repository._execute(
                cursor, f"SELECT {fields} FROM tblUser WHERE ID=? FOR UPDATE",
                (user_id,),
            )
            existing = cursor.fetchone()
            if not existing:
                raise ValueError("The selected user no longer exists.")
            before = (existing[0] or "", existing[1] or None, existing[2] or None)
            after = (display_name, email, phone)
            field_names = ("DisplayName", "Email", "Phone")
            if person_id is not _PERSON_UNCHANGED:
                self._ensure_person_available(cursor, person_id, user_id)
                before += (existing[3],)
                after += (person_id,)
                field_names += ("PersonID",)
            changed = [
                name for name, old, new in zip(field_names, before, after)
                if old != new
            ]
            if not changed:
                self.connection.rollback()
                return False
            if person_id is _PERSON_UNCHANGED:
                sql = "UPDATE tblUser SET DisplayName=?, Email=?, Phone=? WHERE ID=?"
                values = (display_name, email, phone, user_id)
            else:
                sql = "UPDATE tblUser SET DisplayName=?, Email=?, Phone=?, PersonID=? WHERE ID=?"
                values = (display_name, email, phone, person_id, user_id)
            self.repository._execute(cursor, sql, values)
            contact_changes = [name for name in changed if name != "PersonID"]
            if contact_changes:
                self.repository._execute(
                    cursor,
                    "INSERT INTO tblSecurityAuditEvent "
                    "(UserID, Action, EntityType, EntityID, AfterJSON) "
                    "VALUES (?, 'USER_CONTACT_UPDATED', 'User', ?, ?)",
                    (
                        self.acting_user_id, str(user_id),
                        json.dumps({"changed_fields": contact_changes}),
                    ),
                )
            if "PersonID" in changed:
                self.repository._execute(
                    cursor,
                    "INSERT INTO tblSecurityAuditEvent "
                    "(UserID, Action, EntityType, EntityID, AfterJSON) "
                    "VALUES (?, 'USER_PERSON_LINK_CHANGED', 'User', ?, ?)",
                    (
                        self.acting_user_id, str(user_id),
                        json.dumps({"linked": person_id is not None}),
                    ),
                )
            self.connection.commit()
            return True
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    @staticmethod
    def welcome_message(display_name, username):
        """Build a password-free account welcome message."""
        return JSForm.MailMessage(
            "Your ChurchManager account is ready",
            "Hello {},\n\n"
            "A ChurchManager account has been created for you.\n\n"
            "Username: {}\n\n"
            "Open ChurchManager using the ChurchManager shortcut. Your temporary "
            "password must be changed the first time you sign in. Contact your "
            "ChurchManager administrator to receive that temporary password through "
            "a separate channel.\n\n"
            "The temporary password is intentionally not included in this email."
            .format(display_name, username),
        )

    def send_welcome_email(self, user_id, mail_service):
        """Send and safely audit an explicit new-user welcome message."""
        cursor = self._cursor()
        try:
            self.repository._execute(
                cursor, "SELECT Username,DisplayName,COALESCE(Email,'') FROM tblUser WHERE ID=?",
                (user_id,),
            )
            row = cursor.fetchone()
            if not row:
                raise ValueError("The selected user no longer exists.")
            if not JSForm.valid_email(row[2]):
                raise ValueError("The selected user does not have a valid email address.")
            try:
                results = mail_service.send(
                    (row[2],), self.welcome_message(row[1], row[0])
                )
            except Exception as error:
                self._audit(cursor, "USER_WELCOME_EMAIL_FAILED", user_id, "Delivery failed")
                self.connection.commit()
                raise RuntimeError(
                    "The welcome email could not be delivered. "
                    "The user account remains available."
                ) from error
            if not results or not all(result.succeeded for result in results):
                self._audit(cursor, "USER_WELCOME_EMAIL_FAILED", user_id, "Delivery failed")
                self.connection.commit()
                raise RuntimeError(
                    "The welcome email could not be delivered. "
                    "The user account remains available."
                )
            self._audit(cursor, "USER_WELCOME_EMAIL_SENT", user_id, "Welcome instructions sent")
            self.connection.commit()
            return results
        except (ValueError, RuntimeError):
            raise
        except Exception as error:
            self.connection.rollback()
            raise RuntimeError("The welcome email could not be delivered. The user account remains available.") from error
        finally:
            cursor.close()

    def set_roles(self, user_id, role_ids):
        cursor = self._cursor()
        try:
            self.repository._execute(
                cursor, "SELECT MasterAdministrator FROM tblUser WHERE ID=?", (user_id,)
            )
            row = cursor.fetchone()
            if not row:
                raise ValueError("The selected user no longer exists.")
            self._replace_roles(cursor, user_id, role_ids, preserve_master=bool(row[0]))
            self._audit(cursor, "USER_ROLES_CHANGED", user_id)
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def _replace_roles(self, cursor, user_id, role_ids, preserve_master=False):
        if preserve_master:
            self.repository._execute(
                cursor,
                "DELETE ur FROM tblUserRole ur JOIN tblRole r ON r.ID=ur.RoleID "
                "WHERE ur.UserID=? AND r.Name <> 'Master Administrator'",
                (user_id,),
            )
        else:
            self.repository._execute(
                cursor, "DELETE FROM tblUserRole WHERE UserID=?", (user_id,)
            )
        for role_id in sorted(set(role_ids)):
            self.repository._execute(
                cursor,
                "INSERT INTO tblUserRole (UserID, RoleID, AssignedByUserID) "
                "SELECT ?, ID, ? FROM tblRole "
                "WHERE ID=? AND Active=1 AND Name <> 'Master Administrator'",
                (user_id, self.acting_user_id, role_id),
            )

    def set_active(self, user_id, active):
        cursor = self._cursor()
        try:
            self.repository._execute(
                cursor,
                "SELECT Active, MasterAdministrator FROM tblUser WHERE ID=?",
                (user_id,),
            )
            row = cursor.fetchone()
            if not row:
                raise ValueError("The selected user no longer exists.")
            if not active and row[1]:
                self.repository._execute(
                    cursor,
                    "SELECT COUNT(*) FROM tblUser "
                    "WHERE Active=1 AND MasterAdministrator=1",
                )
                self.ensure_can_disable(True, cursor.fetchone()[0])
            self.repository._execute(
                cursor, "UPDATE tblUser SET Active=? WHERE ID=?", (int(active), user_id)
            )
            self._audit(cursor, "USER_ENABLED" if active else "USER_DISABLED", user_id)
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def unlock(self, user_id):
        cursor = self._cursor()
        try:
            self.repository._execute(
                cursor,
                "UPDATE tblUser SET FailedLoginCount=0, LockedUntil=NULL WHERE ID=?",
                (user_id,),
            )
            self._audit(cursor, "USER_UNLOCKED", user_id)
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def reset_password(self, user_id, temporary_password):
        password_hash = self.passwords.hash(temporary_password)
        cursor = self._cursor()
        try:
            self.repository._execute(
                cursor,
                "UPDATE tblUser SET PasswordHash=?, MustChangePassword=1, "
                "FailedLoginCount=0, LockedUntil=NULL WHERE ID=?",
                (password_hash, user_id),
            )
            self._audit(cursor, "PASSWORD_RESET", user_id)
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def _audit(self, cursor, action, user_id, reason=None):
        self.repository._execute(
            cursor,
            "INSERT INTO tblSecurityAuditEvent "
            "(UserID, Action, EntityType, EntityID, Reason) "
            "VALUES (?, ?, 'User', ?, ?)",
            (self.acting_user_id, action, str(user_id), reason),
        )


class PasswordEntryDialog(wx.Dialog):
    def __init__(self, parent, title):
        super().__init__(parent, title=title)
        grid = wx.FlexGridSizer(2, 2, 8, 8)
        grid.AddGrowableCol(1, 1)
        grid.Add(wx.StaticText(self, label="Temporary password"))
        self.password = wx.TextCtrl(self, style=wx.TE_PASSWORD, size=(280, -1))
        grid.Add(self.password, 1, wx.EXPAND)
        grid.Add(wx.StaticText(self, label="Confirm password"))
        self.confirmation = wx.TextCtrl(self, style=wx.TE_PASSWORD)
        grid.Add(self.confirmation, 1, wx.EXPAND)
        root = wx.BoxSizer(wx.VERTICAL)
        root.Add(grid, 1, wx.ALL | wx.EXPAND, 12)
        root.Add(self.CreateSeparatedButtonSizer(wx.OK | wx.CANCEL), 0, wx.ALL | wx.EXPAND, 10)
        self.SetSizerAndFit(root)


class NewUserDialog(PasswordEntryDialog):
    def __init__(self, parent, people):
        wx.Dialog.__init__(self, parent, title="Create ChurchManager User")
        self.people = people
        grid = wx.FlexGridSizer(8, 2, 8, 8)
        grid.AddGrowableCol(1, 1)
        grid.Add(wx.StaticText(self, label="Username"))
        self.username = wx.TextCtrl(self, size=(280, -1))
        grid.Add(self.username, 1, wx.EXPAND)
        grid.Add(wx.StaticText(self, label="Display name"))
        self.display_name = wx.TextCtrl(self)
        grid.Add(self.display_name, 1, wx.EXPAND)
        grid.Add(wx.StaticText(self, label="Email"))
        self.email = wx.TextCtrl(self)
        grid.Add(self.email, 1, wx.EXPAND)
        grid.Add(wx.StaticText(self, label="Phone"))
        self.phone = wx.TextCtrl(self)
        self.phone.Bind(wx.EVT_KILL_FOCUS, _format_phone_control)
        grid.Add(self.phone, 1, wx.EXPAND)
        grid.Add(wx.StaticText(self, label="Linked person"))
        self.person = wx.Choice(
            self, choices=["Not linked to a congregation person"] + [item.display for item in people],
        )
        self.person.SetSelection(0)
        self.person.Bind(wx.EVT_CHOICE, self.on_person_selected)
        grid.Add(self.person, 1, wx.EXPAND)
        grid.Add(wx.StaticText(self, label="Temporary password"))
        self.password = wx.TextCtrl(self, style=wx.TE_PASSWORD)
        grid.Add(self.password, 1, wx.EXPAND)
        grid.Add(wx.StaticText(self, label="Confirm password"))
        self.confirmation = wx.TextCtrl(self, style=wx.TE_PASSWORD)
        grid.Add(self.confirmation, 1, wx.EXPAND)
        grid.AddSpacer(1)
        self.send_welcome = wx.CheckBox(
            self, label="Send welcome email now (temporary password is not included)",
        )
        grid.Add(self.send_welcome, 1, wx.EXPAND)
        root = wx.BoxSizer(wx.VERTICAL)
        root.Add(grid, 1, wx.ALL | wx.EXPAND, 12)
        root.Add(self.CreateSeparatedButtonSizer(wx.OK | wx.CANCEL), 0, wx.ALL | wx.EXPAND, 10)
        self.SetSizerAndFit(root)

    def on_person_selected(self, _event):
        """Use the linked person's first name as the editable display default."""
        selection = self.person.GetSelection()
        if selection > 0:
            self.display_name.SetValue(self.people[selection - 1].first_name)


class UserContactDialog(wx.Dialog):
    def __init__(self, parent, user, people):
        super().__init__(parent, title="Edit User Details")
        self.people = people
        grid = wx.FlexGridSizer(5, 2, 8, 8)
        grid.AddGrowableCol(1, 1)
        grid.Add(wx.StaticText(self, label="Username"))
        username = wx.TextCtrl(self, value=user.username, style=wx.TE_READONLY, size=(320, -1))
        grid.Add(username, 1, wx.EXPAND)
        grid.Add(wx.StaticText(self, label="Display name"))
        self.display_name = wx.TextCtrl(self, value=user.display_name)
        grid.Add(self.display_name, 1, wx.EXPAND)
        grid.Add(wx.StaticText(self, label="Email"))
        self.email = wx.TextCtrl(self, value=user.email)
        grid.Add(self.email, 1, wx.EXPAND)
        grid.Add(wx.StaticText(self, label="Phone"))
        self.phone = wx.TextCtrl(self, value=JSForm.phone_display(user.phone))
        self.phone.Bind(wx.EVT_KILL_FOCUS, _format_phone_control)
        grid.Add(self.phone, 1, wx.EXPAND)
        grid.Add(wx.StaticText(self, label="Linked person"))
        self.person = wx.Choice(
            self, choices=["Not linked to a congregation person"] + [item.display for item in people],
        )
        linked = next(
            (index for index, item in enumerate(people, start=1) if item.id == user.person_id), 0
        )
        self.person.SetSelection(linked)
        grid.Add(self.person, 1, wx.EXPAND)
        root = wx.BoxSizer(wx.VERTICAL)
        root.Add(grid, 1, wx.ALL | wx.EXPAND, 12)
        root.Add(self.CreateSeparatedButtonSizer(wx.OK | wx.CANCEL), 0, wx.ALL | wx.EXPAND, 10)
        self.SetSizerAndFit(root)


class RolePermissionDialog(wx.Dialog):
    def __init__(self, parent, service):
        super().__init__(parent, title="Role Permissions", size=(760, 560))
        self.service = service
        self.roles = service.list_editable_roles()
        self.permissions = service.list_permissions()
        self.role = wx.Choice(self, choices=[role[1] for role in self.roles])
        self.role.Bind(wx.EVT_CHOICE, self.on_role_changed)
        self.permission_list = wx.CheckListBox(
            self,
            choices=[
                "{}{} — {}".format("Sensitive: " if item[3] else "", item[1], item[2] or "")
                for item in self.permissions
            ],
        )
        buttons = self.CreateSeparatedButtonSizer(wx.OK | wx.CANCEL)
        root = wx.BoxSizer(wx.VERTICAL)
        root.Add(wx.StaticText(self, label="Role"), 0, wx.LEFT | wx.TOP, 12)
        root.Add(self.role, 0, wx.ALL | wx.EXPAND, 10)
        root.Add(wx.StaticText(self, label="Permissions"), 0, wx.LEFT, 12)
        root.Add(self.permission_list, 1, wx.ALL | wx.EXPAND, 10)
        root.Add(buttons, 0, wx.ALL | wx.EXPAND, 10)
        self.SetSizer(root)
        if self.roles:
            self.role.SetSelection(0)
            self.load_permissions()

    def on_role_changed(self, event):
        self.load_permissions()

    def load_permissions(self):
        role_id = self.roles[self.role.GetSelection()][0]
        assigned = self.service.permission_ids_for_role(role_id)
        for index, permission in enumerate(self.permissions):
            self.permission_list.Check(index, permission[0] in assigned)

    def save(self):
        if not self.roles:
            return
        role_id = self.roles[self.role.GetSelection()][0]
        selected = [
            permission[0] for index, permission in enumerate(self.permissions)
            if self.permission_list.IsChecked(index)
        ]
        self.service.set_role_permissions(role_id, selected)


class SecurityAuditDialog(wx.Dialog):
    def __init__(self, parent, service):
        super().__init__(parent, title="Security Audit", size=(980, 560))
        records = service.list_security_audit()
        audit_list = wx.ListCtrl(self, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        columns = (
            ("When", 165), ("User", 120), ("Action", 210),
            ("Type", 90), ("Record", 90), ("Reason", 260),
        )
        for index, (label, width) in enumerate(columns):
            audit_list.InsertColumn(index, label, width=width)
        for record in records:
            row = audit_list.InsertItem(
                audit_list.GetItemCount(), str(record.occurred_at)
            )
            for column, value in enumerate((
                record.username, record.action, record.entity_type,
                record.entity_id, record.reason,
            ), start=1):
                audit_list.SetItem(row, column, str(value))
        close = wx.Button(self, wx.ID_CLOSE, "Close")
        close.Bind(wx.EVT_BUTTON, lambda event: self.EndModal(wx.ID_CLOSE))
        root = wx.BoxSizer(wx.VERTICAL)
        root.Add(audit_list, 1, wx.ALL | wx.EXPAND, 10)
        root.Add(close, 0, wx.ALIGN_RIGHT | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        self.SetSizer(root)


class UserAdministrationDialog(wx.Dialog):
    def __init__(self, parent, service, authorization, mail_factory=configured_mail_service):
        super().__init__(parent, title="ChurchManager User Administration", size=(1480, 500))
        self.service = service
        self.authorization = authorization
        self.mail_factory = mail_factory
        self.users = []
        self.list = wx.ListCtrl(self, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        for index, (label, width) in enumerate((
            ("Username", 125), ("Display name", 190), ("Email", 220),
            ("Phone", 145), ("Linked person", 220), ("Active", 65),
            ("Master", 65), ("Roles", 250),
        )):
            self.list.InsertColumn(index, label, width=width)
        self.list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_roles)
        buttons = wx.BoxSizer(wx.HORIZONTAL)
        actions = (
            ("New User", self.on_new), ("Edit Details", self.on_contact),
            ("Send Welcome", self.on_welcome),
            ("Roles", self.on_roles),
            ("Enable/Disable", self.on_active), ("Unlock", self.on_unlock),
            ("Reset Password", self.on_reset),
            ("Role Permissions", self.on_role_permissions),
            ("Security Audit", self.on_security_audit),
        )
        for label, handler in actions:
            button = wx.Button(self, label=label)
            button.Bind(wx.EVT_BUTTON, handler)
            buttons.Add(button, 0, wx.RIGHT, 6)
        close = wx.Button(self, wx.ID_CLOSE, "Close")
        close.Bind(wx.EVT_BUTTON, lambda event: self.EndModal(wx.ID_CLOSE))
        buttons.AddStretchSpacer()
        buttons.Add(close)
        root = wx.BoxSizer(wx.VERTICAL)
        root.Add(self.list, 1, wx.ALL | wx.EXPAND, 10)
        root.Add(buttons, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)
        self.SetSizer(root)
        self.refresh()

    def refresh(self):
        self.users = self.service.list_users()
        self.list.DeleteAllItems()
        for user in self.users:
            row = self.list.InsertItem(self.list.GetItemCount(), user.username)
            self.list.SetItem(row, 1, user.display_name)
            self.list.SetItem(row, 2, user.email)
            self.list.SetItem(row, 3, user.phone)
            self.list.SetItem(row, 4, user.person_name)
            self.list.SetItem(row, 5, "Yes" if user.active else "No")
            self.list.SetItem(row, 6, "Yes" if user.is_master else "No")
            self.list.SetItem(row, 7, ", ".join(user.roles))

    @staticmethod
    def selected_person_id(dialog):
        selection = dialog.person.GetSelection()
        return dialog.people[selection - 1].id if selection > 0 else None

    def selected(self):
        index = self.list.GetFirstSelected()
        if index < 0:
            wx.MessageBox("Select a user first.", "User Administration", wx.OK)
            return None
        return self.users[index]

    def show_error(self, error):
        wx.MessageBox(str(error), "User Administration", wx.OK | wx.ICON_ERROR)

    def on_new(self, event):
        dialog = NewUserDialog(self, self.service.list_available_people())
        try:
            if dialog.ShowModal() != wx.ID_OK:
                return
            if dialog.password.GetValue() != dialog.confirmation.GetValue():
                raise ValueError("The passwords do not match.")
            user_id = self.service.create_user(
                dialog.username.GetValue(), dialog.display_name.GetValue(),
                dialog.password.GetValue(),
                email=dialog.email.GetValue(), phone=dialog.phone.GetValue(),
                person_id=self.selected_person_id(dialog),
            )
            if dialog.send_welcome.GetValue():
                self.service.send_welcome_email(user_id, self.mail_factory())
        except (ValueError, RuntimeError) as error:
            self.show_error(error)
        finally:
            dialog.Destroy()
        self.refresh()

    def on_contact(self, _event):
        user = self.selected()
        if not user:
            return
        dialog = UserContactDialog(
            self, user, self.service.list_available_people(user.id)
        )
        try:
            if dialog.ShowModal() != wx.ID_OK:
                return
            self.service.update_contact(
                user.id, dialog.display_name.GetValue(),
                dialog.email.GetValue(), dialog.phone.GetValue(),
                person_id=self.selected_person_id(dialog),
            )
        except (ValueError, RuntimeError) as error:
            self.show_error(error)
        finally:
            dialog.Destroy()
        self.refresh()

    def on_welcome(self, _event):
        user = self.selected()
        if not user:
            return
        if wx.MessageBox(
            "Send account instructions to {}?\n\nThe temporary password will not be included."
            .format(user.email or "this user"),
            "Send Welcome Email", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION,
        ) != wx.YES:
            return
        try:
            self.service.send_welcome_email(user.id, self.mail_factory())
            wx.MessageBox(
                "The welcome email was sent.", "Welcome Email",
                wx.OK | wx.ICON_INFORMATION,
            )
        except (ValueError, RuntimeError) as error:
            self.show_error(error)

    def on_roles(self, event):
        user = self.selected()
        if not user:
            return
        roles = self.service.list_assignable_roles()
        dialog = wx.MultiChoiceDialog(self, "Assign roles", user.display_name, [r[1] for r in roles])
        assigned = self.service.role_ids_for(user.id)
        dialog.SetSelections([i for i, role in enumerate(roles) if role[0] in assigned])
        try:
            if dialog.ShowModal() == wx.ID_OK:
                self.service.set_roles(user.id, [roles[i][0] for i in dialog.GetSelections()])
        except (ValueError, RuntimeError) as error:
            self.show_error(error)
        finally:
            dialog.Destroy()
        self.refresh()

    def on_active(self, event):
        user = self.selected()
        if not user:
            return
        try:
            self.service.set_active(user.id, not user.active)
        except (ValueError, RuntimeError) as error:
            self.show_error(error)
        self.refresh()

    def on_unlock(self, event):
        user = self.selected()
        if user:
            try:
                self.service.unlock(user.id)
            except RuntimeError as error:
                self.show_error(error)
            self.refresh()

    def on_reset(self, event):
        user = self.selected()
        if not user:
            return
        dialog = PasswordEntryDialog(self, "Reset Password for {}".format(user.username))
        try:
            if dialog.ShowModal() != wx.ID_OK:
                return
            if dialog.password.GetValue() != dialog.confirmation.GetValue():
                raise ValueError("The passwords do not match.")
            self.service.reset_password(user.id, dialog.password.GetValue())
        except (ValueError, RuntimeError) as error:
            self.show_error(error)
        finally:
            dialog.Destroy()
        self.refresh()

    def on_role_permissions(self, event):
        try:
            self.authorization.require(
                "security.roles.manage", "manage role permissions"
            )
        except PermissionError as error:
            self.show_error(error)
            return
        dialog = RolePermissionDialog(self, self.service)
        try:
            if dialog.ShowModal() == wx.ID_OK:
                dialog.save()
        except (ValueError, RuntimeError) as error:
            self.show_error(error)
        finally:
            dialog.Destroy()

    def on_security_audit(self, event):
        try:
            self.authorization.require(
                "security.audit.view", "view the security audit"
            )
        except PermissionError as error:
            self.show_error(error)
            return
        dialog = SecurityAuditDialog(self, self.service)
        try:
            dialog.ShowModal()
        finally:
            dialog.Destroy()


def show_user_administration(
    parent, connection, session, authorization, minimum_length=12, test_mode=False,
):
    authorization.require("security.users.manage", "manage ChurchManager users")
    service = UserAdministrationService(
        connection, session.user_id,
        passwords=PasswordService(minimum_length=minimum_length),
    )
    dialog = UserAdministrationDialog(
        parent, service, authorization,
        mail_factory=lambda: configured_mail_service(test_mode=test_mode),
    )
    try:
        dialog.ShowModal()
    finally:
        dialog.Destroy()
