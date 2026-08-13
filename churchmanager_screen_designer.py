"""ChurchManager authorization, storage, and audit boundary for screen design."""

import json
import os
from pathlib import Path
import shutil

import JSForm


ROOT = Path(__file__).resolve().parent
STARTERS = ROOT / "Forms"


def user_screen_directory(test_mode=False, local_app_data=None):
    base = Path(local_app_data or os.environ["LOCALAPPDATA"])
    return base / "ChurchManager" / ("TestScreenDefinitions" if test_mode else "ScreenDefinitions")


def ensure_user_screen(form_name, test_mode=False, local_app_data=None):
    starter = STARTERS / "{}.json".format(form_name)
    if not starter.is_file():
        raise FileNotFoundError("Starter screen definition not found: {}".format(form_name))
    target = user_screen_directory(test_mode, local_app_data) / starter.name
    if not target.is_file():
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.with_suffix(".json.tmp")
        shutil.copyfile(starter, temporary)
        temporary.replace(target)
    JSForm.ScreenDefinitionLoader().load(target)
    return target


def security_audit_hook(connection, session):
    marker = "%s" if connection.__class__.__module__.startswith("mysql.connector") else "?"

    def audit(action, filename, detail=None):
        cursor = connection.cursor()
        try:
            sql = (
                "INSERT INTO tblSecurityAuditEvent "
                "(UserID,SessionID,Action,EntityType,EntityID,FormName,AfterJSON,Workstation) "
                "VALUES (?,? ,?,'SCREEN_DEFINITION',?,?,?,?)"
            ).replace("?", marker)
            cursor.execute(
                sql,
                (
                    session.user_id, None, action,
                    filename, Path(filename).stem,
                    json.dumps({"detail": detail}, separators=(",", ":")) if detail else None,
                    session.workstation,
                ),
            )
            connection.commit()
        finally:
            cursor.close()
    return audit


def open_churchmanager_screen_designer(connection, session, authorization, test_mode=False, local_app_data=None):
    authorization.require("screens.design", "Open Screen Designer")
    user_directory = user_screen_directory(test_mode, local_app_data)
    user_directory.mkdir(parents=True, exist_ok=True)
    os.environ["JSFORM_SCREEN_OVERLAY"] = str(user_directory)
    audit = security_audit_hook(connection, session)

    def open_entry(entry):
        authorization.require("screens.design", "Design {}".format(entry["name"]))
        path = ensure_user_screen(entry["name"], test_mode, local_app_data)
        audit("SCREEN_DESIGN_OPENED", path.name)
        JSForm.open_screen_designer(
            path,
            starter_definition_path=entry["starter"],
            allowed_directory=user_directory,
            audit_hook=audit,
        )

    return JSForm.open_screen_catalog(user_directory, STARTERS, open_entry)
