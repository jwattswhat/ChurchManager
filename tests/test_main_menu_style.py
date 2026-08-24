"""Tests for the ChurchManager main-menu section heading treatment."""

import unittest
from unittest.mock import patch

from startup import style_main_menu_headers


class Font:
    def __init__(self, size=9): self.size = size; self.weight = None
    def SetWeight(self, value): self.weight = value
    def SetPointSize(self, value): self.size = value
    def GetPointSize(self): return self.size


class Control:
    def __init__(self): self.font = Font(); self.colour = None
    def GetFont(self): return self.font
    def SetFont(self, font): self.font = font
    def SetForegroundColour(self, colour): self.colour = colour


class MainMenuStyleTests(unittest.TestCase):
    def test_only_static_box_headers_are_enlarged_and_colored(self):
        box = Control(); link = Control()
        form = type("Form", (), {
            "CONTROLDESCRIPTION": {
                "PlanningBox": {"type": "StaticBox"},
                "lblService": {"type": "StaticText"},
            },
            "CONTROLID": {"PlanningBox": box, "lblService": link},
        })()
        with patch("startup.wx.Colour", return_value="section-blue"):
            style_main_menu_headers(form)
        self.assertEqual(box.font.size, 11)
        self.assertEqual(box.colour, "section-blue")
        self.assertEqual(link.font.size, 9)
        self.assertIsNone(link.colour)


if __name__ == "__main__": unittest.main()
