"""Compatibility functions for ChurchManager database credentials.

The reusable Windows Credential Manager implementation belongs to JSForm.
"""

from JSForm.credential_store import WindowsCredentialStore


_STORE = WindowsCredentialStore()


def write_credential(target, username, password):
    """Store a ChurchManager database credential securely in Windows."""
    return _STORE.write(target, username, password)


def read_credential(target):
    """Read a ChurchManager database credential from Windows."""
    return _STORE.read(target)


def delete_credential(target):
    """Remove one ChurchManager credential when setup rollback requires it."""
    return _STORE.delete(target)
