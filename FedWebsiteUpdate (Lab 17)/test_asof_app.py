"""Offline checks for the educational FRED/ALFRED app; no live requests."""

from collections import Counter
from datetime import date
from io import BytesIO
from pathlib import Path
import types
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlparse

from streamlit.testing.v1 import AppTest


APP = Path(__file__).with_name("asof_app.py")


def helpers():
    module = types.ModuleType("asof_app_helpers")
    exec(compile(APP.read_text().split("# Page\n", 1)[0], str(APP), "exec"), module.__dict__)
    return module


class AppChecks(unittest.TestCase):
    def test_overlay_common_baseline_missing_values_and_axis_limits(self):
        app = helpers()
        windows = {
            "A": {date(2020, 1, 1): "2", date(2020, 1, 2): None, date(2020, 1, 3): "4"},
            "B": {date(2020, 1, 1): "10", date(2020, 1, 3): "12"},
        }
        rows, baseline = app.chart_records(windows, rebase=True)
        self.assertEqual(baseline, date(2020, 1, 1))
        self.assertEqual([r["Value"] for r in rows if r["Series"] == "A"], [100.0, None, 200.0])
        self.assertEqual([r["Value"] for r in rows if r["Series"] == "B"], [100.0, 120.0])
        self.assertEqual(windows["A"][date(2020, 1, 3)], "4")  # Source never transformed in place.
        spec = app.make_chart(rows, "Start = 100").to_dict()
        self.assertEqual(spec["mark"]["invalid"], "break-paths-show-domains")
        self.assertEqual(app.y_domain(rows, 50, 250), [50, 250])
        with self.assertRaises(ValueError):
            app.y_domain(rows, 250, 50)
        with self.assertRaises(ValueError):
            app.chart_records({"A": {date(2020, 1, 1): "1"}, "B": {date(2020, 1, 2): "2"}}, True)
        with self.assertRaises(ValueError):
            app.chart_records({"A": {date(2020, 1, 1): "0"}}, True)

    def test_missing_values_exact_revisions_and_later_counts(self):
        app = helpers()
        current = app.parse_csv(
            "observation_date,BAA\n2020-01-01,1.00\n2020-02-01,.\n"
            "2020-03-01,2.100\n2020-04-01,.\n2020-05-01,3\n", "BAA")
        known = app.parse_csv(
            "observation_date,BAA_20200331\n2020-01-01,1.0\n"
            "2020-02-01,.\n2020-03-01,2.0\n", "BAA", date(2020, 3, 31))
        result = app.compare_series(current, known)
        self.assertIsNone(current[date(2020, 2, 1)])
        self.assertEqual(result["Known: last measured"], date(2020, 3, 1))
        self.assertEqual(result["Later observations"], 1)  # May; not April's missing value.
        self.assertEqual(result["Revised values"], 1)  # Not 1.00 versus 1.0.
        self.assertIsNone(app.compare_series(current, {})["Later observations"])
        self.assertIsNone(app.compare_series(current, None)["Revised values"])
        negative = app.parse_csv("observation_date,DGS10\n2020-01-01,-0.1\n", "DGS10")
        self.assertEqual(negative[date(2020, 1, 1)], "-0.1")

    def test_wrong_vintage_and_duplicate_dates_fail_closed(self):
        app = helpers()
        earlier = app.parse_csv("observation_date,BAA_20200330\n2020-03-01,2\n",
                                "BAA", date(2020, 3, 31))
        self.assertEqual(earlier[date(2020, 3, 1)], "2")
        with self.assertRaises(ValueError):
            app.parse_csv("observation_date,BAA_20260401\n2020-01-01,2\n",
                          "BAA", date(2026, 3, 31))
        with self.assertRaises(ValueError):
            app.parse_csv("observation_date,BAA_20200331\n2020-04-01,2\n",
                          "BAA", date(2020, 3, 31))
        with self.assertRaises(ValueError):
            app.parse_csv("observation_date,BAA\n2020-01-01,1\n2020-01-01,2\n", "BAA")

    def test_ui_cache_dates_extra_id_and_failure_isolation(self):
        calls = []

        def fake_urlopen(request, timeout):
            url = urlparse(request)
            query = parse_qs(url.query)
            series = query["id"][0]
            vintage = query.get("vintage_date", [None])[0]
            calls.append((series, vintage))
            if series == "UNKNOWN_TEST":
                raise HTTPError(request, 404, "not found", {}, None)
            header = series if vintage is None else f"{series}_{vintage.replace('-', '')}"
            text = f"observation_date,{header}\n"
            if vintage is None or vintage >= "2020-01-01":
                text += "2020-01-01,1.00\n2020-02-01,.\n"
            if vintage is None or vintage >= "2026-03-11":
                text += "2026-02-01," + ("4.10" if vintage is None else "4.00") + "\n"
            if vintage is None or vintage >= "2026-05-01":
                text += "2026-04-01,5.00\n"
            return BytesIO(text.encode())

        with patch("urllib.request.urlopen", side_effect=fake_urlopen):
            at = AppTest.from_file(str(APP), default_timeout=30).run()
            self.assertFalse(at.exception)
            self.assertEqual(len(at.checkbox), 6)
            self.assertTrue(all(widget.value for widget in at.checkbox))
            self.assertEqual(at.date_input(key="start_date").value, date(2020, 1, 1))
            self.assertEqual(at.date_input(key="as_known_on").value, date.today())
            self.assertEqual(len(at.dataframe[0].value), 6)
            self.assertEqual(len(at.get("vega_lite_chart")), 6)
            self.assertEqual(len(calls), 12)  # One FRED and one ALFRED request per series.
            at.date_input(key="start_date").set_value(date(2021, 1, 1)).run()
            self.assertFalse(at.exception)
            self.assertEqual(len(calls), 12)  # Cheap date filtering reuses both caches.
            at.date_input(key="as_known_on").set_value(date(2026, 3, 31)).run()
            self.assertFalse(at.exception)
            self.assertEqual(len(calls), 18)  # Only six new vintage requests.
            table = at.dataframe[0].value
            self.assertTrue((table["Later observations"] == 1).all())
            self.assertTrue((table["Revised values"] == 1).all())
            at.text_input(key="extra_series").set_value("UNKNOWN_TEST").run()
            self.assertFalse(at.exception)
            self.assertEqual(len(at.error), 2)
            self.assertEqual(len(at.dataframe[0].value), 7)
            self.assertEqual(len(calls), 20)
            at.run()
            self.assertEqual(len(calls), 20)  # Errors are cached too.
            at.text_input(key="extra_series").set_value("UNRATE").run()
            self.assertFalse(at.exception)
            self.assertFalse(at.error)
            self.assertEqual(len(at.dataframe[0].value), 7)
            self.assertEqual(len(calls), 22)
            # Chart controls never change historical calculations or fetch again.
            before = at.dataframe[0].value.copy()
            at.number_input(key="axis_min_BAA").set_value(0.0).run()
            at.button(key="reset_BAA").click().run()
            self.assertIsNone(at.number_input(key="axis_min_BAA").value)
            self.assertEqual(at.session_state["chart_epoch_BAA"], 1)
            self.assertEqual(at.date_input(key="as_known_on").value, date(2026, 3, 31))
            at.session_state["chart_layout"] = "Overlay"
            at.run()
            self.assertFalse(at.exception)
            self.assertEqual(len(at.get("vega_lite_chart")), 1)
            self.assertTrue(before.equals(at.dataframe[0].value))
            at.session_state["overlay_scale"] = "Native units"
            at.run()
            self.assertFalse(at.exception)
            self.assertEqual(len(at.get("vega_lite_chart")), 0)  # Don't mix incompatible units.
            self.assertTrue(any("different units" in info.value for info in at.info))
            at.button(key="fit_dates").click().run()
            self.assertEqual(at.date_input(key="start_date").value, date(2020, 1, 1))
            self.assertEqual(at.date_input(key="end_date").value, date(2026, 4, 1))
            self.assertEqual(at.date_input(key="as_known_on").value, date(2026, 3, 31))
            self.assertEqual(len(calls), 22)
            at.button(key="clear_series").click().run()
            self.assertFalse(at.exception)
            self.assertFalse(at.dataframe)
            self.assertFalse(any(widget.value for widget in at.checkbox))
            at.button(key="select_all").click().run()
            self.assertFalse(at.exception)
            self.assertEqual(len(at.dataframe[0].value), 7)
            self.assertEqual(len(calls), 22)
            self.assertTrue(all(count == 1 for count in Counter(calls).values()))


if __name__ == "__main__":
    unittest.main()
