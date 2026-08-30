"""Database-mode selection and safety checks for ChurchManager."""

import json
from credential_store import read_credential
from configuration_paths import configuration_path, ensure_configuration


CONFIG_PATH = configuration_path()


def load_config(path=None):
    """Load the development or writable installed configuration."""

    selected = ensure_configuration(path or configuration_path())
    with selected.open("r", encoding="utf-8-sig") as config_file:
        return json.load(config_file)


def resolve_database(
    arguments, config=None, credential_reader=read_credential, *, resolve_credentials=True,
):
    """Return isolated connection settings, optionally resolving a credential now.

    Desktop composition roots use ``resolve_credentials=False`` and hand the
    protected target to JSForm. Maintenance tools may retain the established
    immediate-resolution behavior for the duration of their own operation.
    """
    config = config or load_config()
    resolved = dict(arguments)
    production_database = config["database_settings"].get("database", "ChurchDB")
    credential_target = config["database_settings"].get(
        "credential_target", "ChurchManager/Production"
    )
    if resolved.get("test_mode"):
        testing = config.get("testing", {})
        test_host = testing.get("host")
        if not test_host:
            raise RuntimeError("Test mode is not configured with a test database host.")
        resolved["server"] = test_host
        resolved["port"] = int(testing.get("port", 3306))
        test_database = testing.get("database")
        if not test_database:
            raise RuntimeError("Test mode is not configured with a test database.")
        if test_database.casefold() == production_database.casefold():
            raise RuntimeError("Safety stop: the test database matches the production database.")
        resolved["database"] = test_database
        credential_target = testing.get(
            "credential_target", "ChurchManager/Test"
        )
        resolved["user"] = resolved.get("user") or testing.get("user")
    else:
        resolved["server"] = resolved.get("server") or config["database_settings"].get(
            "host", "127.0.0.1"
        )
        resolved["port"] = int(config["database_settings"].get("port", 3306))
        resolved["database"] = resolved.get("database") or production_database
        resolved["user"] = resolved.get("user") or config["database_settings"].get("user")

    if resolve_credentials and not resolved.get("password"):
        stored_user, stored_password = credential_reader(credential_target)
        if resolved.get("user") and resolved["user"].casefold() != stored_user.casefold():
            raise RuntimeError("The configured database user does not match the stored credential.")
        resolved["user"] = stored_user
        resolved["password"] = stored_password
    elif not resolve_credentials:
        resolved.pop("password", None)
    resolved["credential_target"] = credential_target

    return resolved


def connection_arguments(arguments):
    """Build reusable command-line connection arguments for child programs."""
    result = [
        "--server", str(arguments["server"]),
        "--database", str(arguments["database"]),
    ]
    if arguments.get("user"):
        result.extend(["--user", str(arguments["user"])])
    if arguments.get("test_mode"):
        result.append("--test")
    return result
