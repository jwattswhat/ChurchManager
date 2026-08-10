"""Windows Credential Manager access for ChurchManager database logins."""

import ctypes
from ctypes import wintypes


CRED_TYPE_GENERIC = 1
CRED_PERSIST_LOCAL_MACHINE = 2


class CREDENTIAL(ctypes.Structure):
    _fields_ = [
        ("Flags", wintypes.DWORD),
        ("Type", wintypes.DWORD),
        ("TargetName", wintypes.LPWSTR),
        ("Comment", wintypes.LPWSTR),
        ("LastWritten", wintypes.FILETIME),
        ("CredentialBlobSize", wintypes.DWORD),
        ("CredentialBlob", ctypes.POINTER(ctypes.c_ubyte)),
        ("Persist", wintypes.DWORD),
        ("AttributeCount", wintypes.DWORD),
        ("Attributes", ctypes.c_void_p),
        ("TargetAlias", wintypes.LPWSTR),
        ("UserName", wintypes.LPWSTR),
    ]


PCREDENTIAL = ctypes.POINTER(CREDENTIAL)
_advapi32 = ctypes.WinDLL("Advapi32.dll", use_last_error=True)
_cred_write = _advapi32.CredWriteW
_cred_write.argtypes = [PCREDENTIAL, wintypes.DWORD]
_cred_write.restype = wintypes.BOOL
_cred_read = _advapi32.CredReadW
_cred_read.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, ctypes.POINTER(PCREDENTIAL)]
_cred_read.restype = wintypes.BOOL
_cred_free = _advapi32.CredFree
_cred_free.argtypes = [ctypes.c_void_p]


def write_credential(target, username, password):
    encoded = password.encode("utf-16-le")
    blob = (ctypes.c_ubyte * len(encoded)).from_buffer_copy(encoded)
    credential = CREDENTIAL()
    credential.Type = CRED_TYPE_GENERIC
    credential.TargetName = target
    credential.UserName = username
    credential.CredentialBlobSize = len(encoded)
    credential.CredentialBlob = ctypes.cast(blob, ctypes.POINTER(ctypes.c_ubyte))
    credential.Persist = CRED_PERSIST_LOCAL_MACHINE
    if not _cred_write(ctypes.byref(credential), 0):
        raise ctypes.WinError(ctypes.get_last_error())


def read_credential(target):
    pointer = PCREDENTIAL()
    if not _cred_read(target, CRED_TYPE_GENERIC, 0, ctypes.byref(pointer)):
        error = ctypes.get_last_error()
        if error == 1168:
            raise KeyError("No Windows credential is stored for {}".format(target))
        raise ctypes.WinError(error)
    try:
        credential = pointer.contents
        password = ctypes.string_at(
            credential.CredentialBlob, credential.CredentialBlobSize
        ).decode("utf-16-le")
        return credential.UserName, password
    finally:
        _cred_free(pointer)
