"""Install ChurchManager's native application menu through JSForm commands."""

from pathlib import Path
import os

import JSForm

from main_menu import MENU_CONTROLS, MENU_LABELS, command_name
from permission_catalog import MAIN_MENU_PERMISSIONS


MENU_ROOT = Path(__file__).resolve().parent / "Menus"


def install_churchmanager_menu(main_form, application_context, dispatch_control):
    """Register, load, and install the main ChurchManager menu bar."""
    registry = JSForm.CommandRegistry()
    registry.register_many(
        JSForm.ApplicationCommand(
            command_name(control_name),
            MENU_LABELS[control_name],
            lambda _context, selected=control_name: dispatch_control(selected),
            permission=MAIN_MENU_PERMISSIONS[control_name],
            help_text="Open {}".format(MENU_LABELS[control_name]),
        )
        for control_name in sorted(MENU_CONTROLS)
    )
    registry.register_many((
        JSForm.ApplicationCommand(
            "session.help", "User Guide",
            lambda _context: dispatch_control("lblHelp"),
            help_text="Open the ChurchManager user guide",
        ),
        JSForm.ApplicationCommand(
            "session.change_password", "Change Password",
            lambda _context: dispatch_control("lblChangePassword"),
        ),
        JSForm.ApplicationCommand(
            "session.logout", "Log Out",
            lambda _context: dispatch_control("lblLogout"),
        ),
    ))

    customization = (
        Path(os.environ.get("LOCALAPPDATA", Path.cwd()))
        / "ChurchManager" / "Menus" / "main.menu.json"
    )

    def command_descriptors():
        categories = {
            "churchmanager": "ChurchManager",
            "session": "Session",
            "tools": "Tools",
        }
        return tuple(
            JSForm.MenuCommandDescriptor(
                command.name, command.label,
                help_text=command.help_text,
                category=categories.get(
                    command.name.split(".", 1)[0], "Other",
                ),
            )
            for command in (registry.get(name) for name in registry.names)
        )

    def open_churchmanager_menu_designer():
        catalog = JSForm.MenuCatalogModel(customization.parent, MENU_ROOT)
        entry = next(
            item for item in catalog.entries()
            if item["filename"] == "main.menu.json"
        )
        custom = catalog.open_customization(entry)
        frame = JSForm.open_menu_designer(
            custom, command_descriptors(), save_path=custom,
            starter_path=MENU_ROOT / "main.menu.json",
        )
        application_context.menu_designer = frame
        return frame

    registry.register(JSForm.ApplicationCommand(
        "tools.menu_designer", "Menu &Designer...",
        lambda _context: open_churchmanager_menu_designer(),
        permission="screens.design",
        help_text="Customize the ChurchManager application menu for the next launch",
    ))

    def command_context():
        return JSForm.CommandContext(
            frame=main_form.FRAME,
            current_form=main_form,
            authorization_policy=(
                application_context.authorization
                or JSForm.AllowAllAuthorizationPolicy()
            ),
            services={"application": application_context},
        )

    definition = JSForm.MenuDefinitionLoader().load_application(
        MENU_ROOT / "main.menu.json", customization, fallback_to_starter=True,
    )
    installer = JSForm.MenuInstaller(
        main_form.FRAME, registry, context_provider=command_context,
    )
    installer.install(definition, current_form=lambda: main_form)
    return installer
