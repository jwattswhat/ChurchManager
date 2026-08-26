"""Contract tests for service-owned lectionary appointment snapshots."""

from pathlib import Path
import unittest

from unified_worship_service_dialog import UnifiedWorshipServiceRepository


class ServiceReadingSnapshotTests(unittest.TestCase):
    def test_common_reading_labels_map_to_neutral_roles(self):
        role = UnifiedWorshipServiceRepository._reading_role
        self.assertEqual(role("Old Testament"), "FIRST_READING")
        self.assertEqual(role("Epistle"), "SECOND_READING")
        self.assertEqual(role("Holy Gospel"), "GOSPEL")
        self.assertEqual(role("Psalm"), "PSALM_CANTICLE")
        self.assertEqual(role("Local reflection"), "")

    def test_snapshot_migration_owns_report_reading_view(self):
        sql = Path("migrations/077_add_service_reading_snapshots.sql").read_text(
            encoding="utf-8",
        )
        self.assertIn("CREATE TABLE IF NOT EXISTS tblServiceReadingSnapshot", sql)
        self.assertIn("ON DELETE CASCADE", sql)
        self.assertIn("ON DELETE SET NULL", sql)
        view = sql.split("rpt_worship_planner_reading", 1)[1]
        self.assertIn("FROM tblServiceReadingSnapshot", view)
        self.assertNotIn("JOIN tblReading", view)

    def test_save_replaces_snapshot_inside_existing_transaction(self):
        source = Path("unified_worship_service_dialog.py").read_text(encoding="utf-8")
        delete = source.index("DELETE FROM tblServiceReadingSnapshot")
        insert = source.index("INSERT INTO tblServiceReadingSnapshot")
        self.assertLess(delete, insert)
        self.assertIn("self._sync_reading_snapshots", source)


if __name__ == "__main__":
    unittest.main()
