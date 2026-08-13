"""Windows single-instance guard scoped to this ChurchManager installation."""

from __future__ import annotations

import atexit
import ctypes
from ctypes import wintypes
import hashlib
from pathlib import Path


ERROR_ALREADY_EXISTS = 183


class ChurchManagerSingleInstance:
    def __init__(self, application_directory):
        identity = str(Path(application_directory).resolve()).casefold().encode("utf-8")
        suffix = hashlib.sha256(identity).hexdigest()[:16]
        self.name = f"Local\\ChurchManager-{suffix}"
        self.handle = None

    def acquire(self):
        if self.handle is not None:
            return True
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.CreateMutexW.argtypes = (wintypes.LPVOID, wintypes.BOOL, wintypes.LPCWSTR)
        kernel32.CreateMutexW.restype = wintypes.HANDLE
        handle = kernel32.CreateMutexW(None, False, self.name)
        if not handle:
            raise ctypes.WinError(ctypes.get_last_error())
        if ctypes.get_last_error() == ERROR_ALREADY_EXISTS:
            kernel32.CloseHandle(handle)
            return False
        self.handle = handle
        atexit.register(self.release)
        return True

    def release(self):
        if self.handle is None:
            return
        ctypes.WinDLL("kernel32", use_last_error=True).CloseHandle(self.handle)
        self.handle = None
