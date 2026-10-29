"""Educational and research purposes only; not investment advice.

Compare public FRED CSVs with dated ALFRED CSVs. No API key or account.
Run: python -m streamlit run asof_app.py
"""

import csv
from datetime import date
from decimal import Decimal, InvalidOperation
from io import StringIO
import re
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

import pandas as pd
import streamlit as st
import altair as alt


SERIES_NAMES = {
    "BAA": "Moody's Baa corporate bond yield",
    "FEDFUNDS": "Federal funds rate",
    "DGS10": "10-year Treasury yield",
    "MORTGAGE30US": "30-year mortgage rate",
    "PAYEMS": "Payroll jobs, thousands",
    "CPIAUCSL": "Consumer Price Index, all items",
}
SERIES_UNITS = {series: "Percent" for series in ("BAA", "FEDFUNDS", "DGS10", "MORTGAGE30US")}
SERIES_UNITS["PAYEMS"] = "Thousands of jobs"
SERIES_UNITS["CPIAUCSL"] = "Index (1982–1984 = 100)"
DEFAULT_AS_KNOWN = date.today()


def valid_series_id(series_id):
    return bool(re.fullmatch(r"[A-Z0-9_.-]{1,100}", series_id))


def parse_csv(text, series_id, vintage=None):
    """Keep missing observations as None and preserve exact published decimals."""
    reader = csv.reader(StringIO(text.lstrip("\ufeff")))
    header = next(reader, [])
    if len(header) != 2 or header[0].lower() not in ("observation_date", "date"):
        raise ValueError("The service did not return the expected series/vintage CSV.")
    actual_vintage = None
    if vintage is None:
        if header[1] != series_id:
            raise ValueError("The service returned a different series.")
    else:
        match = re.fullmatch(re.escape(series_id) + r"_(\d{8})", header[1])
        if match is None:
            raise ValueError("The service returned an invalid vintage header.")
        actual_vintage = date.fromisoformat(match.group(1))
        if actual_vintage > vintage:
            raise ValueError("The service returned a snapshot later than requested.")
    observations = {}
    for fields in reader:
        if not fields:
            continue
        if len(fields) != 2:
            raise ValueError("The CSV contains an unexpected number of columns.")
        measured = date.fromisoformat(fields[0].strip())
        if measured in observations:
            raise ValueError("The CSV contains duplicate measured dates.")
        if actual_vintage is not None and measured > actual_vintage:
            raise ValueError("The vintage CSV contains a measured date after the requested date.")
        raw_value = fields[1].strip()
        if raw_value in (".", ""):
            observations[measured] = None
        else:
            value = Decimal(raw_value)
            if not value.is_finite():
                raise ValueError("The CSV contains a non-finite numeric value.")
            observations[measured] = raw_value
    return dict(sorted(observations.items()))


def fetch_csv(url, series_id, vintage=None):
    """One request, with no metadata requests, retries, API keys, or local files."""
    try:
        with urlopen(url, timeout=30) as response:
            text = response.read().decode("utf-8-sig")
        data = parse_csv(text, series_id, vintage)
        actual_vintage = None
        if vintage is not None:
            header = next(csv.reader(StringIO(text.lstrip("\ufeff"))))
            actual_vintage = date.fromisoformat(header[1].rsplit("_", 1)[1])
        return {"data": data, "error": None, "vintage": actual_vintage}
    except HTTPError as error:
        detail = "Series or vintage not found." if error.code in (400, 404) else "Service request failed."
        return {"data": None, "error": f"{detail} HTTP {error.code}."}
    except (URLError, TimeoutError, OSError):
        return {"data": None, "error": "Could not download the CSV. Check the connection and try again later."}
    except (ValueError, InvalidOperation, UnicodeError, csv.Error):
        return {"data": None, "error": "No valid CSV for this series and date. Check the series ID or choose another date."}


@st.cache_data(ttl=3600, max_entries=256, show_spinner=False)
def download_today(series_id, downloaded_on):
    """Today's FRED values; the date in the cache key prevents overnight reuse."""
    url = "https://fred.stlouisfed.org/graph/fredgraph.csv?" + urlencode({"id": series_id})
    return fetch_csv(url, series_id)


@st.cache_data(ttl=3600, max_entries=256, show_spinner=False)
def download_as_known(series_id, as_known_on, downloaded_on):
    """Request an ALFRED vintage; accept a labeled earlier snapshot, never a later one."""
    url = "https://alfred.stlouisfed.org/graph/alfredgraph.csv?" + urlencode(
        {"id": series_id, "vintage_date": as_known_on.isoformat()}
    )
    return fetch_csv(url, series_id, as_known_on)


def in_window(observations, start, end):
    return {day: value for day, value in observations.items() if start <= day <= end}


def last_numeric(observations):
    available = [(day, value) for day, value in observations.items() if value is not None]
    return max(available, default=(None, None), key=lambda pair: pair[0])


def compare_series(current, known):
    """None means download failure; an empty dict means a valid empty window."""
    current_date, current_value = last_numeric(current or {})
    known_date, known_value = last_numeric(known or {})
    added = revised = None
    if current is not None and known is not None:
        if known_date is not None:
            added = sum(day > known_date and value is not None for day, value in current.items())
        revised = sum(
            old is not None and current.get(day) is not None
            and Decimal(old) != Decimal(current[day])
            for day, old in known.items()
        )
    return {
        "Known: last measured": known_date,
        "Known: value": float(known_value) if known_value is not None else None,
        "Today: value for known date": (
            float(current[known_date])
            if current is not None and current.get(known_date) is not None else None
        ),
        "Today: last measured": current_date,
        "Today: value": float(current_value) if current_value is not None else None,
        "Later observations": added,
        "Revised values": revised,
    }


PALETTE = ["#0071E3", "#7B4ACB", "#14856E", "#C66A17", "#C44B72", "#69727E"]
SERIES_COLORS = dict(zip(SERIES_NAMES, PALETTE))


def chart_records(windows, rebase=False):
    """No resampling or filling. Rebase only at a shared observed date."""
    usable = {sid: obs for sid, obs in windows.items() if last_numeric(obs)[0] is not None}
    baseline = None
    if rebase and usable:
        dates = [{day for day, value in obs.items() if value is not None}
                 for obs in usable.values()]
        shared = set.intersection(*dates)
        if not shared:
            raise ValueError("No shared observed baseline date. Widen the date range or select fewer series.")
        baseline = min(shared)
        if any(Decimal(obs[baseline]) <= 0 for obs in usable.values()):
            raise ValueError("Start-at-100 needs positive baseline values. Choose a different start date or native units.")
    records = []
    for sid, obs in usable.items():
        base_value = Decimal(obs[baseline]) if baseline is not None else None
        for day, raw in obs.items():
            if baseline is not None and day < baseline:
                continue
            original = Decimal(raw) if raw is not None else None
            value = original / base_value * 100 if original is not None and base_value is not None else original
            records.append({"Date measured": day.isoformat(), "Value": float(value) if value is not None else None,
                            "Original value": float(original) if original is not None else None,
                            "Series": sid, "Units": SERIES_UNITS.get(sid, "Native series units")})
    return records, baseline


def y_domain(records, lower=None, upper=None):
    values = [r["Value"] for r in records if r["Value"] is not None]
    if not values:
        raise ValueError("No numeric values in this date range.")
    low, high = min(values), max(values)
    padding = (high - low) * 0.06 if high != low else max(abs(high) * 0.03, 0.01)
    lower = low - padding if lower is None else lower
    upper = high + padding if upper is None else upper
    if lower >= upper:
        raise ValueError("Y-axis minimum must be below its maximum.")
    return [lower, upper]


def make_chart(records, units, lower=None, upper=None):
    ids = list(dict.fromkeys(r["Series"] for r in records))
    colors = [SERIES_COLORS.get(sid, "#A36914") for sid in ids]
    bounds = y_domain(records, lower, upper)
    chart = alt.Chart(alt.Data(values=records)).mark_line(
        strokeWidth=2.4, clip=True, invalid="break-paths-show-domains",
    ).encode(
        x=alt.X("Date measured:T", title=None, axis=alt.Axis(grid=False, tickCount=6, format="%b %Y")),
        y=alt.Y("Value:Q", title=units, scale=alt.Scale(domain=bounds, zero=False, nice=False),
                axis=alt.Axis(grid=True, tickCount=5)),
        color=alt.Color("Series:N", scale=alt.Scale(domain=ids, range=colors),
                        legend=alt.Legend(orient="bottom", title=None) if len(ids) > 1 else None),
        tooltip=[alt.Tooltip("Series:N"), alt.Tooltip("Date measured:T", format="%b %d, %Y"),
                 alt.Tooltip("Value:Q", format=",.3f"), alt.Tooltip("Original value:Q", format=",.3f"),
                 alt.Tooltip("Units:N")],
    ).properties(height=300).add_params(
        alt.selection_interval(bind="scales", encodings=["x", "y"], clear="dblclick",
                               zoom="wheel![event.shiftKey]")
    )
    return chart.configure_view(stroke=None).configure_axis(
        labelColor="#69727E", titleColor="#69727E", gridColor="#E7E9ED", domain=False,
        labelFontSize=11, titleFontSize=11, labelPadding=8,
    )


def reset_charts(series_id=None):
    ids = [series_id] if series_id is not None else list(SERIES_NAMES) + ["overlay"]
    extra = st.session_state.get("extra_series", "").strip().upper()
    if series_id is None and extra:
        ids.append(extra)
    for sid in ids:
        st.session_state[f"axis_min_{sid}"] = None
        st.session_state[f"axis_max_{sid}"] = None
        key = f"chart_epoch_{sid}"
        st.session_state[key] = st.session_state.get(key, 0) + 1


def fit_data_dates():
    bounds = st.session_state.get("available_data_range")
    if bounds:
        st.session_state["start_date"], st.session_state["end_date"] = bounds
        reset_charts()


def select_checks(checked):
    for sid in SERIES_NAMES:
        st.session_state[f"show_{sid}"] = checked
    for key in list(st.session_state):
        if key.startswith("show_custom_"):
            st.session_state[key] = checked


def axis_controls(chart_id):
    with st.expander("Y-axis limits", icon=":material/tune:"):
        c1, c2 = st.columns(2)
        with c1:
            lower = st.number_input("Minimum", value=None, placeholder="Auto", key=f"axis_min_{chart_id}")
        with c2:
            upper = st.number_input("Maximum", value=None, placeholder="Auto", key=f"axis_max_{chart_id}")
        st.caption("Blank limits fit the visible values. Hold Shift and scroll to zoom; drag to pan.")
    return lower, upper


def display_chart(records, units, chart_id):
    lower, upper = axis_controls(chart_id)
    try:
        chart = make_chart(records, units, lower, upper)
    except ValueError as error:
        st.error(str(error))
        return
    epoch = st.session_state.get(f"chart_epoch_{chart_id}", 0)
    st.altair_chart(chart, key=f"chart_{chart_id}_{epoch}", width="stretch",
                    alt=f"{chart_id}: current published values; {units}. Shift-scroll to zoom and drag to pan.")


def format_value(value, sid):
    if value is None:
        return "—"
    return f"{Decimal(str(value)):,.0f}" if sid == "PAYEMS" else f"{Decimal(str(value)):,.3f}".rstrip("0").rstrip(".")


# Page
st.set_page_config(page_title="Fixed income research — FRED & ALFRED", layout="wide",
                   initial_sidebar_state="expanded", page_icon=":material/query_stats:")
today = date.today()

# Initialize once, preserving an existing session's selected historical date.
if not st.session_state.get("interface_v3_initialized", False):
    previous = st.session_state.get("selected_series", list(SERIES_NAMES))
    for sid in SERIES_NAMES:
        st.session_state.setdefault(f"show_{sid}", sid in previous)
    st.session_state.setdefault("end_date", today)
    st.session_state["interface_v3_initialized"] = True
st.session_state.setdefault("start_date", date(2020, 1, 1))
st.session_state.setdefault("as_known_on", DEFAULT_AS_KNOWN)

with st.sidebar:
    st.header("Your workspace")
    st.caption("Choose the series and period you want to explore.")
    with st.container(horizontal=True):
        st.button("Select all", key="select_all", on_click=select_checks, args=(True,))
        st.button("Clear", key="clear_series", on_click=select_checks, args=(False,))
    selected = []
    for sid, name in SERIES_NAMES.items():
        if st.checkbox(f"{sid} · {name}", key=f"show_{sid}",
                       help=f"Units: {SERIES_UNITS[sid]}"):
            selected.append(sid)
    extra = st.text_input("Add a FRED series", placeholder="Enter a series ID, then press Enter",
                          key="extra_series").strip().upper()
    if extra and extra not in SERIES_NAMES:
        st.session_state.setdefault(f"show_custom_{extra}", True)
        if st.checkbox(f"Show {extra}", key=f"show_custom_{extra}"):
            selected.append(extra)
    elif extra and extra not in selected:
        st.caption("Use the checkbox above to show this preset series.")
    st.subheader("Dates")
    start = st.date_input("Chart start", value=None,
                          min_value=date(1776, 7, 4), max_value=today, key="start_date")
    end = st.date_input("Chart end", value=None, min_value=date(1776, 7, 4), max_value=today, key="end_date")
    as_known_on = st.date_input("As known on", value=None,
                               min_value=date(1776, 7, 4), max_value=today, key="as_known_on",
                               help="Only publications available by this date belong in the historical snapshot.")
    st.caption("Chart dates set the measured period. “As known on” sets the historical information cutoff.")
    st.subheader("Sources")
    st.link_button("Explore FRED", "https://fred.stlouisfed.org/", width="stretch")
    st.link_button("Explore ALFRED", "https://alfred.stlouisfed.org/", width="stretch")

st.caption("FIXED INCOME RESEARCH")
st.title("A clearer view of the data.")
st.markdown("Explore rates, jobs, and inflation. Compare today's values with what was known then.")
st.caption(
    f"Data from FRED and ALFRED, Federal Reserve Bank of St. Louis, downloaded today ({today:%Y-%m-%d}); "
    "built with AI help, a learning demonstration, not investment advice."
)
with st.container(horizontal=True, vertical_alignment="center"):
    layout = st.segmented_control("Chart layout", ["Separate", "Overlay"], default="Separate",
                                   required=True, key="chart_layout")
    st.button("Reset zoom & axes", icon=":material/restart_alt:", key="reset_all",
              on_click=reset_charts, help="Reset chart zoom and manual y-axis limits. Keep your dates and series.")
    st.button("Fit data dates", icon=":material/fit_screen:", key="fit_dates",
              on_click=fit_data_dates, help="Use the full measured-date range of the selected downloaded series and fit the axes.")
if layout == "Overlay":
    overlay_scale = st.segmented_control("Overlay scale", ["Native units", "Start at 100"],
                                         default="Start at 100", required=True, key="overlay_scale")
else:
    overlay_scale = "Native units"

if start is None or end is None or as_known_on is None:
    st.info("Choose a chart start, chart end, and historical date to continue.")
    st.stop()
if start > end:
    st.error("Chart start must be on or before chart end.")
    st.stop()
if not selected:
    st.info("Check a series in Your workspace to display its chart and historical comparison.")

results, summary = {}, []
with st.spinner("Loading selected series…", show_time=True):
    for sid in selected:
        row = {"Series": f"https://fred.stlouisfed.org/series/{sid}",
               "Units": SERIES_UNITS.get(sid, "Native series units"),
               **compare_series(None, None), "Status": ""}
        if not valid_series_id(sid):
            results[sid] = {"current": None, "known": None, "errors": ["Enter a valid FRED series ID."],
                            "vintage": None}
            row["Status"] = "Invalid series ID"
            summary.append(row)
            continue
        current_result = download_today(sid, today)
        known_result = download_as_known(sid, as_known_on, today)
        errors = []
        current = known = None
        if current_result["error"]:
            errors.append("Today's data: " + current_result["error"])
        else:
            current = in_window(current_result["data"], start, end)
        if known_result["error"]:
            errors.append(f"As known on {as_known_on}: " + known_result["error"])
        else:
            known = in_window(known_result["data"], start, min(end, as_known_on))
        results[sid] = {"current": current, "known": known, "errors": errors,
                        "vintage": known_result.get("vintage"), "full_current": current_result["data"]}
        row.update(compare_series(current, known))
        row["Status"] = "; ".join(errors) or ("No historical values in window" if last_numeric(known or {})[0] is None else "OK")
        summary.append(row)

all_dates = [day for result in results.values() for day, value in (result.get("full_current") or {}).items()
             if value is not None and day <= today]
st.session_state["available_data_range"] = (min(all_dates), max(all_dates)) if all_dates else None

if layout == "Overlay" and selected:
    with st.container(border=True):
        st.subheader("Compare the trends")
        with st.container(horizontal=True):
            for sid in selected:
                if valid_series_id(sid):
                    st.link_button(sid + " on FRED", f"https://fred.stlouisfed.org/series/{sid}")
            st.button("Reset overlay", key="reset_overlay", on_click=reset_charts, args=("overlay",),
                      icon=":material/restart_alt:")
        windows = {sid: result["current"] for sid, result in results.items() if result["current"] is not None}
        units = {SERIES_UNITS.get(sid, f"Unverified native units ({sid})")
                 for sid, obs in windows.items() if last_numeric(obs)[0] is not None}
        if overlay_scale == "Native units" and len(units) > 1:
            st.info("These series use different units. Choose Start at 100, or select only series with matching native units.")
        else:
            try:
                records, baseline = chart_records(windows, rebase=overlay_scale == "Start at 100")
                if not records:
                    st.info("No numeric values to overlay in this period.")
                else:
                    label = "Index · common start = 100" if baseline is not None else next(iter(units), "Value")
                    if baseline is not None:
                        st.caption(f"All series start at 100 on {baseline}. Relative trends, not investment returns. "
                                   "Native frequencies and missing values are preserved. Rate indices can move sharply from small baselines.")
                    display_chart(records, label, "overlay")
            except ValueError as error:
                st.info(str(error))
        for sid, result in results.items():
            for error in result["errors"]:
                st.error(f"{sid}: {error}")
        dates = [f"{sid}: {last_numeric(result['known'] or {})[0] or 'unavailable'}" for sid, result in results.items()]
        st.caption(f"Last measured dates known on {as_known_on}: " + " · ".join(dates))
        earlier = [f"{sid}: {r['vintage']}" for sid, r in results.items() if r.get("vintage") and r["vintage"] < as_known_on]
        if earlier:
            st.caption("Earlier historical snapshots returned: " + "; ".join(earlier))

if layout == "Separate":
    for sid, result in results.items():
        with st.container(border=True):
            header, value_column = st.columns([3, 1], vertical_alignment="center")
            current_date, current_value = last_numeric(result["current"] or {})
            with header:
                st.subheader(SERIES_NAMES.get(sid, sid))
                st.caption(f"{sid} · {SERIES_UNITS.get(sid, 'Native series units')}")
            with value_column:
                st.subheader(format_value(current_value, sid))
                st.caption(str(current_date) if current_date else "No value in window")
            with st.container(horizontal=True):
                if valid_series_id(sid):
                    st.link_button("FRED", f"https://fred.stlouisfed.org/series/{sid}", key=f"fred_{sid}")
                    st.link_button("ALFRED", f"https://alfred.stlouisfed.org/series?" + urlencode(
                        {"seid": sid, "vintage_date": as_known_on.isoformat()}), key=f"alfred_{sid}")
                st.button("Reset chart", key=f"reset_{sid}", on_click=reset_charts, args=(sid,),
                          icon=":material/restart_alt:", help="Restore both axes to the selected date window and fit the values.")
            for error in result["errors"]:
                st.error(f"{sid}: {error}")
            if current_date is not None:
                records, _ = chart_records({sid: result["current"]})
                display_chart(records, SERIES_UNITS.get(sid, "Series value"), sid)
            elif not result["errors"]:
                st.info("No numeric observations in this chart period.")
            known_date, known_value = last_numeric(result["known"] or {})
            st.caption(f"Last measured date known on {as_known_on}: {known_date or 'unavailable in this window'}.")
            if result.get("vintage") is not None and result["vintage"] < as_known_on:
                st.caption(f"Historical snapshot returned: {result['vintage']}; requested: {as_known_on}.")
            if sid == "PAYEMS" and known_date is not None:
                same_month_today = (result["current"] or {}).get(known_date)
                st.caption(f"{known_date:%B %Y}: {format_value(known_value, sid)} as known then; "
                           f"the same month today: {format_value(same_month_today, sid)}. Units: thousands of jobs.")

if summary:
    st.subheader("What changed since then?")
    st.caption("Raw values, unaffected by chart scale or zoom. Counts use your measured-date window. "
               "Later observations exclude missing values; revisions compare numeric values on the same dates. A dash means unavailable.")
    table = pd.DataFrame(summary)
    for column in ("Later observations", "Revised values"):
        table[column] = pd.array(table[column], dtype="Int64")
    st.dataframe(table, hide_index=True, placeholder="—", width="stretch", height="content",
        column_config={
            "Series": st.column_config.LinkColumn("Series", display_text=r"https://fred\.stlouisfed\.org/series/(.*)", pinned=True),
            "Known: last measured": st.column_config.DateColumn(format="YYYY-MM-DD"),
            "Today: last measured": st.column_config.DateColumn(format="YYYY-MM-DD"),
            "Known: value": st.column_config.NumberColumn(format="%.3f"),
            "Today: value for known date": st.column_config.NumberColumn(format="%.3f",
                help="Today's value for the historical last measured date, not today's latest month."),
            "Today: value": st.column_config.NumberColumn(format="%.3f"),
        }, alt="Raw historical and current dates and values, later observations, and revision counts.")

st.caption("Educational and research purposes only. Not investment advice. "
           "A daily as-of date does not establish availability before an intraday trade.")
