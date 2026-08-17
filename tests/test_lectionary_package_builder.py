"""Tests for provenance-gated lectionary package authoring."""

import unittest

from build_lectionary_package import build_package, validate_provenance
from lectionary_packages import LectionaryPackageError
try:
    from tests.test_lectionary_importer import valid_package
except ModuleNotFoundError:  # unittest discovery imports test modules at top level.
    from test_lectionary_importer import valid_package


def approval(package):
    return {
        "package_code": package["package_code"],
        "package_version": package["package_version"],
        "approval_status": "APPROVED", "reviewed_by": "Catalog reviewer",
        "reviewed_date": "2026-08-17", "source_owner": "Source owner",
        "redistribution_basis": "Written metadata permission",
        "distribution_scope": "REDISTRIBUTABLE", "metadata_only_confirmed": True,
        "notes": "",
    }


class LectionaryPackageBuilderTests(unittest.TestCase):
    def test_builder_replaces_checksum_and_returns_validated_package(self):
        draft = valid_package()
        draft["checksum"] = "wrong"
        package, summary = build_package(draft, approval(draft))
        self.assertEqual(len(package["checksum"]), 64)
        self.assertNotEqual(package["checksum"], "wrong")
        self.assertEqual(summary.package_code, "sample")
        self.assertEqual(package["distribution_scope"], "REDISTRIBUTABLE")

    def test_builder_embeds_local_only_scope_and_rejects_a_mismatch(self):
        package = valid_package()
        item = approval(package)
        item["distribution_scope"] = "LOCAL_ONLY"
        package.pop("distribution_scope")
        built, summary = build_package(package, item)
        self.assertEqual(built["distribution_scope"], "LOCAL_ONLY")
        self.assertEqual(summary.distribution_scope, "LOCAL_ONLY")

        package = valid_package()
        item = approval(package)
        item["distribution_scope"] = "LOCAL_ONLY"
        with self.assertRaisesRegex(LectionaryPackageError, "does not match"):
            build_package(package, item)

    def test_pending_or_unconfirmed_provenance_is_rejected(self):
        package = valid_package()
        for field, value in (("approval_status", "PENDING"),
                             ("metadata_only_confirmed", False)):
            with self.subTest(field=field):
                item = approval(package)
                item[field] = value
                with self.assertRaises(LectionaryPackageError):
                    validate_provenance(item, package)

    def test_provenance_cannot_authorize_another_version_or_package(self):
        package = valid_package()
        for field, value in (("package_code", "other"), ("package_version", "2.0")):
            with self.subTest(field=field):
                item = approval(package)
                item[field] = value
                with self.assertRaises(LectionaryPackageError):
                    validate_provenance(item, package)

    def test_unknown_provenance_fields_fail_closed(self):
        package = valid_package()
        item = approval(package)
        item["email_thread"] = "not package metadata"
        with self.assertRaisesRegex(LectionaryPackageError, "Unknown provenance field"):
            validate_provenance(item, package)


if __name__ == "__main__":
    unittest.main()
