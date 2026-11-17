import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from panel import INVESTORS, enrich_report, export_zip, skill_checks, synthesize


class PanelContract(unittest.TestCase):
    def setUp(self):
        self.report = json.loads((ROOT / 'examples/COST_report.json').read_text())
        self.memos = {k: (ROOT / f'examples/COST_{k}_memo.md').read_text() for k in INVESTORS}

    def test_cost_revised_threshold_and_unknown_rd(self):
        r = self.report
        self.assertEqual(r['summary']['revenue_cagr']['display'], '7.51%')
        self.assertEqual(list(r['panel_checks']['wood'].values()), ['pass', 'not known'])
        self.assertEqual(list(r['panel_checks']['burry'].values()), ['pass', 'pass'])
        self.assertTrue(all(v == 'pass' for v in r['panel_checks']['buffett'].values()))
        self.assertIsNone(r['rows'][-1]['metrics']['research_and_development']['value'])

    def test_growth_exact_boundary_and_missing_window(self):
        r = copy.deepcopy(self.report)
        r['rows'][0]['metrics']['revenue']['value'] = 100_000_000
        r['rows'][-1]['metrics']['revenue']['value'] = 121_550_625
        self.assertEqual(skill_checks('wood', r)['Revenue CAGR at least 5%'], 'pass')
        r['rows'][-1]['metrics']['revenue']['value'] -= 1
        self.assertEqual(skill_checks('wood', r)['Revenue CAGR at least 5%'], 'fail')
        r['rows'].pop(2)
        self.assertEqual(skill_checks('wood', r)['Revenue CAGR at least 5%'], 'not known')

    def test_rd_exact_boundary_and_mismatched_periods(self):
        r = copy.deepcopy(self.report)
        m = r['rows'][-1]['metrics']
        m['revenue']['value'] = 100
        m['research_and_development'] = copy.deepcopy(m['revenue'])
        m['research_and_development']['value'] = 5
        self.assertEqual(list(skill_checks('wood', r).values())[-1], 'pass')
        m['research_and_development']['value'] = 4.999999
        self.assertEqual(list(skill_checks('wood', r).values())[-1], 'fail')
        m['research_and_development']['sources'][0]['start'] = '1900-01-01'
        self.assertEqual(list(skill_checks('wood', r).values())[-1], 'not known')

    def test_burry_boundaries_missing_and_bad_equity(self):
        r = copy.deepcopy(self.report)
        m = r['rows'][-1]['metrics']
        m['liabilities']['value'], m['equity']['value'] = 200, 100
        self.assertEqual(list(skill_checks('burry', r).values())[-1], 'pass')
        m['liabilities']['value'] = 200.00001
        self.assertEqual(list(skill_checks('burry', r).values())[-1], 'fail')
        for eq in (0, -100, None):
            m['equity']['value'] = eq
            self.assertEqual(list(skill_checks('burry', r).values())[-1], 'not known')
        for row in r['rows']:
            row['metrics']['operating_cash_flow']['value'] = row['metrics']['net_income']['value']
        self.assertEqual(list(skill_checks('burry', r).values())[0], 'pass')
        r['rows'][1]['metrics']['operating_cash_flow']['value'] -= 1
        self.assertEqual(list(skill_checks('burry', r).values())[0], 'fail')
        r['rows'][1]['metrics']['net_income']['value'] = None
        self.assertEqual(list(skill_checks('burry', r).values())[0], 'not known')

    def test_memos_and_aggregate_audit(self):
        result = synthesize(self.report, self.memos)
        self.assertTrue(result['audit_valid'])
        self.assertFalse(result['unprinted_number_flag'])
        self.assertEqual(result['verdicts']['wood'], 'watch it')
        self.assertEqual(result['decision'], 'own the business')
        self.memos['wood'] += '\nInvented growth: 99.123%.\n'
        result = synthesize(self.report, self.memos)
        self.assertTrue(result['unprinted_number_flag'])
        self.assertFalse(result['audit_valid'])
        self.assertEqual(result['decision'], 'watch it')

    def test_stale_missing_citation_and_invalid_decision_block_synthesis(self):
        for mutation in ('stale', 'missing', 'citation', 'decision', 'malformed decision'):
            memos = self.memos.copy()
            if mutation == 'stale':
                memos['burry'] = memos['burry'].replace(self.report['snapshot_id'], 'old')
            elif mutation == 'missing':
                memos['burry'] = ''
            elif mutation == 'citation':
                memos['burry'] += '\n[Claim](https://example.org/unprovided)'
            elif mutation == 'decision':
                memos['burry'] += '\nDecision: pass\n'
            else:
                memos['burry'] += '\nDecision: definitely buy\n'
            self.assertFalse(synthesize(self.report, memos)['audit_valid'], mutation)

    def test_snapshot_binds_evidence(self):
        before = enrich_report(self.report)
        changed = copy.deepcopy(self.report)
        changed['evidence'][0]['passages'].append('Changed qualitative context')
        self.assertNotEqual(before['snapshot_id'], enrich_report(changed)['snapshot_id'])

    def test_zip_contains_each_skill_and_packet(self):
        import io
        import zipfile
        with zipfile.ZipFile(io.BytesIO(export_zip(self.report, self.memos))) as z:
            for key in INVESTORS:
                self.assertIn(f'{key}_memo_packet.md', z.namelist())
                self.assertIn(f'{key}_memo.md', z.namelist())
            self.assertIn('panel.py', z.namelist())
            self.assertEqual(len([p for p in z.namelist() if p.endswith('SKILL.md')]), 3)
