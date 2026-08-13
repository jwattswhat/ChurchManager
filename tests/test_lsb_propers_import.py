import unittest

from import_lsb_propers_from_production import SYSTEM_DEFINITIONS, SYSTEM_MAP, proper_key


class LSBPropersImportTests(unittest.TestCase):
    def test_legacy_cycles_map_to_one_normalized_three_year_system(self):
        names = {SYSTEM_MAP[code][0] for code in ("LCMS-A", "LCMS-B", "LCMS-C")}
        cycles = {SYSTEM_MAP[code][2] for code in ("LCMS-A", "LCMS-B", "LCMS-C")}
        self.assertEqual(len(names), 1)
        self.assertEqual(cycles, {"A", "B", "C"})
        self.assertEqual(next(iter(names)), "LSB Three-Year Lectionary")

    def test_one_year_festivals_and_occasions_remain_distinct(self):
        names = {SYSTEM_MAP[code][0] for code in ("LCMS-1", "LCMS-F", "LCMS-O")}
        self.assertEqual(len(names), 3)
        self.assertEqual(len(SYSTEM_DEFINITIONS), 4)

    def test_natural_key_is_case_insensitive_and_cycle_aware(self):
        self.assertEqual(
            proper_key("System", "A", "First Sunday"),
            proper_key("SYSTEM", "a", " first sunday "),
        )
        self.assertNotEqual(
            proper_key("System", "A", "First Sunday"),
            proper_key("System", "B", "First Sunday"),
        )

    def test_festival_identity_does_not_depend_on_reused_sort_values(self):
        self.assertNotEqual(
            proper_key("Festivals", None, "St. Mary Magdalene"),
            proper_key("Festivals", None, "St. James the Elder"),
        )


if __name__ == "__main__":
    unittest.main()
