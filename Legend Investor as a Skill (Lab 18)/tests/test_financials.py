import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.agents/skills/buffett-business-review/scripts'))
from edgar import TAGS, calculate, select_fact, memo_packet, normalize_ticker
from memo_validation import audit_memo


def fixture():
    facts = {'cik': 1, 'facts': {'us-gaap': {}}}
    ends = [f'{y}-12-31' for y in range(2020, 2025)]
    for key, tags in TAGS.items():
        values = []
        for i, end in enumerate(ends):
            value = {'revenue': 500, 'net_income': 15, 'operating_cash_flow': 100+i*10,
                     'capital_spending': 20, 'equity': 100, 'liabilities': 40}[key]
            f = {'form': '10-K', 'start': end[:4]+'-01-01', 'end': end,
                 'filed': f'{int(end[:4])+1}-02-01', 'accn': f'0000000001-{end[2:4]}-000001', 'val': value}
            if key in ('equity', 'liabilities'):
                f.pop('start')
            values.append(f)
        facts['facts']['us-gaap'][tags[0]] = {'units': {'USD': values}}
    return facts, ends


class FinancialContract(unittest.TestCase):
    def test_years_and_exact_checks(self):
        f, ends = fixture()
        rows, checks = calculate(f, list(reversed(ends)))
        self.assertEqual([r['fiscal_year_end'] for r in rows], ends)
        self.assertEqual(rows[0]['metrics']['owner_earnings']['value'], 80)
        self.assertEqual(rows[0]['metrics']['roe']['display'], '15.00%')
        self.assertTrue(all(v == 'pass' for v in checks.values()))

    def test_latest_comparative_annual_wins_quarters_and_amendments_excluded(self):
        f, ends = fixture()
        values = f['facts']['us-gaap']['NetIncomeLoss']['units']['USD']
        latest = dict(values[0], filed='2025-02-01', accn='0000000001-25-000001', val=25, fy=2024)
        values.extend([latest, dict(latest, start='2020-10-01', filed='2026-02-01', val=999),
                       dict(latest, form='10-Q', filed='2027-01-01', val=888),
                       dict(latest, form='10-K/A', filed='2027-02-01', val=777)])
        result = select_fact(f, 'net_income', ends[0])
        self.assertEqual(result['value'], 25)
        self.assertEqual(result['sources'][0]['filed'], '2025-02-01')

    def test_latest_filing_then_preferred_tag(self):
        f, ends = fixture()
        preferred = f['facts']['us-gaap'][TAGS['revenue'][0]]['units']['USD'][0]
        fallback = dict(preferred, val=600, filed='2025-02-01', accn='0000000001-25-000001')
        f['facts']['us-gaap']['Revenues'] = {'units': {'USD': [fallback]}}
        self.assertEqual(select_fact(f, 'revenue', ends[0])['value'], 600)
        f['facts']['us-gaap'][TAGS['revenue'][0]]['units']['USD'].append(dict(fallback, val=650))
        self.assertEqual(select_fact(f, 'revenue', ends[0])['value'], 650)

    def test_missing_input_is_not_known_not_zero(self):
        f, ends = fixture()
        f['facts']['us-gaap'][TAGS['capital_spending'][0]]['units']['USD'].pop(2)
        rows, checks = calculate(f, ends)
        self.assertEqual(rows[2]['metrics']['capital_spending']['display'], 'not found')
        self.assertEqual(rows[2]['metrics']['owner_earnings']['display'], 'not found')
        self.assertEqual(checks['Owner earnings positive every year'], 'not known')
        self.assertEqual(checks['Owner earnings grew first year to last'], 'pass')

    def test_nonpositive_equity(self):
        for value in (0, -100):
            with self.subTest(value=value):
                f, ends = fixture()
                f['facts']['us-gaap']['StockholdersEquity']['units']['USD'][0]['val'] = value
                rows, checks = calculate(f, ends)
                self.assertEqual(rows[0]['metrics']['roe']['display'], 'not known')
                self.assertEqual(rows[0]['metrics']['liabilities_to_equity']['display'], 'not known')
                self.assertEqual(checks['ROE at least 15% every year'], 'not known')

    def test_threshold_not_rounded_and_growth_is_strict(self):
        f, ends = fixture()
        f['facts']['us-gaap']['NetIncomeLoss']['units']['USD'][0]['val'] = 14.99999
        f['facts']['us-gaap'][TAGS['operating_cash_flow'][0]]['units']['USD'][-1]['val'] = 100
        rows, checks = calculate(f, ends)
        self.assertEqual(rows[0]['metrics']['roe']['display'], '15.00%')
        self.assertEqual(checks['ROE at least 15% every year'], 'fail')
        self.assertEqual(checks['Owner earnings grew first year to last'], 'fail')

    def test_annual_period_matching_and_53_week_year(self):
        f, ends = fixture()
        f['facts']['us-gaap'][TAGS['operating_cash_flow'][0]]['units']['USD'][0]['start'] = '2019-12-27'
        rows, _ = calculate(f, ends)
        self.assertIsNotNone(rows[0]['metrics']['operating_cash_flow']['value'])
        self.assertEqual(rows[0]['metrics']['owner_earnings']['display'], 'not found')

    def test_missing_window_and_ambiguous_facts(self):
        f, ends = fixture()
        _, checks = calculate(f, ends[:4])
        self.assertTrue(all(v == 'not known' for v in checks.values()))
        values = f['facts']['us-gaap']['NetIncomeLoss']['units']['USD']
        values.append(dict(values[0], val=999))
        self.assertEqual(select_fact(f, 'net_income', ends[0])['display'], 'not found')

    def test_ticker_validation(self):
        self.assertEqual(normalize_ticker(' brk.b '), 'BRK-B')
        with self.assertRaises(ValueError):
            normalize_ticker('../../file')


class MemoContract(unittest.TestCase):
    def setUp(self):
        self.report = json.loads((ROOT/'examples/AAPL_report.json').read_text())
        self.memo = (ROOT/'examples/AAPL_memo.md').read_text()

    def test_saved_memo_validates(self):
        result = audit_memo(self.memo, self.report)
        self.assertEqual(result['flags'], [])
        self.assertEqual(result['unknown_citations'], [])
        self.assertTrue(result['snapshot_match'])
        self.assertTrue(result['decision_valid'])

    def test_unsupported_numbers_words_abbreviations_and_scientific_notation(self):
        bad = self.memo + '\nGrowth 99.123%; $999; twenty years; 136.06b; 9e12.\n'
        flags = audit_memo(bad, self.report)['flags']
        self.assertEqual([f['number'] for f in flags], ['99.123%', '$999', 'twenty', '136.06b', '9e12'])

    def test_snapshot_and_unprovided_citation(self):
        bad = self.memo.replace(self.report['snapshot_id'], 'abc') + '\n[Source](https://example.org/123)'
        result = audit_memo(bad, self.report)
        self.assertFalse(result['snapshot_match'])
        self.assertEqual(result['unknown_citations'], ['https://example.org/123'])
        self.assertEqual(result['flags'], [])

    def test_unprovided_filing_date_flagged(self):
        result = audit_memo(self.memo+'\n10-Q filed 2099-12-31', self.report)
        self.assertEqual([f['number'] for f in result['flags']], ['2099-12-31'])

    def test_packet_contains_exact_snapshot_and_no_key_request(self):
        packet = memo_packet(self.report)
        self.assertIn(self.report['snapshot_id'], packet)
        self.assertIn('BEGIN SCRIPT OUTPUT', packet)
        self.assertIn('BEGIN UNTRUSTED QUALITATIVE FILING EXCERPTS', packet)
        self.assertIn('Decision: watch it', packet)


if __name__ == '__main__':
    unittest.main()
