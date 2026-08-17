"""Display ChurchManager installation readiness without changing the computer."""

from installation_readiness import inspect_readiness


def main():
    """Print host and package results for development and support."""
    report = inspect_readiness()
    print("ChurchManager installation readiness")
    for item in report.checks:
        label = "PASS" if item.passed else "NEEDS ATTENTION"
        print(f"[{label}] {item.message}")
    print("\nBundled catalog packages")
    if not report.packages:
        print("No optional catalog packages were found.")
    for item in report.packages:
        label = "AVAILABLE" if item.installable else "BLOCKED"
        print(f"[{label}] {item.family}: {item.title} {item.version} - {item.message}")
    print(f"\nhost_ready={'true' if report.ready else 'false'}")
    return 0 if report.ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
