import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
ENV_SCRIPT = ROOT / "scripts" / "check_environment.py"
RENDER_SCRIPT = ROOT / "scripts" / "render_report.py"
STATS_SCRIPT = ROOT / "scripts" / "recalculate_reported_stats.py"
FIXTURE = ROOT / "tests" / "fixtures" / "sample-report.md"


class PortableWorkflowTests(unittest.TestCase):
    def test_scripts_run_from_outside_skill_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "audit.html"
            env_result = subprocess.run(
                [sys.executable, str(ENV_SCRIPT)],
                cwd=tmp,
                capture_output=True,
                text=True,
                check=True,
            )
            render_result = subprocess.run(
                [sys.executable, str(RENDER_SCRIPT), str(FIXTURE), "--output", str(output)],
                cwd=tmp,
                capture_output=True,
                text=True,
                check=True,
            )
            stats_result = subprocess.run(
                [sys.executable, str(STATS_SCRIPT), "vif-from-r", "--r", "0.95"],
                cwd=tmp,
                capture_output=True,
                text=True,
                check=True,
            )
            self.assertTrue(output.exists())

        self.assertIn("pdf_page_rendering", json.loads(env_result.stdout))
        self.assertIn(str(output), render_result.stdout)
        self.assertAlmostEqual(
            json.loads(stats_result.stdout)["result"]["vif"],
            10.256410256410254,
        )

    def test_environment_detector_reports_missing_optional_tools(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = os.environ.copy()
            env["PATH"] = tmp
            result = subprocess.run(
                [sys.executable, str(ENV_SCRIPT)],
                cwd=tmp,
                env=env,
                capture_output=True,
                text=True,
                check=True,
            )

        report = json.loads(result.stdout)
        self.assertFalse(report["pdf_text_extraction"]["available"])
        self.assertFalse(report["pdf_page_rendering"]["available"])
        self.assertFalse(report["html_open"]["available"])


if __name__ == "__main__":
    unittest.main()
