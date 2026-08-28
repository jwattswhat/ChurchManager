"""ChurchManager application composition root."""

from dataclasses import dataclass
import os

import wx
import JSForm

import fnCMargParse
from development_boundary import assert_development_isolation
from authorization import ChurchManagerAuthorizationPolicy
from churchmanager_mode import load_config, resolve_database
from file_opening_policy import configure_churchmanager_file_opening
from login_dialog import authenticate_user
from churchmanager_version import __version__


assert_development_isolation(JSForm)


@dataclass
class Runtime:
    arguments: dict
    wx_app: object
    database: object
    main_form: object
    session: object | None = None
    authorization: object | None = None


def style_main_menu_headers(main_form):
    """Give every main-menu section a consistent, clearly visible heading."""
    descriptions = getattr(main_form, "CONTROLDESCRIPTION", {})
    controls = getattr(main_form, "CONTROLID", {})
    for name, description in descriptions.items():
        if description.get("type") != "StaticBox" or name not in controls:
            continue
        control = controls[name]
        font = control.GetFont()
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        font.SetPointSize(font.GetPointSize() + 2)
        control.SetFont(font)
        control.SetForegroundColour(wx.Colour(0, 72, 125))


def security_enabled(arguments, config=None):
    config = config or load_config()
    security = config.get("security", {})
    key = "testing_enabled" if arguments.get("test_mode") else "production_enabled"
    return bool(security.get(key, False))


def main_window_title(arguments):
    title = "ChurchManager {}".format(__version__)
    if arguments.get("test_mode"):
        return "{} - TEST MODE - {}".format(title, arguments["database"])
    return title


def build_runtime(form_class, argv=None, login_provider=authenticate_user):
    arguments = fnCMargParse.CMargs(
        prog="ChurchManager",
        description="ChurchManager {}".format(__version__),
        arguments=["server", "database", "user", "test_mode", "jsform_database"],
        argv=argv,
    )
    arguments = resolve_database(arguments)
    overlay_name = "TestScreenDefinitions" if arguments.get("test_mode") else "ScreenDefinitions"
    overlay = os.path.join(os.environ.get("LOCALAPPDATA", os.getcwd()), "ChurchManager", overlay_name)
    os.makedirs(overlay, exist_ok=True)
    os.environ["JSFORM_SCREEN_OVERLAY"] = overlay
    os.environ["JSFORM_DEFAULT_THEME"] = "churchmanager"
    wx_app = wx.App(0)
    JSForm.check_internetconnection(1)
    database = JSForm.clsDB(
        arguments["server"], arguments["database"], arguments["user"],
        arguments["password"], arguments["jsform_database"],
    )
    JSForm.CONFIG.set_Config_DBConnection(database)
    JSForm.OPTION.set_Option_DBConnection(database)
    JSForm.FONT.set_Font_DBConnection(database)
    JSForm.FONT.Get_Config_Font()
    configure_churchmanager_file_opening(JSForm, JSForm.CONFIG, os.path.dirname(__file__))
    JSForm.CONST.btnNavigationCONTROLS = JSForm.convertNavButtons(
        JSForm.CONST.btnNavigationCONTROLS
    )
    session = None
    authorization = None
    if security_enabled(arguments):
        session = login_provider(
            database.DBConnection,
            minimum_length=4 if arguments["test_mode"] else 12,
        )
        if session is None:
            database.DBConnection.close()
            database.JSConnection.close()
            wx_app.Destroy()
            raise SystemExit(0)
        authorization = ChurchManagerAuthorizationPolicy(session)
    main_form = form_class(
        None, database.DBConnection, "frmMain", ["Close"],
        authorization_policy=authorization,
    )
    style_main_menu_headers(main_form)
    main_form.FRAME.SetTitle(main_window_title(arguments))
    return Runtime(arguments, wx_app, database, main_form, session, authorization)
