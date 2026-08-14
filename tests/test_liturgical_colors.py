import unittest

from liturgical_colors import liturgical_color_hex


class TestLiturgicalColors(unittest.TestCase):
    def test_standard_and_alias_colors(self):
        self.assertEqual(liturgical_color_hex("Green"), "#2E7D32")
        self.assertEqual(liturgical_color_hex("Purple"), "#6A1B9A")
        self.assertEqual(liturgical_color_hex("White or Gold"), "#FFFFFF")

    def test_blank_and_unknown_colors_do_not_create_a_swatch(self):
        self.assertEqual(liturgical_color_hex(None), "")
        self.assertEqual(liturgical_color_hex(""), "")
        self.assertEqual(liturgical_color_hex("Seasonal"), "")


if __name__ == "__main__":
    unittest.main()
