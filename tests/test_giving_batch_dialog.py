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
        self.assertIn('label="Contribution Batches"', source)
        self.assertNotIn('label="Draft Contribution Batches"', source)
        self.assertIn("New Batch", source)
        self.assertIn("Open Batch", source)
        self.assertIn("EVT_LIST_ITEM_ACTIVATED", source)

    def test_ready_batch_handoff_is_permission_gated_and_privacy_explained(self):
        source = inspect.getsource(batch_dialog.BatchCatalogDialog)
        self.assertIn("giving.batches.post", source)
        self.assertIn("Send Ready Batch to Accounting", source)
        self.assertIn("No donor or envelope details", source)

    def test_gift_entry_supports_envelope_resolution_and_split_allocations(self):
        source = inspect.getsource(batch_dialog.GiftDialog)
        self.assertIn("Anonymous / resolve from envelope", source)
        self.assertIn("Add Allocation", source)
        self.assertIn("Remove Allocation", source)
        self.assertIn("Statement treatment", source)

    def test_new_batch_refreshes_bank_accounts_with_organization(self):
        self.assertTrue(hasattr(batch_dialog.NewBatchDialog, "on_organization"))
        source = inspect.getsource(batch_dialog.NewBatchDialog.on_organization)
        self.assertIn("bank_accounts", source)

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

    def test_draft_gifts_support_double_click_edit_and_guarded_delete(self):
        source = inspect.getsource(batch_dialog.BatchEditorDialog)
        self.assertIn("EVT_LIST_ITEM_ACTIVATED", source)
        self.assertIn("Edit Contribution", source)
        self.assertIn("Delete Contribution", source)
        self.assertIn("YES_NO | wx.NO_DEFAULT", source)


if __name__ == "__main__":
    unittest.main()
