"""Protected ChurchManager user and role administration."""

from __future__ import annotations

import json
from dataclasses import dataclass

import wx

from authentication import MariaDBUserRepository, PasswordService


@dataclass(frozen=True)
class UserSummary:
    id: int
    username: str
    display_name: str
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
                "SELECT u.ID, u.Username, u.DisplayName, u.Active, "
                "u.MasterAdministrator, u.FailedLoginCount, u.LockedUntil, "
                "GROUP_CONCAT(r.Name ORDER BY r.Name SEPARATOR ', ') "
                "FROM tblUser u LEFT JOIN tblUserRole ur ON ur.UserID=u.ID "
                "LEFT JOIN tblRole r ON r.ID=ur.RoleID "
                "GROUP BY u.ID, u.Username, u.DisplayName, u.Active, "
                "u.MasterAdministrator, u.FailedLoginCount, u.LockedUntil "
                "ORDER BY u.DisplayName, u.Username",
            )
            rows = cursor.fetchall()
        finally:
            cursor.close()
        return [
            UserSummary(
                row[0], row[1], row[2], bool(row[3]), bool(row[4]), row[5], row[6],
                tuple(filter(None, (row[7] or "").split(", "))),
            )
            for row in rows
        ]

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

    def create_user(self, username, display_name, temporary_password, role_ids=()):
        username = username.strip()
        display_name = display_name.strip()
        if not username or not display_name:
            raise ValueError("Username and display name are required.")
        password_hash = self.passwords.hash(temporary_password)
        cursor = self._cursor()
        try:
            self.repository._execute(
                cursor, "SELECT COUNT(*) FROM tblUser WHERE Username=?", (username,)
            )
            if cursor.fetchone()[0]:
                raise ValueError("That username already exists.")
            self.repository._execute(
                cursor,
                "INSERT INTO tblUser "
                "(Username, DisplayName, PasswordHash, Active, MustChangePassword) "
                "VALUES (?, ?, ?, 1, 1)",
                (username, display_name, password_hash),
            )
            user_id = cursor.lastrowid
            self._replace_roles(cursor, user_id, role_ids)
            self._audit(cursor, "USER_CREATED", user_id, "Created {}".format(username))
            self.connection.commit()
            return user_id
        except Exception:
            self.connection.rollback()
            raise
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
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, title="Create ChurchManager User")
        grid = wx.FlexGridSizer(4, 2, 8, 8)
        grid.AddGrowableCol(1, 1)
        grid.Add(wx.StaticText(self, label="Username"))
        self.username = wx.TextCtrl(self, size=(280, -1))
        grid.Add(self.username, 1, wx.EXPAND)
        grid.Add(wx.StaticText(self, label="Display name"))
        self.display_name = wx.TextCtrl(self)
        grid.Add(self.display_name, 1, wx.EXPAND)
        grid.Add(wx.StaticText(self, label="Temporary password"))
        self.password = wx.TextCtrl(self, style=wx.TE_PASSWORD)
        grid.Add(self.password, 1, wx.EXPAND)
        grid.Add(wx.StaticText(self, label="Confirm password"))
        self.confirmation = wx.TextCtrl(self, style=wx.TE_PASSWORD)
        grid.Add(self.confirmation, 1, wx.EXPAND)
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
    def __init__(self, parent, service, authorization):
        super().__init__(parent, title="ChurchManager User Administration", size=(1080, 430))
        self.service = service
        self.authorization = authorization
        self.users = []
        self.list = wx.ListCtrl(self, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        for index, (label, width) in enumerate((
            ("Username", 130), ("Display name", 210), ("Active", 70),
            ("Master", 70), ("Roles", 280),
        )):
            self.list.InsertColumn(index, label, width=width)
        buttons = wx.BoxSizer(wx.HORIZONTAL)
        actions = (
            ("New User", self.on_new), ("Roles", self.on_roles),
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
            self.list.SetItem(row, 2, "Yes" if user.active else "No")
            self.list.SetItem(row, 3, "Yes" if user.is_master else "No")
            self.list.SetItem(row, 4, ", ".join(user.roles))

    def selected(self):
        index = self.list.GetFirstSelected()
        if index < 0:
            wx.MessageBox("Select a user first.", "User Administration", wx.OK)
            return None
        return self.users[index]

    def show_error(self, error):
        wx.MessageBox(str(error), "User Administration", wx.OK | wx.ICON_ERROR)

    def on_new(self, event):
        dialog = NewUserDialog(self)
        try:
            if dialog.ShowModal() != wx.ID_OK:
                return
            if dialog.password.GetValue() != dialog.confirmation.GetValue():
                raise ValueError("The passwords do not match.")
            self.service.create_user(
                dialog.username.GetValue(), dialog.display_name.GetValue(),
                dialog.password.GetValue(),
            )
        except (ValueError, RuntimeError) as error:
            self.show_error(error)
        finally:
            dialog.Destroy()
        self.refresh()

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


def show_user_administration(parent, connection, session, authorization):
    authorization.require("security.users.manage", "manage ChurchManager users")
    service = UserAdministrationService(connection, session.user_id)
    dialog = UserAdministrationDialog(parent, service, authorization)
    try:
        dialog.ShowModal()
    finally:
        dialog.Destroy()
