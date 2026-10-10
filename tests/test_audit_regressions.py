import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

SKILL = Path(__file__).parents[1] / 'skills' / 'ob-methods-results-check'
SPEC = importlib.util.spec_from_file_location('audit_renderer', SKILL / 'scripts/render_report.py')
RENDERER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RENDERER)


def calc(*args):
    return subprocess.run([sys.executable, str(SKILL / 'scripts/recalculate_reported_stats.py'), *map(str, args)], capture_output=True, text=True)


class AuditRegressionTests(unittest.TestCase):
    def test_headings_do_not_generate_readiness_or_resolution(self):
        for title in ('图文方向矛盾', 'P0-1 图文方向矛盾'):
            doc = RENDERER.build_document(RENDERER.render_markdown('# 审计\n## P0 issues\n### ' + title + '\nREVIEW_REQUIRED: example says CONFIRMED.'), '审计')
            self.assertNotIn('class="health-score"', doc)
            self.assertNotIn('class="evidence-pill', doc)
            self.assertNotIn('localStorage', doc)
            self.assertIn('REVIEW_REQUIRED: example says CONFIRMED.', doc)

    def test_scope_limitations_and_status_remain_verbatim(self):
        doc = RENDERER.build_document(RENDERER.render_markdown('# 审计\n**状态：** 尚未核实\n## 审计范围与局限\n缺少输出，可补充核查。'), '审计')
        self.assertIn('>审计范围与局限</h2>', doc)
        self.assertIn('<strong>状态：</strong> 尚未核实', doc)
        self.assertNotIn('无法修改', doc)

    def test_actual_moderator_probes(self):
        p = calc('first-stage-moderated-mediation', '--a', .2, '--interaction', .1, '--b', .5, '--moderator-low', 2, '--moderator-high', 4)
        self.assertEqual(p.returncode, 0, p.stderr)
        d = json.loads(p.stdout)
        self.assertAlmostEqual(d['result']['low_indirect_effect'], .2)
        self.assertAlmostEqual(d['result']['high_indirect_effect'], .3)
        self.assertIn('assumptions', d)

    def test_invalid_or_ambiguous_probes(self):
        base = ('first-stage-moderated-mediation', '--a', .2, '--interaction', .1, '--b', .5)
        for extra in [(), ('--moderator-low', 2), ('--moderator-low', 4, '--moderator-high', 2), ('--moderator-sd', 1, '--moderator-low', -1, '--moderator-high', 1)]:
            self.assertNotEqual(calc(*base, *extra).returncode, 0)

    def test_rounding_compatibility_is_not_exact_equality(self):
        base = ('mediation-product', '--a', .12, '--b', .23, '--a-decimals', 2, '--b-decimals', 2, '--reported-decimals', 2)
        for reported, expected in [(.03, True), (.05, False)]:
            p = calc(*base, '--reported', reported)
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertEqual(json.loads(p.stdout)['result']['rounding_compatible'], expected)

    def test_all_commands_describe_assumptions(self):
        for args in [('vif-from-r', '--r', .5), ('mediation-product', '--a', .2, '--b', .3), ('cfa-df', '--indicators', 8, '--factors', 2)]:
            p = calc(*args)
            d = json.loads(p.stdout)
            self.assertTrue(d.get('assumptions'))
            self.assertTrue(d.get('limitations'))

    def test_nonfinite_input_rejected(self):
        self.assertNotEqual(calc('mediation-product', '--a', 'nan', '--b', 1).returncode, 0)

if __name__ == '__main__':
    unittest.main()
