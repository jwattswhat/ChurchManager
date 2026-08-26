"""Framework-facing ChurchManager authorization policy and user session."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


class AuthorizationDenied(PermissionError):
    """Raised when the authenticated user may not perform an operation."""


@dataclass(frozen=True)
class UserSession:
    """Immutable identity and permission snapshot for one signed-in user."""

    user_id: int
    username: str
    display_name: str
    is_master: bool
    permissions: frozenset[str] = field(default_factory=frozenset)
    role_ids: frozenset[int] = field(default_factory=frozenset)
    login_at: datetime | None = None
    workstation: str | None = None
    must_change_password: bool = False


class ChurchManagerAuthorizationPolicy:
    """Answer permission questions for the current ChurchManager session."""

    def __init__(self, session: UserSession):
        if session is None:
            raise ValueError("ChurchManager requires an authenticated user session.")
        self.session = session

    def has_permission(self, permission_name: str | None) -> bool:
        if not permission_name:
            return False
        return self.session.is_master or permission_name in self.session.permissions

    def require(self, permission_name: str, operation: str | None = None) -> None:
        if not self.has_permission(permission_name):
            label = operation or permission_name
            raise AuthorizationDenied("You are not authorized to {}.".format(label))

    def can_open(self, permission_name: str | None) -> bool:
        return self.has_permission(permission_name)

    def can_create(self, permission_name: str | None) -> bool:
        return self.has_permission(permission_name)

    def can_update(self, permission_name: str | None) -> bool:
        return self.has_permission(permission_name)

    def can_delete(self, permission_name: str | None) -> bool:
        return self.has_permission(permission_name)

    def can_view_control(self, permission_name: str | None) -> bool:
        return self.has_permission(permission_name)

    def can_edit_control(self, permission_name: str | None) -> bool:
        return self.has_permission(permission_name)

    def can_invoke(self, permission_name: str | None) -> bool:
        return self.has_permission(permission_name)
