from pathlib import Path
import unittest
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]


class AppBehavior(unittest.TestCase):
    def test_cost_panel_and_pasted_number_flag(self):
        app = AppTest.from_file(str(ROOT / 'streamlit_app.py')).run(timeout=20)
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(app.dataframe[0].value), 3)
        self.assertTrue(any('CLEAR' in s.value for s in app.success))
        self.assertEqual(len(app.columns), 3)
        self.assertTrue(any('judgment belong' in m.value for m in app.markdown))
        next(c for c in app.segmented_control if c.label == 'Memo source').set_value('Paste Markdown').run()
        for area, key in zip(app.text_area, ('buffett', 'wood', 'burry')):
            area.set_value((ROOT / f'examples/COST_{key}_memo.md').read_text())
        app.run()
        self.assertEqual(len(app.exception), 0)
        self.assertTrue(any('CLEAR' in s.value for s in app.success))
        app.text_area[1].set_value(app.text_area[1].value + '\nInvented 99.123% growth.').run()
        self.assertEqual(len(app.exception), 0)
        self.assertTrue(any('FLAGGED' in e.value for e in app.error))
        self.assertTrue(any('Synthesis withheld' in m.value for m in app.markdown))

    def test_invalid_ticker_and_stacked_reading(self):
        app = AppTest.from_file(str(ROOT / 'streamlit_app.py')).run(timeout=20)
        app.text_input[0].set_value('../bad')
        app.button[0].click().run()
        self.assertEqual(len(app.exception), 0)
        self.assertTrue(any('ticker' in e.value for e in app.error))
        self.assertTrue(any('COST' in s.value for s in app.subheader))
        next(c for c in app.segmented_control if c.label == 'Reading layout').set_value('Stacked').run()
        self.assertEqual(len(app.exception), 0)
        self.assertTrue(any('CLEAR' in s.value for s in app.success))
