from pathlib import Path
import unittest
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]


class AppBehavior(unittest.TestCase):
    def test_example_and_fresh_pasted_memo(self):
        app = AppTest.from_file(str(ROOT/'streamlit_app.py')).run(timeout=20)
        self.assertEqual(len(app.exception), 0)
        self.assertTrue(any('No unsupported' in s.value for s in app.success))
        self.assertEqual(len(app.dataframe[0].value), 5)
        next(c for c in app.segmented_control if c.label == 'Memo source').set_value('Paste Markdown').run()
        memo = (ROOT/'examples/AAPL_memo.md').read_text()+'\nClaim: 99.123% growth.'
        app.text_area[0].set_value(memo).run()
        self.assertEqual(len(app.exception), 0)
        self.assertTrue(any('unsupported numerical' in e.value for e in app.error))
        self.assertEqual(app.dataframe[-1].value.iloc[0]['number'], '99.123%')

    def test_invalid_ticker_keeps_explicit_previous_company(self):
        app = AppTest.from_file(str(ROOT/'streamlit_app.py')).run(timeout=20)
        app.text_input[0].set_value('../bad')
        app.button[0].click().run()
        self.assertEqual(len(app.exception), 0)
        self.assertTrue(any('ticker' in e.value for e in app.error))
        self.assertTrue(any('AAPL' in s.value for s in app.subheader))
