"""Run source-level release safety checks that do not rebuild the installer."""

from __future__ import annotations

import ast
import argparse
import json
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent
EXCLUDED = {".git", ".runtime-venv", "build", "dist", "tmp"}


@dataclass(frozen=True)
class Finding:
    """Describe one source construct requiring release review."""

    path: Path
    line: int
    category: str
    detail: str


def python_files(root: Path = ROOT):
    """Yield maintained Python sources while excluding generated runtimes."""
    for path in root.rglob("*.py"):
        if not any(part in EXCLUDED for part in path.parts):
            yield path


def audit_source(root: Path = ROOT) -> list[Finding]:
    """Find shell execution and visibly interpolated SQL for manual review."""
    findings: list[Finding] = []
    for path in python_files(root):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
        except (OSError, SyntaxError, UnicodeError):
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            name = _call_name(node.func)
            if name in {"os.system", "subprocess.call", "subprocess.Popen", "subprocess.run"}:
                for keyword in node.keywords:
                    if keyword.arg == "shell" and isinstance(keyword.value, ast.Constant) and keyword.value.value is True:
                        findings.append(Finding(path, node.lineno, "shell", "shell=True"))
            if name.endswith(".execute") and node.args and isinstance(node.args[0], (ast.JoinedStr, ast.BinOp)):
                findings.append(Finding(path, node.lineno, "sql", "interpolated execute() SQL"))
    return findings


def _call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return f"{_call_name(node.value)}.{node.attr}".lstrip(".")
    return ""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-baseline", action="store_true")
    args = parser.parse_args()
    findings = audit_source()
    baseline_path = ROOT / "Documentation" / "release-source-audit-baseline.json"
    current = [
        {"path": str(item.path.relative_to(ROOT)).replace("\\", "/"),
         "line": item.line, "category": item.category, "detail": item.detail}
        for item in findings
    ]
    if args.write_baseline:
        baseline_path.write_text(json.dumps(current, indent=2) + "\n", encoding="utf-8")
        print(f"release_source_audit_baseline_written={len(current)}")
        return 0
    try:
        baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        baseline = []
    known = {(item["path"], item["line"], item["category"], item["detail"]) for item in baseline}
    unexpected = [item for item in current if (item["path"], item["line"], item["category"], item["detail"]) not in known]
    for item in unexpected:
        print(f"{item['category']}: {item['path']}:{item['line']}: {item['detail']}")
    print(f"release_source_audit_reviewed={len(current) - len(unexpected)}")
    print(f"release_source_audit_unexpected={len(unexpected)}")
    return 1 if unexpected else 0


if __name__ == "__main__":
    raise SystemExit(main())
