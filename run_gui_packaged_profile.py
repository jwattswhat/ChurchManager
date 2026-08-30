"""Verify the current bundle and guard optional native packaged GUI automation."""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import secrets
import subprocess
import time
from tempfile import TemporaryDirectory

from credential_store import read_credential
from authentication import PasswordService


ROOT = Path(__file__).resolve().parent
BUNDLE = ROOT / "dist" / "ChurchManagerBundle" / "ChurchManager.exe"
OUTPUT = ROOT / ".gui-test-artifacts" / "packaged-profile.json"
PACKAGE_CHECK = ROOT / ".gui-test-artifacts" / "packaged-package-check.json"
OPT_IN = "CHURCHMANAGER_GUI_PACKAGED"
INTERACTIVE = "CHURCHMANAGER_GUI_INTERACTIVE"
LOGIN_TITLE = "ChurchManager Login"
MAIN_TITLE_RE = r"ChurchManager .* - TEST MODE - ChurchDBTest"
PROJECTS_TITLE = "Projects and Scheduling"


def packaged_test_config(path):
    """Write a non-secret, test-only packaged configuration."""
    data = {
        "database_settings": {
            "host": "127.0.0.1", "port": 3306, "user": "",
            "database": "ChurchDB", "credential_target": "ChurchManager/Production",
        },
        "testing": {
            "host": "127.0.0.1", "port": 3306, "database": "ChurchDBTest",
            "credential_target": "ChurchManager/LocalTestAdmin",
        },
        "security": {"production_enabled": False, "testing_enabled": True},
    }
    target = Path(path)
    target.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return target


def create_temporary_login(database_username, database_password):
    """Create one fictional application login in local ChurchDBTest."""
    import mariadb

    connection = mariadb.connect(
        host="127.0.0.1", port=3306, database="ChurchDBTest",
        user=database_username, password=database_password, autocommit=False,
    )
    username = "gui_test_" + secrets.token_hex(6)
    password = secrets.token_urlsafe(24)
    cursor = connection.cursor()
    try:
        cursor.execute(
            "INSERT INTO tblUser (Username,DisplayName,PasswordHash,Active,"
            "MasterAdministrator,MustChangePassword) VALUES (?,?,?,1,1,0)",
            (username, "Fictional GUI Test User", PasswordService(minimum_length=4).hash(password)),
        )
        user_id = cursor.lastrowid
        cursor.execute("SELECT ID FROM tblRole WHERE Name='Master Administrator'")
        role = cursor.fetchone()
        if not role:
            raise RuntimeError("The test database has no Master Administrator role.")
        cursor.execute(
            "INSERT INTO tblUserRole (UserID,RoleID,AssignedByUserID) VALUES (?,?,?)",
            (user_id, role[0], user_id),
        )
        connection.commit()
        return connection, user_id, username, password
    except Exception:
        connection.rollback()
        connection.close()
        raise
    finally:
        cursor.close()


def remove_temporary_login(connection, user_id):
    """Remove the fictional packaged-test login and its authentication audit."""
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM tblSecurityAuditEvent WHERE UserID=?", (user_id,))
        cursor.execute("DELETE FROM tblUserRole WHERE UserID=?", (user_id,))
        cursor.execute("DELETE FROM tblUser WHERE ID=?", (user_id,))
        connection.commit()
    finally:
        cursor.close()
        connection.close()


def validate_executable(path):
    """Return the exact current bundle executable or reject an unsafe target."""
    candidate = Path(path).resolve()
    expected = BUNDLE.resolve()
    if candidate != expected:
        raise RuntimeError("Safety stop: packaged GUI testing requires the current bundle.")
    if "churchmanager-legacy" in {part.casefold() for part in candidate.parts}:
        raise RuntimeError("Safety stop: the Frozen application is outside test scope.")
    if not candidate.is_file():
        raise FileNotFoundError(f"Current bundle is unavailable: {candidate}")
    return candidate


def automation_readiness():
    """Return a non-secret reason when native login automation cannot run."""
    if importlib.util.find_spec("pywinauto") is None:
        return False, "The reviewed pywinauto test dependency is not installed."
    try:
        username, password = read_credential("ChurchManager/LocalTestAdmin")
    except KeyError:
        return False, "The configured LocalTestAdmin credential is unavailable."
    password = ""
    return bool(username), "" if username else "The protected test username is empty."


def run_native_smoke(executable, username, password, config_path):
    """Drive the guarded packaged login, read-only project screen, and exit."""
    from pywinauto import Desktop
    from pywinauto.application import Application

    variable = "CHURCHMANAGER_CONFIG"
    previous = os.environ.get(variable)
    os.environ[variable] = str(config_path)
    try:
        app = Application(backend="uia").start(
            f'"{executable}" --test', timeout=30,
        )
    finally:
        if previous is None:
            os.environ.pop(variable, None)
        else:
            os.environ[variable] = previous
    try:
        desktop = Desktop(backend="uia")
        login = desktop.window(title=LOGIN_TITLE)
        login.wait("visible enabled ready", timeout=30)
        login.child_window(title="Username", control_type="Edit").set_edit_text(username)
        login.child_window(title="Password", control_type="Edit").set_edit_text(password)
        login.child_window(title="OK", control_type="Button").click_input()
        main = desktop.window(title_re=MAIN_TITLE_RE)
        main.wait("visible enabled ready", timeout=45)
        if not main.is_visible():
            raise RuntimeError("The authenticated ChurchManager main window is unavailable.")
        high_value = "pending-interactive-button-verification"
        if os.environ.get(INTERACTIVE) == "1":
            print("Click Projects and Scheduling in the ChurchManager window.", flush=True)
            projects = Desktop(backend="win32").window(title_re=r".*Projects.*")
            projects.wait("visible enabled ready", timeout=120)
            projects.close()
            projects.wait_not("visible", timeout=15)
            high_value = "passed-interactive"
        else:
            projects_button = main.child_window(
                title=PROJECTS_TITLE, control_type="Button",
            )
            projects_button.set_focus()
            projects_button.type_keys("{ENTER}")
            projects = Desktop(backend="win32").window(title_re=r".*Projects.*")
            projects.wait("visible enabled ready", timeout=20)
            projects.close()
            projects.wait_not("visible", timeout=15)
            high_value = "passed-automated-keyboard"
        main.close()
        main.wait_not("visible", timeout=20)
        return "passed", high_value
    finally:
        try:
            if app.is_process_running():
                app.kill(soft=True)
                time.sleep(0.2)
        except Exception:
            pass


def main():
    """Run package proof, then gate native UI automation behind explicit readiness."""
    executable = validate_executable(BUNDLE)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [str(executable), "--package-check", str(PACKAGE_CHECK)],
        check=True, timeout=60,
    )
    proof = json.loads(PACKAGE_CHECK.read_text(encoding="utf-8"))
    if not proof.get("passed"):
        raise RuntimeError("The current packaged resource proof failed.")
    result = {
        "profile": "gui-packaged", "bundle": str(executable.relative_to(ROOT)),
        "package_check": "passed", "native_automation": "skipped",
    }
    if os.environ.get(OPT_IN) != "1":
        result["reason"] = f"Set {OPT_IN}=1 to request native UI automation."
    else:
        ready, reason = automation_readiness()
        if not ready:
            result["reason"] = reason
        else:
            database_username, database_password = read_credential(
                "ChurchManager/LocalTestAdmin"
            )
            connection = user_id = None
            password = ""
            with TemporaryDirectory(prefix="cm-packaged-gui-") as folder:
                config = packaged_test_config(Path(folder) / "churchmanager.json")
                try:
                    connection, user_id, username, password = create_temporary_login(
                        database_username, database_password,
                    )
                    native_status, high_value = run_native_smoke(
                        executable, username, password, config,
                    )
                    result["native_automation"] = native_status
                finally:
                    if connection is not None:
                        remove_temporary_login(connection, user_id)
                    password = ""
                    database_password = ""
            result["scenario"] = "temporary-login-projects-keyboard-exit"
            result["high_value_screen"] = high_value
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
