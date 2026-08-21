"""Structural tests for the confidential contribution-batch entry dialogs."""

import inspect
import unittest

from giving import batch_dialog


class GivingBatchDialogTests(unittest.TestCase):
    def test_panel_owned_dialog_buttons_avoid_wx_parent_assertions(self):
        source = inspect.getsource(batch_dialog._dialog_buttons)
        self.assertIn("wx.Button(panel, wx.ID_OK)", source)
        self.assertIn("wx.Button(panel, wx.ID_CANCEL)", source)
        module_source = inspect.getsource(batch_dialog)
        self.assertNotIn("CreateStdDialogButtonSizer", module_source)

    def test_catalog_exposes_new_and_open_batch_actions(self):
        source = inspect.getsource(batch_dialog.BatchCatalogDialog)
        self.assertIn("New Batch", source)
        self.assertIn("Open Batch", source)
        self.assertIn("EVT_LIST_ITEM_ACTIVATED", source)

    def test_gift_entry_supports_envelope_resolution_and_split_allocations(self):
        source = inspect.getsource(batch_dialog.GiftDialog)
        self.assertIn("Anonymous / resolve from envelope", source)
        self.assertIn("Add Allocation", source)
        self.assertIn("Remove Allocation", source)
        self.assertIn("Statement treatment", source)

    def test_batch_editor_keeps_control_difference_visible(self):
        source = inspect.getsource(batch_dialog.BatchEditorDialog.refresh)
        self.assertIn("Control total", source)
        self.assertIn("Difference", source)
        self.assertIn("CalculatedTotal", inspect.getsource(batch_dialog.DraftBatchService))

    def test_review_action_is_permission_gated_and_explains_failures(self):
        source = inspect.getsource(batch_dialog.BatchEditorDialog)
        self.assertIn("Review / Mark Ready", source)
        self.assertIn("review.Enable(can_review)", source)
        self.assertIn("This batch is not ready", source)


if __name__ == "__main__":
    unittest.main()
