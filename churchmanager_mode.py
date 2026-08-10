"""Database-mode selection and safety checks for ChurchManager."""

import json
from pathlib import Path
from credential_store import read_credential


CONFIG_PATH = Path(__file__).with_name("churchmanager.json")


def load_config(path=CONFIG_PATH):
    with open(path, "r", encoding="utf-8-sig") as config_file:
        return json.load(config_file)


def resolve_database(arguments, config=None, credential_reader=read_credential):
    """Return effective connection arguments, enforcing test isolation."""
    config = config or load_config()
    resolved = dict(arguments)
    production_database = config["database_settings"].get("database", "ChurchDB")
    production_jsform = config["database_settings"].get("jsform_database", "JSForm")
    credential_target = config["database_settings"].get(
        "credential_target", "ChurchManager/Production"
    )

    if resolved.get("test_mode"):
        test_database = config.get("testing", {}).get("database")
        if not test_database:
            raise RuntimeError("Test mode is not configured with a test database.")
        if test_database.casefold() == production_database.casefold():
            raise RuntimeError("Safety stop: the test database matches the production database.")
        test_jsform = config.get("testing", {}).get("jsform_database")
        if not test_jsform:
            raise RuntimeError("Test mode is not configured with a JSForm test database.")
        if test_jsform.casefold() == production_jsform.casefold():
            raise RuntimeError("Safety stop: the JSForm test database matches production.")
        resolved["database"] = test_database
        resolved["jsform_database"] = test_jsform
        credential_target = config.get("testing", {}).get(
            "credential_target", "ChurchManager/Test"
        )
    else:
        resolved["jsform_database"] = resolved.get("jsform_database") or production_jsform

    if not resolved.get("password"):
        stored_user, stored_password = credential_reader(credential_target)
        if resolved.get("user") and resolved["user"].casefold() != stored_user.casefold():
            raise RuntimeError("The configured database user does not match the stored credential.")
        resolved["user"] = stored_user
        resolved["password"] = stored_password
    resolved["credential_target"] = credential_target

    return resolved


def connection_arguments(arguments):
    """Build reusable command-line connection arguments for child programs."""
    result = [
        "--server", str(arguments["server"]),
        "--database", str(arguments["database"]),
        "--user", str(arguments["user"]),
        "--jsform-database", str(arguments["jsform_database"]),
    ]
    if arguments.get("test_mode"):
        result.append("--test")
    return result
