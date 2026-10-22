"""Run with python -m unittest discover -s 'Lab 15' from Project 2 FIN439."""
import io
import itertools
import math
from pathlib import Path
import unittest

from portfolio import estimate_from_csv, search_lowest_risk_mix


class PortfolioExtensionsTest(unittest.TestCase):
    def test_search_matches_independent_full_grid(self):
        sleeves = {"reserve": {"expected_return": .03, "volatility": .01},
                   "bond": {"expected_return": .05, "volatility": .07},
                   "stock": {"expected_return": .10, "volatility": .20}}
        correlations = [[1, .2, -.1], [.2, 1, .3], [-.1, .3, 1]]
        result = search_lowest_risk_mix(sleeves, correlations, .065, .03, {"reserve"})
        candidates = []
        for units in itertools.product(range(21), repeat=3):
            if sum(units) != 20:
                continue
            w = [value / 20 for value in units]
            if sum(weight * mu for weight, mu in zip(w, [.03, .05, .10])) < .065 - 1e-12 or w[0] < .03:
                continue
            sigma = [.01, .07, .20]
            variance = sum(w[i] * w[j] * sigma[i] * sigma[j] * correlations[i][j]
                           for i in range(3) for j in range(3))
            candidates.append((variance, w))
        best = min(candidates)
        self.assertAlmostEqual(result["volatility"], math.sqrt(best[0]))
        self.assertEqual(list(result["weights"].values()), best[1])
        self.assertAlmostEqual(sum(result["weights"].values()), 1)

    def test_infeasible_and_boundary_constraints(self):
        sleeves = {"A": {"expected_return": .065, "volatility": .1}}
        self.assertIsNone(search_lowest_risk_mix(sleeves, [[1]], .066, 0, set()))
        self.assertIsNone(search_lowest_risk_mix(sleeves, [[1]], .065, .03, set()))
        result = search_lowest_risk_mix(sleeves, [[1]], .065, 1, {"A"})
        self.assertEqual(result["weights"], {"A": 1.0})

    def test_csv_known_sample_statistics_and_negative_correlation(self):
        text = 'date,A,B\n2025-01-31,100,100\n2025-02-28,110,90\n2025-03-31,110,90\n'
        result = estimate_from_csv(io.StringIO(text))
        self.assertAlmostEqual(result["sleeves"]["A"]["expected_return"], .6)
        self.assertAlmostEqual(result["sleeves"]["A"]["volatility"], math.sqrt(.06))
        self.assertAlmostEqual(result["sleeves"]["B"]["expected_return"], -.6)
        self.assertAlmostEqual(result["correlations"][0][1], -1)

    def test_last_36_returns_includes_first_transition(self):
        lines = ['date,A']
        price = 100
        for i in range(41):
            if i:
                price *= 1 + i / 1000
            lines.append(f'{2020 + i // 12}-{i % 12 + 1:02d}-01,{price:.14f}')
        text = '\n'.join(lines)
        all_months = estimate_from_csv(io.StringIO(text))
        recent = estimate_from_csv(io.StringIO(text), True)
        self.assertEqual(all_months["months"], 40)
        self.assertEqual(recent["months"], 36)
        self.assertEqual(recent["start"], '2020-06-01')
        self.assertAlmostEqual(recent["sleeves"]["A"]["expected_return"], ((.005 + .040) / 2) * 12)

    def test_invalid_csv_and_constant_prices(self):
        for text in [
            'date,A\n2025-01-01,100\n2025-03-01,101\n2025-04-01,102',
            'date,A\n2025-02-01,100\n2025-01-01,101\n2025-03-01,102',
            'date,A,A\n2025-01-01,1,1',
            'date,A\n2025-01-01,100\n2025-02-01,nan\n2025-03-01,102',
            'date,A\n2025-01-01,100\n2025-02-01,0\n2025-03-01,102',
            'date,A\n2025-01-01,100\n2025-02-01,101',
        ]:
            with self.subTest(text=text), self.assertRaises(ValueError):
                estimate_from_csv(io.StringIO(text))
        result = estimate_from_csv(io.StringIO(
            'date,A,B\n2025-01-01,100,100\n2025-02-01,100,110\n2025-03-01,100,110'))
        self.assertEqual(result["sleeves"]["A"]["volatility"], 0)
        self.assertEqual(result["correlations"], [[1.0, 0.0], [0.0, 1.0]])


class AppTest(unittest.TestCase):
    def test_meridian_edits_and_infeasibility(self):
        from streamlit.testing.v1 import AppTest
        app = AppTest.from_file(str(Path(__file__).with_name('app.py')), default_timeout=30).run()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[0].value, '6.51%')
        self.assertEqual(app.metric[-1].value, '0.00 percentage points')
        self.assertEqual(sum(widget.value for widget in app.checkbox), 2)
        app.number_input(key='return:Meridian:False:Global equity index fund').set_value(12.0).run()
        self.assertFalse(app.exception)
        self.assertNotEqual(app.metric[-1].value, '0.00 percentage points')
        self.assertEqual(app.metric[3].value, '6.51%')  # Reference is unchanged.
        app.number_input(key='objective').set_value(100.0).run()
        self.assertFalse(app.exception)
        self.assertEqual(sum(item.value == 'no mix meets the objective' for item in app.info), 2)

    def test_csv_upload_and_window(self):
        from unittest.mock import patch
        from streamlit.testing.v1 import AppTest
        lines = ['date,A,B']
        a, b = 100, 100
        for i in range(41):
            a *= 1.01 if i % 2 else 1.02
            b *= 1.002 if i % 2 else 1.004
            lines.append(f'{2020+i//12}-{i%12+1:02d}-01,{a},{b}')
        with patch('streamlit.file_uploader', return_value=io.BytesIO('\n'.join(lines).encode())):
            app = AppTest.from_file(str(Path(__file__).with_name('app.py')), default_timeout=30).run()
            self.assertFalse(app.exception)
            self.assertTrue(any(item.value == 'no mix meets the objective' for item in app.info))
            app.checkbox[1].check().run()
            self.assertFalse(app.exception)
            self.assertEqual(app.metric[-1].value, '0.00 percentage points')
            app.toggle(key='last_36').set_value(True).run()
            self.assertFalse(app.exception)
            self.assertTrue(any('36 monthly returns' in item.value for item in app.caption))


if __name__ == '__main__':
    unittest.main()
