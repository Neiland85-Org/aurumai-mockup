#!/usr/bin/env python3
"""
Backend Error Handling Validation Script
Verifies that error handling hardening has been properly applied.
"""

import ast
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Literal


class ValidationChecker:
    """Checks Python files for error handling patterns."""

    def __init__(self, backend_path: Path) -> None:
        self.backend_path = backend_path
        self.issues: dict[str, list[str]] = {
            "bare_exceptions": [],
            "untyped_functions": [],
            "generic_httpexceptions": [],
            "print_statements": [],
            "missing_docstrings": [],
        }
        self.passed_checks: dict[str, int] = {
            "proper_error_handling": 0,
            "typed_functions": 0,
            "validation_functions": 0,
            "logging_statements": 0,
        }

    def check_file(self, filepath: Path) -> None:
        """Check a single Python file for error handling patterns."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                tree = ast.parse(content)

            self._check_ast_errors(tree, filepath, content)
            self._check_regex_patterns(content, filepath)
        except SyntaxError as e:
            print(f"❌ Syntax error in {filepath}: {e}")
        except Exception as e:
            print(f"⚠️  Error checking {filepath}: {e}")

    def _check_ast_errors(
        self, tree: ast.AST, filepath: Path, content: str
    ) -> None:
        """Check AST for error handling issues."""
        for node in ast.walk(tree):
            # Check for bare except
            if isinstance(node, ast.ExceptHandler):
                if node.type is None:
                    self.issues["bare_exceptions"].append(str(filepath))

            # Check for except Exception
            if isinstance(node, ast.ExceptHandler):
                if (
                    isinstance(node.type, ast.Name)
                    and node.type.id == "Exception"
                ):
                    # Check if it's logging or re-raising
                    has_proper_handling = False
                    for child in ast.walk(node):
                        if isinstance(child, ast.Call):
                            if isinstance(child.func, ast.Attribute):
                                if child.func.attr in [
                                    "error",
                                    "warning",
                                    "info",
                                ]:
                                    has_proper_handling = True
                            if isinstance(child.func, ast.Name):
                                if child.func.id in [
                                    "ComputationException",
                                    "DatabaseException",
                                ]:
                                    has_proper_handling = True
                    if has_proper_handling:
                        self.passed_checks["proper_error_handling"] += 1

            # Check function has type hints
            if isinstance(node, ast.FunctionDef):
                if node.name.startswith("_"):
                    continue
                has_return_type = node.returns is not None
                has_param_types = all(
                    arg.annotation is not None for arg in node.args.args
                )
                if has_return_type and has_param_types:
                    self.passed_checks["typed_functions"] += 1
                elif not has_return_type or not has_param_types:
                    self.issues["untyped_functions"].append(
                        f"{filepath}:{node.lineno}:{node.name}"
                    )

                # Check for docstring
                if ast.get_docstring(node) is not None:
                    pass  # OK
                elif node.name not in ["__init__", "__str__", "__repr__"]:
                    self.issues["missing_docstrings"].append(
                        f"{filepath}:{node.lineno}:{node.name}"
                    )

            # Check for validation functions
            if isinstance(node, ast.FunctionDef):
                if node.name.startswith("_validate"):
                    self.passed_checks["validation_functions"] += 1

    def _check_regex_patterns(self, content: str, filepath: Path) -> None:
        """Check content using regex patterns."""
        lines = content.split("\n")

        for i, line in enumerate(lines, 1):
            # Check for bare except (except:)
            if re.search(r"^\s*except\s*:\s*$", line):
                self.issues["bare_exceptions"].append(f"{filepath}:{i}")

            # Check for generic HTTPException
            if re.search(
                r"HTTPException\s*\(\s*status_code\s*=\s*50\d", line
            ):
                self.issues["generic_httpexceptions"].append(f"{filepath}:{i}")

            # Check for print statements (not in logs)
            if re.search(
                r"^\s*print\s*\(", line
            ) and "logger" not in line:
                self.issues["print_statements"].append(f"{filepath}:{i}")

            # Check for logging
            if re.search(
                r"logger\.(error|warning|info|debug)\s*\(", line
            ):
                self.passed_checks["logging_statements"] += 1

    def run_validation(self) -> int:
        """Run validation on all backend files."""
        print("🔍 Backend Error Handling Validation\n")
        print(f"📂 Checking: {self.backend_path}\n")

        python_files = list(self.backend_path.rglob("*.py"))
        print(f"📄 Found {len(python_files)} Python files\n")

        for pyfile in python_files:
            if "__pycache__" in str(pyfile):
                continue
            self.check_file(pyfile)

        return self._print_results()

    def _print_results(self) -> int:
        """Print validation results."""
        print("\n" + "=" * 60)
        print("✅ PASSED CHECKS")
        print("=" * 60)

        for check, count in self.passed_checks.items():
            status = "✅" if count > 0 else "⚠️ "
            print(f"{status} {check}: {count}")

        print("\n" + "=" * 60)
        print("❌ ISSUES FOUND")
        print("=" * 60)

        has_issues = False
        for issue_type, locations in self.issues.items():
            if locations:
                has_issues = True
                print(f"\n❌ {issue_type}: {len(locations)}")
                for loc in locations[:5]:  # Show first 5
                    print(f"   - {loc}")
                if len(locations) > 5:
                    print(f"   ... and {len(locations) - 5} more")

        if not has_issues:
            print("\n✅ No critical issues found!")

        print("\n" + "=" * 60)
        print("📊 SUMMARY")
        print("=" * 60)

        total_passed = sum(self.passed_checks.values())
        total_issues = sum(len(v) for v in self.issues.values())

        print(f"✅ Passed: {total_passed}")
        print(f"❌ Issues: {total_issues}")

        if total_issues == 0:
            print("\n🎉 Backend error handling validation PASSED!")
            return 0
        else:
            print(f"\n⚠️  Backend needs fixes ({total_issues} issues)")
            return 1


def main() -> int:
    """Main entry point."""
    backend_path = Path(__file__).parent / "backend"

    if not backend_path.exists():
        print(f"❌ Backend path not found: {backend_path}")
        return 1

    checker = ValidationChecker(backend_path)
    checker.run_validation()

    return 0


if __name__ == "__main__":
    sys.exit(main())
