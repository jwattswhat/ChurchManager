from datetime import datetime, time, timedelta
from pathlib import Path
import unittest

from worship_scheduling import (
    AssignmentSuggestion, SchedulingSuggestionService, pattern_matches,
    required_position_rows, serialized_values, time_text,
)


ROOT = Path(__file__).resolve().parents[1]


class SuggestionRepository:
    def __init__(self):
        self.saved = []

    def service_context(self, service_id):
        return service_id, 1, datetime(2026, 8, 16, 9), 7, "Pentecost", "Sunday"

    def requirements(self, service_id):
        return [(1, 10, "Organist", 1), (2, 12, "Elder", 2)]

    def assignments(self, service_id):
        return [(5, 12, "Elder", 101, "Existing Elder", "ASSIGNED", "")]

    def eligible_candidates(self, role_id, starts_at, season):
        return {
            10: [(201, "Available Organist", 0)],
            12: [(101, "Existing Elder", 1), (202, "Second Elder", 0)],
        }[role_id]

    def save_assignment(self, *values):
        self.saved.append(values)


class WorshipSchedulingTests(unittest.TestCase):
    def test_serialized_legacy_values_accept_all_known_delimiters(self):
        self.assertEqual(serialized_values("1;3"), ["1", "3"])
        self.assertEqual(serialized_values("[Reader\rUsher\n]"), ["Reader", "Usher"])

    def test_time_text_accepts_native_time_and_database_timedelta(self):
        self.assertEqual(time_text(time(9, 30)), "09:30")
        self.assertEqual(time_text(timedelta(hours=11, minutes=15)), "11:15")

    def test_pattern_matching_allows_blank_filters_and_checks_specific_filters(self):
        service = datetime(2026, 8, 16, 9)
        self.assertTrue(pattern_matches((1, "Any", None, None, None, None), service, "Pentecost"))
        self.assertTrue(pattern_matches(
            (1, "Sunday", time(9), "Sunday", "August", "Pentecost"), service, "Pentecost"
        ))
        self.assertFalse(pattern_matches(
            (1, "Wrong time", time(10), "Sunday", "August", "Pentecost"), service, "Pentecost"
        ))

    def test_suggestions_preserve_existing_assignments_and_fill_only_missing_slots(self):
        suggestions = SchedulingSuggestionService(SuggestionRepository()).suggest(9)
        self.assertEqual(suggestions, [
            AssignmentSuggestion(10, "Organist", 201, "Available Organist"),
            AssignmentSuggestion(12, "Elder", 202, "Second Elder"),
        ])

    def test_declined_assignment_does_not_fill_a_required_position(self):
        repository = SuggestionRepository()
        repository.assignments = lambda _service_id: [
            (5, 12, "Elder", 101, "Existing Elder", "DECLINED", ""),
        ]
        suggestions = SchedulingSuggestionService(repository).suggest(9)
        self.assertEqual([item.participant for item in suggestions], [
            "Available Organist", "Second Elder",
        ])

    def test_required_position_rows_include_every_open_slot(self):
        rows = required_position_rows(
            [(1, 12, "Acolyte", 2)],
            [(5, 12, "Acolyte", 101, "Alex", "ASSIGNED", "")],
        )
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0][4][4], "Alex")
        self.assertIsNone(rows[1][4])

    def test_normalization_migration_preserves_optional_member_link_and_legacy_roles(self):
        sql = (ROOT / "migrations" / "041_normalize_worship_participants.sql").read_text(
            encoding="utf-8"
        )
        self.assertIn("ExternalParticipant", sql)
        self.assertIn("REFERENCES tblPerson(ID) ON DELETE SET NULL", (
            ROOT / "migrations" / "002_add_foreign_keys.sql"
        ).read_text(encoding="utf-8"))
        self.assertIn("(1,'Liturgist'", sql)
        self.assertIn("(10,'Organist'", sql)
        self.assertIn("(12,'Elder'", sql)
        self.assertIn("CREATE TABLE IF NOT EXISTS tblParticipantRole", sql)
        self.assertIn("CREATE TABLE IF NOT EXISTS tblParticipantAvailability", sql)
        self.assertIn("CREATE TABLE IF NOT EXISTS tblWorshipRoleRequirement", sql)

    def test_required_positions_are_strictly_attached_to_templates(self):
        source = (ROOT / "worship_scheduling.py").read_text(encoding="utf-8")
        migration = (ROOT / "migrations" / "043_require_template_for_participant_positions.sql").read_text(
            encoding="utf-8"
        )
        self.assertIn("if template_id is None:\n            return []", source)
        self.assertIn("BulletinOrderTemplateID int NOT NULL", migration)
        self.assertIn("r.BulletinOrderTemplateID=s.BulletinOrderTemplateID", migration)

    def test_template_editor_owns_requirements_and_custom_copies_inherit_them(self):
        dialog = (ROOT / "bulletin_order_dialog.py").read_text(encoding="utf-8")
        repository = (ROOT / "bulletin_orders.py").read_text(encoding="utf-8")
        migration = (ROOT / "migrations" / "044_attach_participant_positions_to_templates.sql").read_text(
            encoding="utf-8"
        )
        self.assertIn('("Positions...", self.on_required_positions)', dialog)
        self.assertIn("FROM tblWorshipRoleRequirement WHERE BulletinOrderTemplateID=?", repository)
        self.assertIn("DROP COLUMN ChurchID", migration)
        self.assertIn("(BulletinOrderTemplateID,WorshipRoleID)", migration)

    def test_required_position_dialog_can_manage_the_role_catalog(self):
        source = (ROOT / "worship_scheduling.py").read_text(encoding="utf-8")
        self.assertIn('label="Manage Positions..."', source)
        self.assertIn("dialog=RoleManagerDialog(self,self.repository)", source)
        self.assertIn("self._populate_positions(current)", source)

    def test_role_deletion_protects_positions_that_are_in_use(self):
        source = (ROOT / "worship_scheduling.py").read_text(encoding="utf-8")
        self.assertIn('("Delete Role",self.on_delete)', source)
        for table in (
            "tblParticipantRole", "tblParticipantAvailability",
            "tblWorshipRoleRequirement", "tblServiceRole",
        ):
            self.assertIn(f'("{table}"', source)
        self.assertIn("Edit the position and clear Active instead.", source)


if __name__ == "__main__":
    unittest.main()
