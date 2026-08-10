"""ChurchManager application composition root."""

from dataclasses import dataclass

import wx
import JSForm

import fnCMargParse
from authorization import ChurchManagerAuthorizationPolicy
from churchmanager_mode import load_config, resolve_database
from login_dialog import authenticate_user


@dataclass
class Runtime:
    arguments: dict
    wx_app: object
    database: object
    main_form: object
    session: object | None = None
    authorization: object | None = None


def security_enabled(arguments, config=None):
    config = config or load_config()
    security = config.get("security", {})
    key = "testing_enabled" if arguments.get("test_mode") else "production_enabled"
    return bool(security.get(key, False))


def build_runtime(form_class, argv=None, login_provider=authenticate_user):
    arguments = fnCMargParse.CMargs(
        prog="ChurchManager",
        description="ChurchManager v.01",
        arguments=["server", "database", "user", "test_mode", "jsform_database"],
        argv=argv,
    )
    arguments = resolve_database(arguments)
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
    JSForm.CONST.btnNavigationCONTROLS = JSForm.convertNavButtons(
        JSForm.CONST.btnNavigationCONTROLS
    )
    session = None
    authorization = None
    if security_enabled(arguments):
        session = login_provider(database.DBConnection)
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
    if arguments["test_mode"]:
        main_form.FRAME.SetTitle(
            "ChurchManager - TEST MODE - {}".format(arguments["database"])
        )
    return Runtime(arguments, wx_app, database, main_form, session, authorization)
