"""Tests for restricted pastoral-note encryption and key recovery."""

import base64
import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from pastoral_note_crypto import (
    PastoralKeyManager,
    PastoralNoteCipher,
    PastoralNoteCryptoError,
    PastoralRecoveryBackup,
    encrypted_note_values,
    pastoral_note_binding,
)


class MemoryCredentialStore:
    def __init__(self):
        self.values = {}

    def exists(self, target):
        return target in self.values

    def write(self, target, username, secret):
        self.values[target] = (username, secret)

    def read(self, target):
        if target not in self.values:
            raise KeyError(target)
        return self.values[target]


class PastoralNoteCryptoTests(unittest.TestCase):
    def setUp(self):
        self.store = MemoryCredentialStore()
        self.keys = PastoralKeyManager(self.store, "ChurchManager/Test/PastoralNotes")
        self.keys.provision()
        self.cipher = PastoralNoteCipher(self.keys)
        self.binding = pastoral_note_binding(1, 40, 12, 23)

    def test_note_round_trip_has_no_plaintext_database_field(self):
        note = "Hospital visit completed; follow up next week."
        encrypted = self.cipher.encrypt(note, self.binding)
        serialized = json.dumps(encrypted_note_values(encrypted))
        self.assertNotIn(note, serialized)
        self.assertEqual(self.cipher.decrypt(encrypted, self.binding), note)

    def test_unique_nonce_produces_different_ciphertext(self):
        first = self.cipher.encrypt("Brief factual note", self.binding)
        second = self.cipher.encrypt("Brief factual note", self.binding)
        self.assertNotEqual(first.nonce, second.nonce)
        self.assertNotEqual(first.ciphertext, second.ciphertext)

    def test_record_swap_fails_authentication(self):
        encrypted = self.cipher.encrypt("Restricted", self.binding)
        other = pastoral_note_binding(1, 41, 12, 23)
        with self.assertRaises(PastoralNoteCryptoError):
            self.cipher.decrypt(encrypted, other)

    def test_tampered_tag_fails_authentication(self):
        encrypted = self.cipher.encrypt("Restricted", self.binding)
        tag = bytearray(base64.b64decode(encrypted.authentication_tag))
        tag[0] ^= 1
        replacement = base64.b64encode(tag).decode("ascii")
        with self.assertRaises(PastoralNoteCryptoError):
            self.cipher.decrypt(replace(encrypted, authentication_tag=replacement), self.binding)

    def test_missing_key_fails_closed(self):
        encrypted = self.cipher.encrypt("Restricted", self.binding)
        missing = PastoralNoteCipher(
            PastoralKeyManager(MemoryCredentialStore(), "ChurchManager/Test/PastoralNotes")
        )
        with self.assertRaises(PastoralNoteCryptoError):
            missing.decrypt(encrypted, self.binding)

    def test_recovery_package_restores_key_to_new_machine(self):
        encrypted = self.cipher.encrypt("Restricted", self.binding)
        package = self.keys.create_recovery_package("correct horse battery staple")
        self.assertNotIn(self.keys.load_key().hex().encode("ascii"), package)

        restored_store = MemoryCredentialStore()
        restored = PastoralKeyManager(restored_store, "ChurchManager/Test/PastoralNotes")
        restored.restore_recovery_package(package, "correct horse battery staple")
        self.assertEqual(
            PastoralNoteCipher(restored).decrypt(encrypted, self.binding), "Restricted"
        )

    def test_wrong_recovery_password_does_not_install_key(self):
        package = self.keys.create_recovery_package("correct horse battery staple")
        restored_store = MemoryCredentialStore()
        restored = PastoralKeyManager(restored_store, "ChurchManager/Test/PastoralNotes")
        with self.assertRaises(PastoralNoteCryptoError):
            restored.restore_recovery_package(package, "this password is incorrect")
        self.assertEqual(restored_store.values, {})

    def test_tampered_recovery_package_does_not_install_key(self):
        package = json.loads(
            self.keys.create_recovery_package("correct horse battery staple").decode("utf-8")
        )
        package["key_version"] = 2
        restored_store = MemoryCredentialStore()
        restored = PastoralKeyManager(restored_store, "ChurchManager/Test/PastoralNotes")
        with self.assertRaises(PastoralNoteCryptoError):
            restored.restore_recovery_package(
                json.dumps(package).encode("utf-8"), "correct horse battery staple"
            )
        self.assertEqual(restored_store.values, {})

    def test_existing_different_key_is_not_replaced_implicitly(self):
        package = self.keys.create_recovery_package("correct horse battery staple")
        other_store = MemoryCredentialStore()
        other = PastoralKeyManager(other_store, "ChurchManager/Test/PastoralNotes")
        other.provision()
        with self.assertRaises(PastoralNoteCryptoError):
            other.restore_recovery_package(package, "correct horse battery staple")

    def test_short_recovery_password_is_rejected(self):
        with self.assertRaises(ValueError):
            self.keys.create_recovery_package("too short")

    def test_backup_sidecar_round_trip_validates_before_install(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            sql = root / "Manual.ChurchDBTest.Backup.SQL"
            sql.write_text("backup", encoding="utf-8")
            protected = root / "protected" / "pastoral-recovery.json"
            recovery = PastoralRecoveryBackup(self.keys, protected)
            recovery.create_protected_package("correct horse battery staple")
            sidecar = recovery.attach_to_backup(sql)
            self.assertEqual(sidecar, PastoralRecoveryBackup.sidecar_path(sql))

            restored_store = MemoryCredentialStore()
            restored = PastoralRecoveryBackup(
                PastoralKeyManager(restored_store, "ChurchManager/Test/PastoralNotes"),
                root / "replacement.json",
            )
            validated = restored.validate_restore(
                sql, "correct horse battery staple"
            )
            self.assertEqual(restored_store.values, {})
            restored.complete_restore(validated)
            self.assertEqual(
                PastoralNoteCipher(restored.key_manager).decrypt(
                    self.cipher.encrypt("Recovered", self.binding), self.binding
                ),
                "Recovered",
            )

    def test_missing_backup_sidecar_fails_before_restore(self):
        with tempfile.TemporaryDirectory() as folder:
            sql = Path(folder) / "backup.sql"
            sql.write_text("backup", encoding="utf-8")
            recovery = PastoralRecoveryBackup(
                self.keys, Path(folder) / "missing.json"
            )
            self.assertIsNone(
                recovery.validate_restore(sql, "correct horse battery staple")
            )


if __name__ == "__main__":
    unittest.main()
