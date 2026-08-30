"""User-facing database backup and protected restore workflow."""
from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
import os
import wx

from backup_service import BackupError, BackupPreferences
from pastoral_recovery_admin import PastoralRecoveryAdministration
from pastoral_key_rotation import (
    MariaDBPastoralKeyRotationRepository,
    PastoralKeyRotationService,
)
from pastoral_note_crypto import PastoralNoteCipher


def mariadb_tools_directory(jsform):
    value = jsform.CONFIG.get_Config_Value("Location", "MySQLDump")
    candidates = []
    if value:
        candidates.append(Path(value).expanduser())
    program_files = Path(os.environ.get("ProgramFiles", r"C:\Program Files"))
    candidates.extend(sorted(program_files.glob("MariaDB */bin"), reverse=True))
    for candidate in candidates:
        try:
            from backup_service import BackupService
            BackupService._tool(candidate, "mysqldump", "mariadb-dump")
            BackupService._tool(candidate, "mariadb", "mysql")
            return str(candidate)
        except (OSError, BackupError):
            continue
    raise BackupError(
        "MariaDB backup tools were not found. Install MariaDB client tools or correct Location/MySQLDump."
    )


def close_database_connections(context):
    """Release ChurchManager's single owned database connection before restore."""
    context.database.close()


class BackupRestoreDialog(wx.Dialog):
    def __init__(self, parent, context, jsform):
        super().__init__(parent, title="ChurchManager Backup and Restore", size=(720, 540),
                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.context=context; self.jsform=jsform; self.preferences=BackupPreferences()
        self.values=self.preferences.load(); self.can_restore=context.authorization.has_permission("application.database.restore")
        recovery = getattr(context.services.backups, "recovery", None)
        self.pastoral_recovery = (
            PastoralRecoveryAdministration(
                context.connection, context.session, context.authorization, recovery
            )
            if recovery is not None else None
        )
        panel=wx.Panel(self); outer=wx.BoxSizer(wx.VERTICAL)
        title=wx.StaticText(panel,label="Database Backup")
        title.SetFont(title.GetFont().Bold()); outer.Add(title,0,wx.ALL,10)
        info=wx.StaticText(panel,label=f"Active database: {context.settings['database']}    Server: {context.settings['server']}")
        info.SetForegroundColour(wx.Colour(0,90,190)); outer.Add(info,0,wx.LEFT|wx.RIGHT|wx.BOTTOM,10)
        folder_row=wx.BoxSizer(wx.HORIZONTAL); folder_row.Add(wx.StaticText(panel,label="Backup folder:"),0,wx.ALIGN_CENTER_VERTICAL|wx.RIGHT,8)
        self.folder=wx.DirPickerCtrl(panel,path=self.values["folder"],message="Select the ChurchManager backup folder")
        folder_row.Add(self.folder,1,wx.EXPAND); outer.Add(folder_row,0,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM,10)
        self.automatic=wx.CheckBox(panel,label="Create one automatic backup per day when ChurchManager closes normally")
        self.automatic.SetValue(bool(self.values["automatic_on_exit"])); outer.Add(self.automatic,0,wx.LEFT|wx.RIGHT|wx.BOTTOM,10)
        self.last_backup=wx.StaticText(panel,label=self._last_backup_text())
        outer.Add(self.last_backup,0,wx.LEFT|wx.RIGHT|wx.BOTTOM,10)
        backup=wx.Button(panel,label="Backup Now"); backup.Bind(wx.EVT_BUTTON,self.on_backup); outer.Add(backup,0,wx.LEFT|wx.RIGHT|wx.BOTTOM,10)
        if context.authorization.has_permission("pastoral.care.admin") and self.pastoral_recovery:
            recovery_box = wx.StaticBoxSizer(wx.VERTICAL, panel, "Pastoral Note Recovery")
            self.recovery_status = wx.StaticText(panel, label=self._recovery_status_text())
            recovery_box.Add(self.recovery_status, 0, wx.ALL, 8)
            self.recovery_button = wx.Button(panel, label=self._recovery_button_label())
            self.recovery_button.Bind(wx.EVT_BUTTON, self.on_configure_recovery)
            recovery_box.Add(self.recovery_button, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)
            self.rotation_button = wx.Button(panel, label="Rotate Encryption Key...")
            self.rotation_button.Enable(self.pastoral_recovery.configured)
            self.rotation_button.SetToolTip(
                "Creates verified before-and-after backups and re-encrypts all "
                "restricted pastoral notes with a new key version."
            )
            self.rotation_button.Bind(wx.EVT_BUTTON, self.on_rotate_pastoral_key)
            recovery_box.Add(
                self.rotation_button, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 8
            )
            outer.Add(recovery_box, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        line=wx.StaticLine(panel); outer.Add(line,0,wx.EXPAND|wx.ALL,10)
        restore_title=wx.StaticText(panel,label="Restore Database")
        restore_title.SetFont(restore_title.GetFont().Bold()); outer.Add(restore_title,0,wx.LEFT|wx.RIGHT|wx.BOTTOM,10)
        warning=wx.StaticText(panel,label="Restore replaces the active database. Changes made after the selected backup will be lost.")
        warning.SetForegroundColour(wx.Colour(180,35,25)); outer.Add(warning,0,wx.LEFT|wx.RIGHT|wx.BOTTOM,10)
        restore=wx.Button(panel,label="Restore from Backup..."); restore.Enable(self.can_restore); restore.Bind(wx.EVT_BUTTON,self.on_restore)
        restore.SetToolTip("Requires the protected database restore permission.")
        outer.Add(restore,0,wx.LEFT|wx.RIGHT|wx.BOTTOM,10)
        buttons=wx.BoxSizer(wx.HORIZONTAL); buttons.AddStretchSpacer(); close=wx.Button(panel,wx.ID_CLOSE,"Close"); close.Bind(wx.EVT_BUTTON,self.on_close); buttons.Add(close)
        outer.Add(buttons,0,wx.EXPAND|wx.ALL,10); panel.SetSizer(outer)

    def save_preferences(self):
        self.values.update(folder=self.folder.GetPath(),automatic_on_exit=self.automatic.GetValue())
        self.preferences.save(self.values)

    def _last_backup_text(self):
        when=self.values.get("last_successful_at") or "Not yet recorded"
        path=self.values.get("last_successful_backup") or ""
        return "Last successful backup: {}{}".format(when, "\n"+path if path else "")

    def _recovery_status_text(self):
        if self.pastoral_recovery.configured:
            return "Ready. New backups include protected pastoral-note recovery data."
        return "Not configured. Restricted pastoral-note entry remains unavailable."

    def _recovery_button_label(self):
        return (
            "Replace Recovery Password..."
            if self.pastoral_recovery.configured
            else "Set Up Recovery..."
        )

    def on_configure_recovery(self, _event):
        self.context.authorization.require(
            "pastoral.care.admin", "administer pastoral-note recovery"
        )
        first = wx.PasswordEntryDialog(
            self,
            "Create a separate pastoral-note recovery password.\n\n"
            "ChurchManager cannot recover this password. Store it securely outside "
            "this computer.",
            "Pastoral Note Recovery",
        )
        try:
            if first.ShowModal() != wx.ID_OK:
                return
            password = first.GetValue()
        finally:
            first.Destroy()
        confirm = wx.PasswordEntryDialog(
            self, "Enter the same recovery password again:",
            "Confirm Pastoral Note Recovery Password",
        )
        try:
            if confirm.ShowModal() != wx.ID_OK:
                return
            confirmation = confirm.GetValue()
        finally:
            confirm.Destroy()
        try:
            if password != confirmation:
                raise ValueError("The recovery passwords did not match.")
            self.pastoral_recovery.configure(password)
            self.recovery_status.SetLabel(self._recovery_status_text())
            self.recovery_button.SetLabel(self._recovery_button_label())
            self.rotation_button.Enable(True)
            wx.MessageBox(
                "Pastoral-note recovery is ready. Future ChurchManager backups will "
                "include a protected recovery file beside the SQL backup.",
                "Recovery Ready", wx.OK | wx.ICON_INFORMATION, self,
            )
        except Exception as error:
            wx.MessageBox(str(error), "Recovery Setup Failed", wx.OK | wx.ICON_ERROR, self)
        finally:
            password = None
            confirmation = None

    def on_rotate_pastoral_key(self, _event):
        """Confirm and run protected key rotation with matched backups."""

        self.context.authorization.require(
            "pastoral.care.admin", "rotate pastoral-note encryption"
        )
        warning = wx.MessageDialog(
            self,
            "ChurchManager will create a verified backup, rotate the pastoral-note "
            "encryption key, and create a second verification backup.\n\n"
            "Do not close ChurchManager or interrupt MariaDB during this operation.\n\n"
            "Continue?",
            "Rotate Pastoral Note Encryption Key",
            wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING,
        )
        try:
            if warning.ShowModal() != wx.ID_YES:
                return
        finally:
            warning.Destroy()
        prompt = wx.PasswordEntryDialog(
            self,
            "Enter the separate pastoral-note recovery password:",
            "Authorize Key Rotation",
        )
        try:
            if prompt.ShowModal() != wx.ID_OK:
                return
            recovery_password = prompt.GetValue()
        finally:
            prompt.Destroy()
        try:
            self.save_preferences()
            folder = Path(self.folder.GetPath()).expanduser().resolve()
            tools = mariadb_tools_directory(self.jsform)
            backups = self.context.services.backups

            def create_named_backup(label):
                return backups.create(
                    self.context.settings, tools,
                    folder / "PastoralKeyRotation.{}".format(label),
                )

            service = PastoralKeyRotationService(
                MariaDBPastoralKeyRotationRepository(self.context.connection),
                self.pastoral_recovery.recovery.key_manager,
                PastoralNoteCipher(self.pastoral_recovery.recovery.key_manager),
                self.pastoral_recovery.recovery,
                self.context.session,
                self.context.authorization,
                lambda: create_named_backup("Before"),
                lambda: create_named_backup("Verified"),
            )
            busy = wx.BusyInfo(
                "Rotating the pastoral-note encryption key and verifying backups...",
                self,
            )
            try:
                wx.YieldIfNeeded()
                result = service.rotate(recovery_password)
            finally:
                del busy
            self.record_success(result.verification_backup)
            self.recovery_status.SetLabel(self._recovery_status_text())
            wx.MessageBox(
                "Pastoral-note encryption was rotated from version {} to version {}.\n\n"
                "{} restricted note(s) were re-encrypted.\n\n"
                "Verification backup:\n{}".format(
                    result.previous_version, result.active_version,
                    result.notes_rotated, result.verification_backup.path,
                ),
                "Key Rotation Complete",
                wx.OK | wx.ICON_INFORMATION,
                self,
            )
        except Exception as error:
            wx.MessageBox(
                str(error), "Key Rotation Failed", wx.OK | wx.ICON_ERROR, self
            )
        finally:
            recovery_password = None

    def record_success(self,result):
        self.values["last_successful_backup"]=str(result.path)
        self.values["last_successful_at"]=datetime.now().strftime("%Y-%m-%d %I:%M %p")
        self.preferences.save(self.values); self.last_backup.SetLabel(self._last_backup_text())

    def on_backup(self,_event):
        self.save_preferences()
        try:
            result=self.context.services.backups.create_in_folder(
                self.context.settings,mariadb_tools_directory(self.jsform),self.folder.GetPath(),False,
            )
            self.record_success(result)
            wx.MessageBox(f"Backup completed successfully.\n\n{result.path}","Backup Complete",wx.OK|wx.ICON_INFORMATION,self)
        except Exception as error:
            wx.MessageBox(str(error),"Backup Failed",wx.OK|wx.ICON_ERROR,self)

    def on_restore(self,_event):
        self.context.authorization.require("application.database.restore","restore the database")
        picker=wx.FileDialog(self,"Select a ChurchManager SQL backup",defaultDir=self.folder.GetPath(),wildcard="SQL backups (*.sql)|*.sql|All files (*.*)|*.*",style=wx.FD_OPEN|wx.FD_FILE_MUST_EXIST)
        try:
            if picker.ShowModal()!=wx.ID_OK: return
            path=Path(picker.GetPath()); source=self.context.services.backups.inspect_dump(path)
        except Exception as error:
            wx.MessageBox(str(error),"Invalid Backup",wx.OK|wx.ICON_ERROR,self); return
        finally: picker.Destroy()
        recovery_password = None
        recovery = getattr(self.context.services.backups, "recovery", None)
        if recovery is not None and recovery.sidecar_path(path).is_file():
            recovery_prompt = wx.PasswordEntryDialog(
                self,
                "This backup contains protected pastoral-note recovery data.\n\n"
                "Enter its recovery password before continuing:",
                "Pastoral Note Recovery",
            )
            try:
                if recovery_prompt.ShowModal() != wx.ID_OK:
                    return
                recovery_password = recovery_prompt.GetValue()
            finally:
                recovery_prompt.Destroy()
        prompt=wx.TextEntryDialog(self,
            "This will replace the active database and first create a safety backup.\n\n"
            f"Backup database: {source}\nActive database: {self.context.settings['database']}\n\n"
            "Type the active database name to continue:","Confirm Database Restore")
        try:
            if prompt.ShowModal()!=wx.ID_OK: return
            if prompt.GetValue().strip()!=self.context.settings["database"]:
                wx.MessageBox("The database name did not match. Nothing was restored.","Restore Cancelled",wx.OK|wx.ICON_INFORMATION,self); return
        finally: prompt.Destroy()
        if wx.MessageBox("Final warning: restore the selected backup now?","Confirm Restore",wx.YES_NO|wx.NO_DEFAULT|wx.ICON_WARNING,self)!=wx.YES: return
        self.save_preferences()
        tools_directory = mariadb_tools_directory(self.jsform)
        backup_folder = self.folder.GetPath()
        close_database_connections(self.context)
        self.context.skip_auto_backup = True
        busy = wx.BusyInfo(
            "Restoring the ChurchManager database...\n\nPlease wait. Do not close the program.",
            parent=self,
        )
        wx.YieldIfNeeded()
        try:
            safety=self.context.services.backups.restore(
                self.context.settings,tools_directory,path,backup_folder,
                recovery_password=recovery_password,
            )
            log=Path(os.environ.get("LOCALAPPDATA",Path.cwd()))/"ChurchManager"/"restore.log"
            log.parent.mkdir(parents=True,exist_ok=True)
            with log.open("a",encoding="utf-8") as destination:
                destination.write(f"{datetime.now().isoformat()} user={self.context.session.username} database={self.context.settings['database']} source={path} safety={safety.path}\n")
            self.context.skip_auto_backup=True; self.context.restart_requested=True
            del busy
            busy = None
            wx.MessageBox("Restore completed successfully. ChurchManager will restart.","Restore Complete",wx.OK|wx.ICON_INFORMATION,self)
            self.EndModal(wx.ID_OK); wx.CallAfter(self.GetParent().Close)
        except Exception as error:
            del busy
            busy = None
            self.context.restart_requested = True
            wx.MessageBox(
                "{}\n\nChurchManager must restart because its database connections were closed.".format(error),
                "Restore Failed", wx.OK|wx.ICON_ERROR, self,
            )
            self.EndModal(wx.ID_CANCEL)
            wx.CallAfter(self.GetParent().Close)
        finally:
            recovery_password = None
            if busy is not None:
                del busy

    def on_close(self,_event):
        self.save_preferences(); self.EndModal(wx.ID_CLOSE)


def run_automatic_exit_backup(context, jsform, today=None):
    preferences=BackupPreferences(); values=preferences.load(); current=(today or date.today()).isoformat()
    if not values["automatic_on_exit"] or values["last_automatic_date"]==current:
        return None
    result=context.services.backups.create_in_folder(
        context.settings,mariadb_tools_directory(jsform),values["folder"],True,
    )
    context.services.backups.prune_automatic(values["folder"],context.settings["database"],30)
    values["last_automatic_date"]=current
    values["last_successful_backup"]=str(result.path)
    values["last_successful_at"]=datetime.now().strftime("%Y-%m-%d %I:%M %p")
    preferences.save(values); return result


def show_backup_restore(parent,context,jsform):
    dialog=BackupRestoreDialog(parent,context,jsform)
    try: dialog.ShowModal()
    finally: dialog.Destroy()
