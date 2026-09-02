"""Nontechnical fresh-install wizard for ChurchManager.

The development entry point opens in preview mode by default.  Installed
release packaging may enable application with ``--apply`` after the wizard and
its services have passed visual and isolated-database acceptance.
"""

from __future__ import annotations

import json
import os
import re
import secrets
import sys
from pathlib import Path

import wx
import wx.adv

from authentication import (
    MINIMUM_PASSWORD_LENGTH, generate_temporary_password,
)

from credential_store import delete_credential, read_credential, write_credential
from configuration_paths import configuration_path, ensure_configuration
from installation_executor import FreshInstallationExecutor
from installation_plan import (
    InstallationPlanError,
    InstallationRequest,
    build_installation_plan,
)
from installation_readiness import (
    MARIADB_DOWNLOAD_URL,
    blocking_message,
    find_mariadb_tool,
    inspect_readiness,
)


ROOT = Path(__file__).resolve().parent
CONFIG_PATH = configuration_path()
INSTALLATION_TITLE = "ChurchManager Installation"


def packaged_resource(*parts):
    """Return a source-tree or PyInstaller path for a bundled setup resource."""
    base = Path(getattr(sys, "_MEIPASS", ROOT))
    return base.joinpath(*parts)


def application_account_name(database_name):
    """Return a bounded local MariaDB account name for a validated database."""
    clean = re.sub(r"[^a-z0-9_]", "_", str(database_name).casefold())
    return ("cm_" + clean)[:32]


def save_installed_configuration(database_name, application_user, path=CONFIG_PATH):
    """Atomically save non-secret local production connection settings."""
    path = ensure_configuration(path)
    config = json.loads(path.read_text(encoding="utf-8-sig"))
    values = config.setdefault("database_settings", {})
    values.update({
        "host": "127.0.0.1",
        "port": 3306,
        "user": application_user,
        "database": database_name,
        "credential_target": "ChurchManager/Production",
    })
    config.setdefault("security", {})["production_enabled"] = True
    temporary = path.with_suffix(path.suffix + ".tmp")
    rendered = json.dumps(config, indent=4) + "\n"
    temporary.write_text(rendered, encoding="utf-8")
    try:
        temporary.replace(path)
    except PermissionError:
        # Some Windows security contexts permit updating an owned file but
        # deny deleting/replacing its directory entry. Preserve the prepared
        # contents and use a bounded in-place fallback for that case only.
        path.write_text(rendered, encoding="utf-8")
        temporary.unlink(missing_ok=True)


def finalize_installed_connection(
    result, application_password, *, path=CONFIG_PATH,
    credential_reader=read_credential, credential_writer=write_credential,
    credential_deleter=delete_credential,
):
    """Persist configuration and credential together, restoring both on failure."""
    target = "ChurchManager/Production"
    path = ensure_configuration(path)
    previous_config = path.read_bytes()
    try:
        previous_credential = credential_reader(target)
    except KeyError:
        previous_credential = None
    try:
        credential_writer(target, result.application_user, application_password)
        save_installed_configuration(result.database_name, result.application_user, path)
    except Exception:
        path.write_bytes(previous_config)
        if previous_credential is None:
            credential_deleter(target)
        else:
            credential_writer(target, *previous_credential)
        raise


class SetupPage(wx.adv.WizardPageSimple):
    """Common page shell with a clear heading and explanatory text."""

    def __init__(self, wizard, title, explanation):
        super().__init__(wizard)
        outer = wx.BoxSizer(wx.VERTICAL)
        banner_path = packaged_resource(
            "assets", "brand", "png", "ChurchManager-logo-horizontal-600.png",
        )
        if banner_path.is_file():
            image = wx.Image(str(banner_path), wx.BITMAP_TYPE_PNG)
            if image.IsOk():
                maximum_width = 390
                if image.GetWidth() > maximum_width:
                    height = round(image.GetHeight() * maximum_width / image.GetWidth())
                    image = image.Scale(maximum_width, height, wx.IMAGE_QUALITY_HIGH)
                outer.Add(
                    wx.StaticBitmap(self, bitmap=wx.Bitmap(image)),
                    0,
                    wx.LEFT | wx.RIGHT | wx.TOP,
                    12,
                )
        heading = wx.StaticText(self, label=title)
        font = heading.GetFont(); font.SetPointSize(font.GetPointSize() + 3); font.MakeBold()
        heading.SetFont(font)
        outer.Add(heading, 0, wx.ALL, 12)
        message = wx.StaticText(self, label=explanation)
        message.Wrap(650)
        outer.Add(message, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)
        self.body = wx.BoxSizer(wx.VERTICAL)
        outer.Add(self.body, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)
        self.SetSizer(outer)

    def row(self, label, control):
        line = wx.BoxSizer(wx.HORIZONTAL)
        caption = wx.StaticText(self, label=label)
        # Giving a Windows native StaticText an explicit width together with a
        # -1 height can produce an invalid painted rectangle in packaged wx.
        # Preserve the aligned column with a real, positive label height.
        caption.SetMinSize((170, caption.GetBestSize().GetHeight()))
        line.Add(caption, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 8)
        line.Add(control, 1, wx.EXPAND)
        self.body.Add(line, 0, wx.EXPAND | wx.BOTTOM, 8)


class ChurchManagerSetupWizard(wx.adv.Wizard):
    """Collect a safe installation plan and optionally apply it once."""

    def __init__(self, parent=None, *, apply=False, root=ROOT):
        super().__init__(parent, title=INSTALLATION_TITLE)
        self.SetSize((760, 650))
        self.apply = bool(apply)
        self.root = Path(root)
        self.readiness = inspect_readiness(self.root)
        self.plan = None
        self.installed = False
        self._build_pages()
        self.SetPageSize((720, 520))
        self.Bind(wx.adv.EVT_WIZARD_PAGE_CHANGING, self.on_page_changing)
        self.Bind(wx.adv.EVT_WIZARD_PAGE_CHANGED, self.on_page_changed)

    def _build_pages(self):
        self.system = SetupPage(
            self, "System Check",
            "MariaDB Server is required and must be installed separately. "
            "ChurchManager checks for MariaDB, required components, and disk space "
            "before asking for any database password.",
        )
        self.mariadb_download = wx.adv.HyperlinkCtrl(
            self.system, label="Download MariaDB Server", url=MARIADB_DOWNLOAD_URL,
        )
        self.system.body.Add(self.mariadb_download, 0, wx.BOTTOM, 8)
        self.system_results = wx.TextCtrl(
            self.system, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.BORDER_SIMPLE,
        )
        self.system.body.Add(self.system_results, 1, wx.EXPAND)

        self.database = SetupPage(
            self, "Database Connection",
            "The MariaDB administrator password is used only while setup is running and is never saved.",
        )
        self.server = wx.TextCtrl(self.database, value="127.0.0.1", style=wx.TE_READONLY)
        self.admin_user = wx.TextCtrl(self.database, value="root")
        self.admin_password = wx.TextCtrl(self.database, style=wx.TE_PASSWORD)
        self.database_name = wx.TextCtrl(self.database, value="ChurchManager")
        for label, control in (
            ("Database server", self.server),
            ("Administrator account", self.admin_user),
            ("Administrator password", self.admin_password),
            ("New database name", self.database_name),
        ):
            self.database.row(label, control)

        self.congregation = SetupPage(
            self, "Congregation Setup",
            "Enter the congregation name. Address, logo, hymnal, and lectionary details can also be maintained after installation.",
        )
        self.church_name = wx.TextCtrl(self.congregation)
        self.congregation.row("Congregation name", self.church_name)

        self.master = SetupPage(
            self, "Master Administrator",
            "This first account can administer the system. Its temporary password must be changed at first login.",
        )
        self.master_username = wx.TextCtrl(self.master, value="administrator")
        self.master_display = wx.TextCtrl(self.master, value="Church Administrator")
        self.master_email = wx.TextCtrl(self.master)
        self.master_phone = wx.TextCtrl(self.master)
        self.master_password = wx.TextCtrl(self.master, style=wx.TE_PASSWORD)
        self.master_confirmation = wx.TextCtrl(self.master, style=wx.TE_PASSWORD)
        for label, control in (
            ("Username", self.master_username),
            ("Display name", self.master_display),
            ("Email (optional)", self.master_email),
            ("Phone (optional)", self.master_phone),
            ("Temporary password", self.master_password),
            ("Confirm password", self.master_confirmation),
        ):
            self.master.row(label, control)
        self.master_generated_password = wx.TextCtrl(
            self.master, style=wx.TE_READONLY,
        )
        generate_master_password = wx.Button(
            self.master, label="Generate temporary password",
        )
        generate_master_password.Bind(
            wx.EVT_BUTTON, self.on_generate_master_password,
        )
        generated_password_row = wx.BoxSizer(wx.HORIZONTAL)
        generated_password_row.Add(
            self.master_generated_password, 1, wx.RIGHT | wx.EXPAND, 6,
        )
        generated_password_row.Add(generate_master_password)
        self.master.row("Generated password", generated_password_row)

        self.catalog = SetupPage(
            self, "Catalog Selection",
            "Choose only the metadata catalogs this congregation uses. No selection is required.",
        )
        self.catalog_lists = {}
        for family, title in (
            ("hymnal", "Hymnals"),
            ("lectionary", "Lectionaries"),
            ("order_of_service", "Orders of Service"),
        ):
            label = wx.StaticText(self.catalog, label=title); label.GetFont().MakeBold()
            choices = [
                f"{item.title}  (version {item.version})"
                for item in self.readiness.packages
                if item.family == family and item.valid and item.installable
            ]
            # Keep all three catalog families and both default selectors visible
            # within the supported 720x520 wizard page on standard displays.
            control = wx.CheckListBox(self.catalog, choices=choices, size=(-1, 52))
            self.catalog_lists[family] = control
            self.catalog.body.Add(label, 0, wx.BOTTOM, 3)
            self.catalog.body.Add(control, 0, wx.EXPAND | wx.BOTTOM, 8)
        self.primary_hymnal = wx.Choice(self.catalog, choices=["None"])
        self.default_lectionary = wx.Choice(self.catalog, choices=["None"])
        self.primary_hymnal.SetSelection(0); self.default_lectionary.SetSelection(0)
        self.catalog.row("Primary hymnal", self.primary_hymnal)
        self.catalog.row("Default lectionary", self.default_lectionary)
        for control in self.catalog_lists.values():
            control.Bind(wx.EVT_CHECKLISTBOX, self.on_catalog_check)

        self.review = SetupPage(
            self, "Installation Review",
            "Review the choices below. Passwords are deliberately omitted.",
        )
        self.review_text = wx.TextCtrl(
            self.review, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.BORDER_SIMPLE,
        )
        self.review.body.Add(self.review_text, 1, wx.EXPAND)

        self.finish = SetupPage(
            self, "Install and Verify" if self.apply else "Preview Complete",
            "Setup will report exactly what was verified and will never display a password.",
        )
        self.finish_text = wx.TextCtrl(
            self.finish, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.BORDER_SIMPLE,
        )
        self.finish.body.Add(self.finish_text, 1, wx.EXPAND)

        pages = [
            self.system, self.database, self.congregation, self.master,
            self.catalog, self.review, self.finish,
        ]
        for left, right in zip(pages, pages[1:]):
            wx.adv.WizardPageSimple.Chain(left, right)
        self.first_page = pages[0]
        self._show_readiness()

    def _show_readiness(self):
        lines = []
        for check in self.readiness.checks:
            lines.append(("Ready: " if check.passed else "Needs attention: ") + check.message)
        invalid = [item for item in self.readiness.packages if not item.installable]
        if invalid:
            lines.append("")
            lines.append("Catalog notes:")
            lines.extend(f"- {item.title}: {item.message}" for item in invalid)
        self.system_results.SetValue("\n".join(lines))

    def on_catalog_check(self, _event):
        self._refresh_default_choices()

    def on_generate_master_password(self, _event):
        """Generate and display the initial account's temporary password once."""
        password = generate_temporary_password(MINIMUM_PASSWORD_LENGTH)
        self.master_password.SetValue(password)
        self.master_confirmation.SetValue(password)
        self.master_generated_password.SetValue(password)
        self.master_generated_password.SetFocus()
        self.master_generated_password.SelectAll()

    def _selected(self, family):
        available = [
            item for item in self.readiness.packages
            if item.family == family and item.valid and item.installable
        ]
        control = self.catalog_lists[family]
        return tuple(available[index] for index in range(control.GetCount()) if control.IsChecked(index))

    def _refresh_default_choices(self):
        def update(choice, items):
            previous = choice.GetStringSelection()
            labels = ["None"] + [item.title for item in items]
            choice.Set(labels)
            choice.SetSelection(labels.index(previous) if previous in labels else 0)
        update(self.primary_hymnal, self._selected("hymnal"))
        update(self.default_lectionary, self._selected("lectionary"))

    def _request(self):
        selected = {family: self._selected(family) for family in self.catalog_lists}
        primary_index = self.primary_hymnal.GetSelection() - 1
        default_index = self.default_lectionary.GetSelection() - 1
        return InstallationRequest(
            church_name=self.church_name.GetValue(),
            database_name=self.database_name.GetValue(),
            master_username=self.master_username.GetValue(),
            master_display_name=self.master_display.GetValue(),
            hymnal_packages=tuple(item.code for item in selected["hymnal"]),
            lectionary_packages=tuple(item.code for item in selected["lectionary"]),
            order_of_service_packages=tuple(item.code for item in selected["order_of_service"]),
            primary_hymnal=(selected["hymnal"][primary_index].code if primary_index >= 0 else None),
            default_lectionary=(selected["lectionary"][default_index].code if default_index >= 0 else None),
            master_email=self.master_email.GetValue(),
            master_phone=self.master_phone.GetValue(),
        )

    def _build_plan(self):
        self.plan = build_installation_plan(self._request(), self.readiness)
        if len(self.master_password.GetValue()) < MINIMUM_PASSWORD_LENGTH:
            raise InstallationPlanError(
                "The temporary password must contain at least {} characters."
                .format(MINIMUM_PASSWORD_LENGTH)
            )
        if self.master_password.GetValue() != self.master_confirmation.GetValue():
            raise InstallationPlanError("The temporary passwords do not match.")
        packages = "\n".join(f"  - {item.title}" for item in self.plan.selected_packages) or "  None"
        self.review_text.SetValue(
            f"Congregation: {self.plan.church_name}\n"
            f"Database: {self.plan.database_name}\n"
            f"Database account: {application_account_name(self.plan.database_name)}\n"
            f"Master Administrator: {self.plan.master_display_name} ({self.plan.master_username})\n\n"
            f"Selected catalogs:\n{packages}\n\n"
            f"Primary hymnal: {self.plan.primary_hymnal or 'None'}\n"
            f"Default lectionary: {self.plan.default_lectionary or 'None'}\n\n"
            + ("Select Next to install and verify ChurchManager."
               if self.apply else
               "Preview mode: no database, account, credential, or configuration will be changed.")
        )

    def on_page_changing(self, event):
        if not event.GetDirection():
            return
        page = event.GetPage()
        try:
            if page is self.system and not self.readiness.ready:
                raise InstallationPlanError(blocking_message(self.readiness))
            if page is self.database and self.apply and not self.admin_password.GetValue():
                raise InstallationPlanError("The MariaDB administrator password is required.")
            if page is self.catalog:
                self._build_plan()
        except InstallationPlanError as error:
            wx.MessageBox(str(error), "Setup Needs Attention", wx.OK | wx.ICON_WARNING, self)
            event.Veto()

    def on_page_changed(self, event):
        if event.GetPage() is self.finish and not self.installed:
            if self.apply:
                self._apply_installation()
            else:
                self.finish_text.SetValue(
                    "The installation plan is valid.\n\n"
                    "Preview mode made no changes to this computer."
                )

    def _apply_installation(self):
        import mariadb

        admin = None
        application_password = secrets.token_urlsafe(24)
        account = application_account_name(self.plan.database_name)
        busy = wx.BusyInfo("Installing and verifying ChurchManager...", self)
        wx.YieldIfNeeded()
        try:
            admin = mariadb.connect(
                host="127.0.0.1", port=3306,
                user=self.admin_user.GetValue().strip(),
                password=self.admin_password.GetValue(), autocommit=True,
            )
            executor = FreshInstallationExecutor(
                admin, mariadb.connect, root=self.root,
                database_errors=(mariadb.Error,),
                progress=self._show_progress,
            )
            result = executor.install(
                self.plan, account, application_password,
                self.master_password.GetValue(), self.master_confirmation.GetValue(),
                dump_directory=find_mariadb_tool("mariadb-dump.exe").parent,
                backup_folder=(
                    Path(os.environ.get("LOCALAPPDATA", self.root))
                    / "ChurchManager" / "Backups"
                ),
                completion_callback=finalize_installed_connection,
            )
            self.installed = True
            self.finish_text.SetValue(result.completion_report())
        except Exception as error:
            self.finish_text.SetValue(
                "ChurchManager installation did not complete.\n\n" + str(error)
            )
            wx.MessageBox(str(error), "Installation Did Not Complete", wx.OK | wx.ICON_ERROR, self)
        finally:
            del busy
            application_password = ""
            self.admin_password.SetValue("")
            self.master_password.SetValue("")
            self.master_confirmation.SetValue("")
            if admin is not None:
                admin.close()

    def _show_progress(self, message):
        self.finish_text.AppendText(str(message) + "\n")
        wx.YieldIfNeeded()


def show_setup_wizard(*, apply=False):
    """Open the setup wizard and return whether its flow reached Finish."""
    wizard = ChurchManagerSetupWizard(None, apply=apply)
    try:
        return wizard.RunWizard(wizard.first_page)
    finally:
        wizard.Destroy()
