import json
import subprocess
import sys
import unittest
from pathlib import Path


SCRIPT = (
    Path(__file__).parents[1]
    / "skills"
    / "ob-methods-results-audit"
    / "scripts"
    / "recalculate_reported_stats.py"
)


def run_cli(*args, expect_ok=True):
    result = subprocess.run(
        [sys.executable, str(SCRIPT), *map(str, args)],
        capture_output=True,
        text=True,
    )
    if expect_ok:
        if result.returncode != 0:
            raise AssertionError(result.stderr)
        return json.loads(result.stdout)
    return result


class RecalculateReportedStatsTests(unittest.TestCase):
    def test_proportion(self):
        data = run_cli("proportion", "--count", 106, "--total", 242)
        self.assertAlmostEqual(data["result"]["proportion"], 106 / 242)

    def test_weighted_mean(self):
        data = run_cli("weighted-mean", "--group", "72:2.92", "--group", "74:4.82")
        self.assertAlmostEqual(data["result"]["weighted_mean"], (72 * 2.92 + 74 * 4.82) / 146)

    def test_pooled_t(self):
        data = run_cli(
            "pooled-t", "--n1", 146, "--m1", 5.27, "--sd1", 1.37,
            "--n2", 149, "--m2", 4.20, "--sd2", 1.86,
        )
        self.assertAlmostEqual(data["result"]["t"], 5.6166, places=3)
        self.assertAlmostEqual(data["result"]["f_equivalent"], data["result"]["t"] ** 2)

    def test_f_from_r2(self):
        data = run_cli("f-from-r2", "--r2", 0.19, "--n", 242, "--predictors", 6)
        self.assertAlmostEqual(data["result"]["f"], 9.18724, places=4)

    def test_r2_from_f(self):
        data = run_cli("r2-from-f", "--f", 8.80, "--n", 242, "--predictors", 6)
        self.assertAlmostEqual(data["result"]["r2"], 0.18346, places=4)

    def test_vif_from_r(self):
        data = run_cli("vif-from-r", "--r", 0.95)
        self.assertAlmostEqual(data["result"]["vif"], 10.25641, places=4)

    def test_mediation_product(self):
        data = run_cli("mediation-product", "--a", 0.32, "--b", 0.58)
        self.assertAlmostEqual(data["result"]["indirect_effect"], 0.1856)

    def test_first_stage_moderated_mediation(self):
        data = run_cli(
            "first-stage-moderated-mediation",
            "--a", 0.15, "--interaction", 0.12, "--b", 0.20, "--moderator-sd", 1.47,
        )
        result = data["result"]
        self.assertAlmostEqual(result["high_slope"], 0.3264)
        self.assertAlmostEqual(result["low_slope"], -0.0264)
        self.assertAlmostEqual(result["index"], 0.024)
        self.assertAlmostEqual(result["high_low_indirect_difference"], 0.07056)

    def test_cfa_df(self):
        data = run_cli("cfa-df", "--indicators", 38, "--factors", 7)
        self.assertEqual(data["result"]["df"], 644)

    def test_invalid_total_returns_nonzero(self):
        result = run_cli("proportion", "--count", 1, "--total", 0, expect_ok=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("total must be greater than zero", result.stderr)


if __name__ == "__main__":
    unittest.main()
