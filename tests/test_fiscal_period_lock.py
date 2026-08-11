from pathlib import Path
import unittest

from run_churchdb_migrations import statements


class FiscalPeriodLockTests(unittest.TestCase):
    def test_migration_parser_preserves_compound_trigger(self):
        source=(Path(__file__).parents[1]/"migrations"/"014_lock_used_fiscal_period_boundaries.sql").read_text(encoding="utf-8-sig")
        parsed=statements(source)
        self.assertEqual(len(parsed),1)
        self.assertIn("CREATE TRIGGER",parsed[0])
        self.assertIn("SIGNAL SQLSTATE",parsed[0])
        self.assertIn("END IF;",parsed[0])
    def test_lock_covers_posted_history_and_adopted_budgets(self):
        source=(Path(__file__).parents[1]/"migrations"/"014_lock_used_fiscal_period_boundaries.sql").read_text(encoding="utf-8-sig")
        for value in ("FiscalYearID","PeriodNumber","StartDate","EndDate","POSTED","REVERSED","ADOPTED"):
            self.assertIn(value,source)

if __name__=="__main__":unittest.main()
