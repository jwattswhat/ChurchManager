"""Reset only the localhost MariaDB root password using a guarded recovery start."""
from __future__ import annotations

import subprocess
import time
import traceback
from pathlib import Path

import mariadb

from credential_store import read_credential


SERVICE = "MariaDB"
SERVER = Path(r"C:\Program Files\MariaDB 12.1\bin\mysqld.exe")
CONFIG = Path(r"C:\Program Files\MariaDB 12.1\data\my.ini")
TARGET = "ChurchManager/LocalRestoreAdmin"
RECOVERY_LOG = Path(__file__).with_name("root-reset.mariadb.log")


def service_state():
    result = subprocess.run(["sc.exe", "query", SERVICE], capture_output=True, text=True, check=True)
    return "RUNNING" if "STATE" in result.stdout and "RUNNING" in result.stdout else "STOPPED"


def wait_for(state, seconds=30):
    deadline = time.time() + seconds
    while time.time() < deadline:
        if service_state() == state:
            return
        time.sleep(0.5)
    raise RuntimeError("MariaDB service did not reach {} state.".format(state.lower()))


def recovery_connection(seconds=30):
    deadline = time.time() + seconds
    last_error = None
    while time.time() < deadline:
        try:
            return mariadb.connect(host="127.0.0.1", port=3306, user="root", autocommit=True)
        except mariadb.Error as error:
            last_error = error
            time.sleep(0.5)
    raise RuntimeError("MariaDB recovery server did not accept a local connection.") from last_error


def main():
    username, password = read_credential(TARGET)
    if username != "root" or not password:
        raise RuntimeError("A new local MariaDB root password has not been stored securely.")
    if not SERVER.is_file() or not CONFIG.is_file():
        raise RuntimeError("The expected local MariaDB 12.1 installation was not found.")
    if service_state() != "RUNNING":
        raise RuntimeError("Safety stop: the normal MariaDB service was not running before reset.")
    recovery = None
    connection = None
    try:
        subprocess.run(["sc.exe", "stop", SERVICE], check=True, capture_output=True, text=True)
        wait_for("STOPPED")
        recovery = subprocess.Popen(
            [str(SERVER), "--defaults-file=" + str(CONFIG), "--skip-grant-tables",
             "--skip-networking=0", "--bind-address=127.0.0.1", "--port=3306",
             "--log-error=" + str(RECOVERY_LOG), "--console"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        connection = recovery_connection()
        cursor = connection.cursor()
        cursor.execute("FLUSH PRIVILEGES")
        cursor.execute("SELECT Host FROM mysql.user WHERE User='root' AND Host IN ('localhost','127.0.0.1')")
        hosts = [row[0] for row in cursor.fetchall()]
        if not hosts:
            raise RuntimeError("No local MariaDB root account was found.")
        for host in hosts:
            cursor.execute("ALTER USER 'root'@'{}' IDENTIFIED BY ?".format(host), (password,))
        cursor.close()
        connection.close(); connection = None
    finally:
        if connection is not None:
            connection.close()
        if recovery is not None and recovery.poll() is None:
            recovery.terminate()
            try:
                recovery.wait(timeout=15)
            except subprocess.TimeoutExpired:
                recovery.kill(); recovery.wait(timeout=5)
        if service_state() != "RUNNING":
            subprocess.run(["sc.exe", "start", SERVICE], check=True, capture_output=True, text=True)
            wait_for("RUNNING", 45)
    verified = mariadb.connect(host="127.0.0.1", port=3306, user="root", password=password)
    try:
        cursor = verified.cursor(); cursor.execute("SELECT 1"); cursor.fetchone(); cursor.close()
    finally:
        verified.close(); password = ""
    print("Local MariaDB root password reset and verified.")
    print("MariaDB Windows service restored to normal running mode.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        Path(__file__).with_name("root-reset.error.log").write_text(
            traceback.format_exc(), encoding="utf-8"
        )
        raise
