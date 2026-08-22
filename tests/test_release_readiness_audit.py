"""Tests for the non-packaging release safety audit."""

import tempfile
import unittest
from pathlib import Path

from release_readiness_audit import audit_source


class ReleaseReadinessAuditTests(unittest.TestCase):
    def test_flags_shell_and_interpolated_sql(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "unsafe.py").write_text(
                "import subprocess\n"
                "def run(cursor, value):\n"
                " subprocess.run('tool', shell=True)\n"
                " cursor.execute(f'SELECT {value}')\n",
                encoding="utf-8",
            )
            self.assertEqual({item.category for item in audit_source(root)}, {"shell", "sql"})

    def test_accepts_argument_lists_and_parameterized_sql(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "safe.py").write_text(
                "import subprocess\n"
                "def run(cursor, value):\n"
                " subprocess.run(['tool', value], check=True)\n"
                " cursor.execute('SELECT ?', (value,))\n",
                encoding="utf-8",
            )
            self.assertEqual(audit_source(root), [])
