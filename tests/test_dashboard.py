import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'skills' / 'ob-methods-results-check' / 'scripts' / 'render_report.py'
SPEC = importlib.util.spec_from_file_location('audit_dashboard_renderer', SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class DashboardTests(unittest.TestCase):
    def test_explicit_counts_and_zero_counts(self):
        for label in ('合计', 'Total'):
            for counts in (['4', '8', '10', '22'], ['0', '0', '0', '0']):
                rendered = MODULE.render_dashboard(['P0', 'P1', 'P2', label], [counts])
                self.assertEqual(rendered.count('class="audit-metric"'), 4)
                self.assertIn(f'>{counts[-1]}</strong>', rendered)

    def test_reject_invalid_counts(self):
        for row in (['1', '2', '3', '7'], ['-1', '0', '0', '-1'], ['<script>', '0', '0', '0']):
            with self.assertRaises(ValueError):
                MODULE.render_dashboard(['P0', 'P1', 'P2', 'Total'], [row])

    def test_leave_other_tables_unchanged(self):
        document = '<html><head></head><body><table><tr><th>Outcome</th><td>1</td></tr></table></body></html>'
        self.assertEqual(MODULE.enhance_dashboard_tables(document), document)

    def test_preserve_pretty_doc_layout(self):
        document = '<html><head><title>Pretty Doc</title></head><body><aside>Contents</aside><table><thead><tr><th>P0</th><th>P1</th><th>P2</th><th>合计</th></tr></thead><tbody><tr><td>4</td><td>8</td><td>10</td><td>22</td></tr></tbody></table><p>Evidence</p></body></html>'
        result = MODULE.enhance_dashboard_tables(document)
        self.assertIn('<aside>Contents</aside>', result)
        self.assertIn('<p>Evidence</p>', result)
        self.assertEqual(result.count('class="audit-metric"'), 4)


if __name__ == '__main__':
    unittest.main()
