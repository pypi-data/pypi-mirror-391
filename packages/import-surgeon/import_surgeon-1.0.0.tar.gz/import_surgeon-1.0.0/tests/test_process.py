#!/usr/bin/env python3
# tests/test_process.py

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from import_surgeon.modules.process import process_file


class TestProcess(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    # Test process_file updated
    def test_process_file_change(self):
        file_path = self.temp_path / "test.py"
        file_path.write_text("from old.mod import Symbol\n")
        migrations = [
            {"old_module": "old.mod", "new_module": "new.mod", "symbols": ["Symbol"]}
        ]
        changed, msg, detail = process_file(file_path, migrations, dry_run=True)
        self.assertTrue(changed)
        self.assertIn("CHANGES IN", msg)
        self.assertIn("diff", detail)
        self.assertEqual(detail["risk_level"], "low")

    def test_process_file_no_change(self):
        file_path = self.temp_path / "test.py"
        file_path.write_text("from new.mod import Symbol\n")
        migrations = [
            {"old_module": "old.mod", "new_module": "new.mod", "symbols": ["Symbol"]}
        ]
        changed, msg, detail = process_file(file_path, migrations, dry_run=True)
        self.assertFalse(changed)
        self.assertIn("UNCHANGED", msg)

    def test_process_file_apply_backup(self):
        file_path = self.temp_path / "test.py"
        file_path.write_text("from old.mod import Symbol\n")
        migrations = [
            {"old_module": "old.mod", "new_module": "new.mod", "symbols": ["Symbol"]}
        ]
        changed, msg, detail = process_file(
            file_path, migrations, dry_run=False, no_backup=False
        )
        self.assertTrue(changed)
        self.assertIn("MODIFIED", msg)
        self.assertIn("backup", detail)
        self.assertEqual(file_path.read_text(), "from new.mod import Symbol\n")

    def test_process_file_star_warning(self):
        file_path = self.temp_path / "test.py"
        file_path.write_text("from old.mod import *\n")
        migrations = [
            {"old_module": "old.mod", "new_module": "new.mod", "symbols": ["Symbol"]}
        ]
        changed, msg, detail = process_file(file_path, migrations, dry_run=True)
        self.assertTrue(changed)
        self.assertEqual(detail["risk_level"], "medium")
        self.assertIn("Handled wildcard import", detail["warnings"])

    def test_process_file_relative_skip(self):
        file_path = self.temp_path / "test.py"
        file_path.write_text("from .old import Symbol\n")
        migrations = [{"old_module": "old", "new_module": "new", "symbols": ["Symbol"]}]
        changed, msg, detail = process_file(file_path, migrations, dry_run=True)
        self.assertFalse(changed)
        self.assertIn("SKIPPED (relative)", msg)
        self.assertEqual(detail["risk_level"], "high")

    def test_process_file_dotted_warning(self):
        file_path = self.temp_path / "test.py"
        file_path.write_text("from old.mod import Symbol\nold.mod.Symbol\n")
        migrations = [
            {"old_module": "old.mod", "new_module": "new.mod", "symbols": ["Symbol"]}
        ]
        changed, msg, detail = process_file(file_path, migrations, dry_run=True)
        self.assertTrue(changed)
        self.assertEqual(detail["risk_level"], "high")
        self.assertIn(
            "Potential remaining dotted usages for Symbol: 1 instances",
            detail["warnings"],
        )

    def test_process_file_error(self):
        file_path = self.temp_path / "test.py"
        file_path.write_text("invalid syntax")
        migrations = [{"old_module": "old", "new_module": "new", "symbols": ["Symbol"]}]
        with patch("libcst.parse_module", side_effect=SyntaxError("invalid")):
            changed, msg, detail = process_file(file_path, migrations)
        self.assertFalse(changed)
        self.assertIn("ERROR", msg)
        self.assertIn("Error", detail["warnings"][0])

    def test_process_file_rewrite_dotted(self):
        file_path = self.temp_path / "test.py"
        file_path.write_text("a = old.mod.Symbol\n")
        migrations = [
            {"old_module": "old.mod", "new_module": "new.mod", "symbols": ["Symbol"]}
        ]
        changed, msg, detail = process_file(
            file_path, migrations, dry_run=False, rewrite_dotted=True
        )
        self.assertTrue(changed)
        self.assertIn("MODIFIED", msg)
        self.assertEqual(file_path.read_text(), "a = new.mod.Symbol\n")
        self.assertIn("Rewrote 1 dotted usages", detail["warnings"][0])
        self.assertEqual(detail["risk_level"], "medium")

    def test_process_file_multiple_migrations(self):
        file_path = self.temp_path / "test.py"
        file_path.write_text("from mod1 import Sym1\nfrom mod2 import Sym2\n")
        migrations = [
            {"old_module": "mod1", "new_module": "new1", "symbols": ["Sym1"]},
            {"old_module": "mod2", "new_module": "new2", "symbols": ["Sym2"]},
        ]
        changed, msg, detail = process_file(file_path, migrations, dry_run=False)
        self.assertTrue(changed)
        content = file_path.read_text()
        self.assertIn("from new1 import Sym1", content)
        self.assertIn("from new2 import Sym2", content)

    def test_process_file_format(self):
        file_path = self.temp_path / "test.py"
        file_path.write_text("from old.mod import Symbol\n")
        migrations = [
            {"old_module": "old.mod", "new_module": "new.mod", "symbols": ["Symbol"]}
        ]
        with patch("subprocess.run") as mock_run:
            changed, msg, detail = process_file(
                file_path, migrations, dry_run=False, do_format=True
            )
            self.assertTrue(changed)
            mock_run.assert_any_call(
                ["isort", "--quiet", "--atomic", str(file_path)],
                check=True,
                capture_output=True,
            )
            mock_run.assert_any_call(
                ["black", "--quiet", str(file_path)], check=True, capture_output=True
            )

    def test_process_file_format_fail(self):
        file_path = self.temp_path / "test.py"
        file_path.write_text("from old.mod import Symbol\n")
        migrations = [
            {"old_module": "old.mod", "new_module": "new.mod", "symbols": ["Symbol"]}
        ]
        with patch("subprocess.run", side_effect=Exception("fail")):
            changed, msg, detail = process_file(
                file_path, migrations, dry_run=False, do_format=True
            )
            self.assertTrue(changed)
            self.assertIn("Formatting failed", detail["warnings"][0])

    # New test: Quiet mode not printing
    @patch("builtins.print")
    def test_process_file_quiet(self, mock_print):
        file_path = self.temp_path / "test.py"
        file_path.write_text("from old.mod import Symbol\n")
        migrations = [
            {"old_module": "old.mod", "new_module": "new.mod", "symbols": ["Symbol"]}
        ]
        changed, msg, detail = process_file(
            file_path, migrations, dry_run=True, quiet="all"
        )
        mock_print.assert_not_called()


if __name__ == "__main__":
    unittest.main()
