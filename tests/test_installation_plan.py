import unittest

from installation_plan import (
    InstallationPlanError,
    InstallationRequest,
    build_installation_plan,
)
from installation_readiness import CatalogPackage, ReadinessReport


def package(family, code, dependency=None):
    return CatalogPackage(
        family, code, code.upper(), "1.0.0", None, True, True,
        "Validated.", dependency,
    )


class InstallationPlanTests(unittest.TestCase):
    def setUp(self):
        self.readiness = ReadinessReport((), (
            package("hymnal", "book"),
            package("lectionary", "cycle"),
            package("order_of_service", "service", "book"),
        ))

    def request(self, **changes):
        values = {
            "church_name": "Grace Lutheran Church",
            "database_name": "ChurchManager_Grace",
            "master_username": "administrator",
            "master_display_name": "Church Administrator",
            "hymnal_packages": ("book",),
            "lectionary_packages": ("cycle",),
            "order_of_service_packages": ("service",),
            "primary_hymnal": "book",
            "default_lectionary": "cycle",
        }
        values.update(changes)
        return InstallationRequest(**values)

    def test_builds_password_free_review_plan(self):
        plan = build_installation_plan(self.request(), self.readiness)
        self.assertEqual(plan.church_name, "Grace Lutheran Church")
        self.assertEqual(len(plan.selected_packages), 3)
        self.assertFalse(hasattr(plan, "password"))

    def test_none_is_allowed_for_every_catalog_family(self):
        plan = build_installation_plan(self.request(
            hymnal_packages=(), lectionary_packages=(),
            order_of_service_packages=(), primary_hymnal=None,
            default_lectionary=None,
        ), self.readiness)
        self.assertEqual(plan.selected_packages, ())

    def test_service_package_requires_selected_hymnal(self):
        with self.assertRaisesRegex(InstallationPlanError, "requires the hymnal"):
            build_installation_plan(self.request(
                hymnal_packages=(), primary_hymnal=None,
            ), self.readiness)

    def test_default_must_be_selected(self):
        with self.assertRaisesRegex(InstallationPlanError, "default lectionary"):
            build_installation_plan(self.request(
                lectionary_packages=(), default_lectionary="cycle",
            ), self.readiness)

    def test_rejects_unsafe_database_name(self):
        with self.assertRaisesRegex(InstallationPlanError, "Database name"):
            build_installation_plan(self.request(database_name="Church DB; DROP"), self.readiness)

    def test_host_must_be_ready(self):
        failed = ReadinessReport((type("Check", (), {"passed": False})(),), ())
        with self.assertRaisesRegex(InstallationPlanError, "prerequisites"):
            build_installation_plan(self.request(), failed)


if __name__ == "__main__":
    unittest.main()
