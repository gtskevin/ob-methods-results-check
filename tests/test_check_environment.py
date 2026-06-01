import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).parents[1]
SCRIPT = ROOT / "scripts" / "check_environment.py"
SPEC = importlib.util.spec_from_file_location("check_environment", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class CheckEnvironmentTests(unittest.TestCase):
    def test_detect_tool_reports_available_path(self):
        with patch.object(MODULE.shutil, "which", return_value="/usr/local/bin/pdftotext"):
            self.assertEqual(
                MODULE.detect_tool("pdftotext"),
                {"available": True, "path": "/usr/local/bin/pdftotext"},
            )

    def test_detect_tool_reports_missing_tool(self):
        with patch.object(MODULE.shutil, "which", return_value=None):
            self.assertEqual(MODULE.detect_tool("pdftoppm"), {"available": False, "path": None})

    def test_detect_html_open_uses_open_on_macos(self):
        with (
            patch.object(MODULE.sys, "platform", "darwin"),
            patch.object(MODULE.shutil, "which", return_value="/usr/bin/open") as which,
        ):
            self.assertEqual(
                MODULE.detect_html_open(),
                {
                    "available": True,
                    "strategy": "argv",
                    "command": "open",
                    "path": "/usr/bin/open",
                    "argv_prefix": ["/usr/bin/open"],
                },
            )
        which.assert_called_once_with("open")

    def test_detect_html_open_prefers_xdg_open(self):
        with (
            patch.object(MODULE.sys, "platform", "linux"),
            patch.object(MODULE.shutil, "which", return_value="/usr/bin/xdg-open") as which,
        ):
            self.assertEqual(
                MODULE.detect_html_open(),
                {
                    "available": True,
                    "strategy": "argv",
                    "command": "xdg-open",
                    "path": "/usr/bin/xdg-open",
                    "argv_prefix": ["/usr/bin/xdg-open"],
                },
            )
        which.assert_called_once_with("xdg-open")

    def test_detect_html_open_falls_back_to_gio(self):
        def which(name):
            return "/usr/bin/gio" if name == "gio" else None

        with (
            patch.object(MODULE.sys, "platform", "linux"),
            patch.object(MODULE.shutil, "which", side_effect=which),
        ):
            self.assertEqual(
                MODULE.detect_html_open(),
                {
                    "available": True,
                    "strategy": "argv",
                    "command": "gio",
                    "path": "/usr/bin/gio",
                    "argv_prefix": ["/usr/bin/gio", "open"],
                },
            )

    def test_detect_html_open_reports_windows_startfile(self):
        with (
            patch.object(MODULE.sys, "platform", "win32"),
            patch.object(MODULE.shutil, "which") as which,
        ):
            self.assertEqual(
                MODULE.detect_html_open(),
                {
                    "available": True,
                    "strategy": "os.startfile",
                    "command": None,
                    "path": None,
                    "argv_prefix": [],
                },
            )
        which.assert_not_called()

    def test_detect_html_open_reports_missing_opener(self):
        with (
            patch.object(MODULE.sys, "platform", "linux"),
            patch.object(MODULE.shutil, "which", return_value=None),
        ):
            self.assertEqual(
                MODULE.detect_html_open(),
                {
                    "available": False,
                    "strategy": None,
                    "command": None,
                    "path": None,
                    "argv_prefix": [],
                },
            )

    def test_detect_html_open_reports_missing_opener_on_macos(self):
        with (
            patch.object(MODULE.sys, "platform", "darwin"),
            patch.object(MODULE.shutil, "which", return_value=None) as which,
        ):
            self.assertEqual(
                MODULE.detect_html_open(),
                {
                    "available": False,
                    "strategy": None,
                    "command": None,
                    "path": None,
                    "argv_prefix": [],
                },
            )
        which.assert_called_once_with("open")

    def test_build_report_has_stable_schema(self):
        missing_tool = {"available": False, "path": None}
        missing_open = {
            "available": False,
            "strategy": None,
            "command": None,
            "path": None,
            "argv_prefix": [],
        }
        with (
            patch.object(MODULE, "detect_tool", return_value=missing_tool),
            patch.object(MODULE, "detect_html_open", return_value=missing_open),
        ):
            report = MODULE.build_report()

        self.assertEqual(
            set(report),
            {"python", "pdf_text_extraction", "pdf_page_rendering", "html_open"},
        )
        self.assertEqual(set(report["python"]), {"available", "executable", "version"})
        self.assertTrue(report["python"]["available"])
        self.assertEqual(report["python"]["executable"], sys.executable)
        self.assertEqual(report["pdf_text_extraction"], missing_tool)
        self.assertEqual(report["pdf_page_rendering"], missing_tool)
        self.assertEqual(report["html_open"], missing_open)

    def test_cli_outputs_pretty_json(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            capture_output=True,
            text=True,
            check=True,
        )
        report = json.loads(result.stdout)
        self.assertTrue(report["python"]["available"])
        self.assertEqual(
            set(report["html_open"]),
            {"available", "strategy", "command", "path", "argv_prefix"},
        )
        self.assertIn('\n  "python": {', result.stdout)


if __name__ == "__main__":
    unittest.main()
