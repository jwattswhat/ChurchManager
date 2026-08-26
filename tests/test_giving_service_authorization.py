"""Direct-call authorization tests for the confidential Giving boundary."""

from datetime import date
import unittest

from authorization import AuthorizationDenied
from giving.accounting_handoff import GivingAccountingHandoff
from giving.annual_envelopes import AnnualEnvelopeAssignmentService, ASSIGN_NEW_SEQUENCE
from giving.batch_service import DraftBatchService
from giving.contributor_dialog import ContributorRepository
from giving.correction_service import PostedBatchCorrectionService
from giving.import_preview import ContributionImportPreviewService
from giving.import_service import ContributionImportService
from giving.purpose_dialog import PurposeRepository
from giving.report_service import GivingReportService


class DeniedAuthorization:
    """Record the requested operation and deny it before database access."""

    def __init__(self):
        self.calls = []

    def require(self, permission, operation=None):
        self.calls.append((permission, operation))
        raise AuthorizationDenied(operation or permission)


class BombConnection:
    """Fail if a denied operation reaches the database."""

    def cursor(self):
        raise AssertionError("authorization must be checked before database access")


class Store:
    def add(self, _path):
        raise AssertionError("authorization must be checked before evidence storage")


class GivingServiceAuthorizationTests(unittest.TestCase):
    def assert_denied(self, permission, operation):
        authorization = DeniedAuthorization()
        with self.assertRaises(AuthorizationDenied):
            operation(authorization)
        self.assertEqual(authorization.calls[0][0], permission)

    def test_contributor_and_purpose_services_fail_closed(self):
        self.assert_denied(
            "giving.contributors.manage",
            lambda auth: ContributorRepository(BombConnection(), auth).contributors(),
        )
        self.assert_denied(
            "giving.purposes.manage",
            lambda auth: PurposeRepository(BombConnection(), auth).organizations(),
        )
        self.assert_denied(
            "giving.contributors.manage",
            lambda auth: AnnualEnvelopeAssignmentService(
                BombConnection(), 3, auth
            ).preview(2027, ASSIGN_NEW_SEQUENCE),
        )

    def test_batch_entry_and_review_services_fail_closed(self):
        self.assert_denied(
            "giving.batches.enter",
            lambda auth: DraftBatchService(BombConnection(), 3, auth).catalog_batches(),
        )
        self.assert_denied(
            "giving.batches.review",
            lambda auth: DraftBatchService(BombConnection(), 3, auth).mark_ready(1),
        )
        self.assert_denied(
            "giving.batches.enter",
            lambda auth: ContributionImportPreviewService(
                BombConnection(), 1, 1, auth
            ).all("SELECT 1"),
        )
        self.assert_denied(
            "giving.batches.enter",
            lambda auth: ContributionImportService(
                BombConnection(), 3, auth, store=Store()
            ).import_draft(
                source_path="unused.csv", content=b"unused", mapping=None,
                preview_rows=(), church_id=1, organization_id=1,
                bank_account_id=1, deposit_date=date(2027, 1, 1),
                description="Denied import",
            ),
        )

    def test_posting_and_correction_services_fail_closed(self):
        self.assert_denied(
            "giving.batches.post",
            lambda auth: GivingAccountingHandoff(BombConnection(), 3, auth).send(1),
        )
        self.assert_denied(
            "giving.batches.post",
            lambda auth: PostedBatchCorrectionService(
                BombConnection(), 3, auth
            ).create(1, date(2027, 1, 1), "Denied correction"),
        )

    def test_report_read_models_fail_closed(self):
        cases = (
            ("giving.reports.summary", lambda service: service.batch_summary(
                date(2027, 1, 1), date(2027, 12, 31))),
            ("giving.history.view", lambda service: service.contributor_history(
                1, date(2027, 1, 1), date(2027, 12, 31))),
            ("giving.statements.generate", lambda service: service.statement_lines(
                1, date(2027, 1, 1), date(2027, 12, 31))),
            ("giving.reports.confidential", lambda service: service.envelope_assignments(2027)),
        )
        for permission, action in cases:
            with self.subTest(permission=permission):
                self.assert_denied(
                    permission,
                    lambda auth, action=action: action(
                        GivingReportService(BombConnection(), auth)
                    ),
                )


if __name__ == "__main__":
    unittest.main()
