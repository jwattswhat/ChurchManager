"""Explicit runtime state for the ChurchManager desktop application."""

from dataclasses import dataclass


@dataclass
class ApplicationContext:
    """Own the authenticated services and runtime state for one app instance."""

    settings: dict
    database: object
    main_form: object | None = None
    form_factory: object | None = None
    services: object | None = None
    session: object | None = None
    authorization: object | None = None

    @property
    def connection(self):
        return self.database.DBConnection

    @property
    def test_mode(self):
        return bool(self.settings.get("test_mode"))
