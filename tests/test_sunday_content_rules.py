from datetime import date
import unittest

from sunday_content_rules import (
    ANNUAL_FIRST_SUNDAY, EVERY_SUNDAY, annual_date_rule, describe_rule,
    is_active, matches_rule, monthly_rule, next_occurrences,
    occurs_in_service_week, one_time_rule, parse_schedule, service_week,
)


class SundayContentRuleTests(unittest.TestCase):
    def test_monthly_sundays_have_a_natural_description_and_match_by_ordinal(self):
        rule = monthly_rule([1, 3])
        self.assertEqual(describe_rule(rule), "First and third Sundays of each month")
        self.assertTrue(matches_rule(rule, date(2026, 10, 18)))
        self.assertFalse(matches_rule(rule, date(2026, 10, 11)))

    def test_annual_calendar_date_is_not_limited_to_sunday(self):
        rule = annual_date_rule(10, 1)
        self.assertEqual(describe_rule(rule), "Every year on October 1")
        self.assertTrue(matches_rule(rule, date(2026, 10, 1)))
        self.assertFalse(matches_rule(rule, date(2026, 10, 2)))
        self.assertTrue(occurs_in_service_week(rule, date(2026, 9, 27)))
        self.assertTrue(occurs_in_service_week(rule, date(2026, 10, 3)))
        self.assertFalse(occurs_in_service_week(rule, date(2026, 10, 4)))

    def test_first_sunday_of_year(self):
        self.assertEqual(describe_rule(ANNUAL_FIRST_SUNDAY), "First Sunday of each year")
        self.assertTrue(matches_rule(ANNUAL_FIRST_SUNDAY, date(2027, 1, 3)))

    def test_one_time_and_date_boundaries(self):
        rule = one_time_rule(date(2026, 12, 25))
        self.assertEqual(describe_rule(rule), "Once on December 25, 2026")
        self.assertTrue(is_active(rule, date(2026, 12, 25)))
        self.assertFalse(is_active(EVERY_SUNDAY, date(2026, 8, 16), end_date=date(2026, 8, 15)))

    def test_controlled_natural_language_is_canonicalized(self):
        text, rule = parse_schedule(" first and third sindays of the month ")
        self.assertEqual(text, "First and third Sundays of each month")
        self.assertEqual(rule, "RRULE:FREQ=MONTHLY;BYDAY=1SU,3SU")
        self.assertEqual(describe_rule(rule), text)

    def test_fixed_holidays_are_supported(self):
        for phrase, expected, occurrence in (
            ("Every Christmas Eve", "Every Christmas Eve", date(2026, 12, 24)),
            ("Each Christmas Day", "Every Christmas Day", date(2026, 12, 25)),
            ("Annually on New Year's Day", "Every New Year's Day", date(2027, 1, 1)),
            ("Every New Year's Eve", "Every New Year's Eve", date(2026, 12, 31)),
        ):
            text, rule = parse_schedule(phrase)
            self.assertEqual(text, expected)
            self.assertTrue(matches_rule(rule, occurrence))

    def test_each_and_every_are_interchangeable(self):
        for each, every in (
            ("Each Sunday", "Every Sunday"),
            ("Each Christmas Eve", "Every Christmas Eve"),
            ("Each year on October 1", "Every year on October 1"),
        ):
            self.assertEqual(parse_schedule(each), parse_schedule(every))

    def test_first_sunday_strictly_after_fixed_date(self):
        text, rule = parse_schedule("The first Sunday after December 1")
        self.assertEqual(text, "First Sunday after December 1")
        self.assertTrue(matches_rule(rule, date(2026, 12, 6)))
        self.assertFalse(matches_rule(rule, date(2024, 12, 1)))
        self.assertTrue(matches_rule(rule, date(2024, 12, 8)))

    def test_first_sunday_after_fourth_of_july_aliases(self):
        expected = parse_schedule("First Sunday after the Fourth of July")
        self.assertEqual(expected[0], "First Sunday after the Fourth of July")
        self.assertEqual(parse_schedule("First Sunday after 4th of July"), expected)
        self.assertEqual(parse_schedule("First Sunday after Independence Day"), expected)
        self.assertTrue(matches_rule(expected[1], date(2026, 7, 5)))
        self.assertFalse(matches_rule(expected[1], date(2027, 7, 4)))
        self.assertTrue(matches_rule(expected[1], date(2027, 7, 11)))

    def test_movable_church_dates_are_rejected(self):
        for phrase in (
            "First Sunday of Pentecost", "Second Sunday in Advent", "Easter Day",
            "Ash Wednesday", "Palm Sunday",
        ):
            with self.assertRaisesRegex(ValueError, "movable-feast"):
                parse_schedule(phrase)

    def test_one_time_phrase_and_next_occurrences(self):
        text, rule = parse_schedule("Once on December 24, 2026")
        self.assertEqual(text, "Once on December 24, 2026")
        self.assertEqual(next_occurrences(rule, date(2026, 1, 1)), [date(2026, 12, 24)])

    def test_service_week_is_sunday_through_saturday(self):
        self.assertEqual(service_week(date(2026, 10, 1)), (date(2026, 9, 27), date(2026, 10, 3)))

    def test_migration_preserves_existing_monthly_checkbox_meaning(self):
        from pathlib import Path
        migration = (Path(__file__).resolve().parents[1] / "migrations" /
                     "045_add_natural_sunday_content_schedules.sql").read_text(encoding="utf-8")
        self.assertIn("MONTHLY_SUNDAYS:", migration)
        self.assertIn("rpt_sunday_prayer", migration)
        self.assertIn("rpt_sunday_announcement", migration)

    def test_generators_use_explicit_safe_views_and_shared_rules(self):
        from pathlib import Path
        root = Path(__file__).resolve().parents[1]
        for name, view in (
            ("rptPrayers.py", "rpt_sunday_prayer"),
            ("rptAnnouncement.py", "rpt_sunday_announcement"),
        ):
            source = (root / name).read_text(encoding="utf-8")
            self.assertIn(view, source)
            self.assertIn("occurs_in_service_week", source)
            self.assertNotIn("SELECT *", source)

    def test_editors_and_outputs_share_the_preview_workflow(self):
        from pathlib import Path
        root = Path(__file__).resolve().parents[1]
        dialog = (root / "sunday_content_dialog.py").read_text(encoding="utf-8")
        menu = (root / "main_menu.py").read_text(encoding="utf-8")
        self.assertIn("parse_schedule", dialog)
        self.assertNotIn("class ScheduleRuleDialog", dialog)
        self.assertNotIn("First Sunday\", \"Second Sunday", dialog)
        self.assertIn("class SundayContentPreviewDialog", dialog)
        self.assertIn('"lblPrayers", "lblAnnouncement"', menu)

    def test_legacy_checkbox_columns_and_forms_are_retired(self):
        from pathlib import Path
        root = Path(__file__).resolve().parents[1]
        migration = (root / "migrations" / "046_remove_legacy_sunday_checkbox_schedules.sql").read_text(
            encoding="utf-8"
        )
        for column in ("Continuous", "First", "Second", "Third", "Fourth", "Fifth"):
            self.assertIn(f"DROP COLUMN {column}", migration)
        self.assertFalse((root / "Forms" / "frmPrayer.json").exists())
        self.assertFalse((root / "Forms" / "frmAnnouncement.json").exists())

    def test_announcements_use_controlled_categories_without_display_only(self):
        from pathlib import Path
        root = Path(__file__).resolve().parents[1]
        migration = (root / "migrations" / "047_normalize_sunday_content_categories.sql").read_text(
            encoding="utf-8"
        )
        self.assertIn("ADD COLUMN IF NOT EXISTS AnnouncementCategory", migration)
        self.assertIn("DROP COLUMN IF EXISTS Label", migration)
        self.assertIn("DROP COLUMN IF EXISTS eDisplayOnly", migration)
        self.assertIn("tblChoices", migration)
        source = (root / "sunday_content_dialog.py").read_text(encoding="utf-8")
        self.assertIn('field = "PrayerCategory" if kind == "prayer" else "AnnouncementCategory"', source)
        self.assertNotIn("Electronic display only", source)

    def test_standard_schedule_migration_adds_text_and_converts_rules(self):
        from pathlib import Path
        migration = (Path(__file__).resolve().parents[1] / "migrations" /
                     "069_standardize_natural_language_schedules.sql").read_text(encoding="utf-8")
        self.assertIn("ScheduleText", migration)
        self.assertIn("RRULE:FREQ=WEEKLY;BYDAY=SU", migration)
        self.assertIn("RDATE:", migration)
        self.assertIn("rpt_sunday_prayer", migration)
        self.assertIn("rpt_sunday_announcement", migration)

    def test_choice_cleanup_removes_legacy_rows_and_adds_active_lists(self):
        from pathlib import Path
        root = Path(__file__).resolve().parents[1]
        migration = (root / "migrations" / "048_clean_and_complete_choices.sql").read_text(
            encoding="utf-8"
        )
        for obsolete in (
            "AccountType", "OrderofService", "PsalmorIntroit", "Roles", "EnteredBy", "GroupType",
        ):
            self.assertIn(obsolete, migration)
        for active in ("UsedAs", "AnnouncementCategory", "AddressLabel", "Reading", "Season", "Category"):
            self.assertIn(active, migration)
        self.assertIn("Hymn of Invocation", migration)
        self.assertIn("Hymn of the Day", migration)
        self.assertIn("Distribution Hymn", migration)

    def test_legacy_choice_screens_are_retired_and_person_lookups_are_relational(self):
        from pathlib import Path
        import json
        root = Path(__file__).resolve().parents[1]
        for retired in ("frmOS.json", "frmOSList.json", "frmParticipant.json"):
            self.assertFalse((root / "Forms" / retired).exists())
        for filename in ("frmPersonAddress.json",):
            document = json.loads((root / "Forms" / filename).read_text(encoding="utf-8"))
            form = next(iter(document.values()))
            lookup = form["CONTROLS"]["PersonID"]["lookupchoices"]
            self.assertEqual(lookup["name"], "tblPerson")
            self.assertEqual(lookup["fields"], ["ID", "LastName", "FirstName"])

    def test_choice_manager_is_safe_and_choice_fields_are_unique(self):
        from pathlib import Path
        root = Path(__file__).resolve().parents[1]
        migration = (root / "migrations" / "049_enforce_unique_choice_fields.sql").read_text(
            encoding="utf-8"
        )
        self.assertIn("UNIQUE (Field)", migration)
        menu = (root / "main_menu.py").read_text(encoding="utf-8")
        application = (root / "cm.py").read_text(encoding="utf-8")
        self.assertIn('"lblChoices"', menu)
        self.assertIn("show_choice_manager", application)
        self.assertIn('"AnnouncementCategory"', application)


if __name__ == "__main__":
    unittest.main()
