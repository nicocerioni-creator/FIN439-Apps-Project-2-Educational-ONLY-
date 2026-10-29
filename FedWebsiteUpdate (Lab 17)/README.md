# Lab 17 — FRED and ALFRED data explorer

## Educational and research purposes only

This project, including its data, analyses, and outputs, is for educational and research purposes only. It does not constitute investment, financial, legal, tax, or other professional advice, or a recommendation or solicitation to buy or sell securities. Historical data and estimates do not guarantee future results. Do not rely on these materials as the basis for real-world investment or financial decisions.

## Open the app on Nicolas's Mac

1. Open **Terminal** with Command+Space, type Terminal, and press Return.
2. Paste this command and press Return:

   ```bash
   cd "/Users/nicocerioni/Documents/School/Business/AI Finance 2026"
   ```

3. Paste this command and press Return:

   ```bash
   ./.venv/bin/python -m streamlit run "NicolasCerioni/Project 2 FIN439/Lab 17/asof_app.py" --server.port 8503
   ```

4. The browser should open automatically. Otherwise, visit **http://localhost:8503**.
5. Keep Terminal open while using the app. To stop it, press **Control+C** in that Terminal.

If port 8503 is already in use, first try opening that address and refreshing: the app may already be running. To run a separate instance, change the command to `--server.port 8504` and open http://localhost:8504. Do not stop an unrelated app just to free a port.

The existing project environment already contains the required packages. Normal startup does not require an API key, account, or package installation. An internet connection is needed for the public FRED/ALFRED CSV downloads.

## Open the GitHub copy on another computer

GitHub stores the project files; uploading them does not deploy a publicly hosted Streamlit app. Run the downloaded code locally.

The repository folder for this lab is **FedWebsiteUpdate (Lab 17)**. With Python 3.11 available, a first-time setup from Terminal is:

```bash
git clone https://github.com/nicocerioni-creator/Part-2-of-FIN439.git
cd Part-2-of-FIN439
python3 -m venv .venv
source .venv/bin/activate
python -m pip install "streamlit==1.66.1" "pandas==3.1.0" "altair==6.3.0"
python -m streamlit run "FedWebsiteUpdate (Lab 17)/asof_app.py" --server.port 8503
```

These are the package versions tested on the original Mac. The installation commands are for a new environment, not a required reinstall on the original Mac. On later visits, enter the repository folder, activate its environment, and run the last command again. Keep the lab's `.streamlit/config.toml` with the app so its theme is available.

## Use the app

1. Open **Your workspace** in the left sidebar. On a narrow window, click the top-left double-chevron to expand it.
2. Check the series you want. **Select all** and **Clear** apply to the graph checkboxes. Enter an additional FRED ID in **Add a FRED series** and press Return to add its checkbox.
3. Set **Chart start** and **Chart end** to choose the measured period. Set **As known on** independently to select the historical information available by that day. The historical date defaults to today; no Project 2 trading schedule is selected automatically.
4. Use **Separate** for individual charts. Each card shows its current value, units, source links, and latest measured date available in the historical snapshot.
5. Use **Overlay** to layer selected graphs. **Native units** requires matching verified units. **Start at 100** compares relative trends on a shared observed baseline date; it is not an investment-return chart. If there is no common observed date, widen the window or select fewer series.
6. Hold **Shift** while scrolling over a chart to zoom; drag to pan. Expand **Y-axis limits** to enter a minimum or maximum, or leave both blank for automatic fitting. **Reset chart**, **Reset overlay**, and **Reset zoom & axes** restore chart views without changing the historical cutoff.
7. **Fit data dates** fits the full current downloaded date range of the selected series and their axes. It can extend the measured period before 2020 and change the comparison counts. It keeps **As known on** unchanged.
8. Read **What changed since then?** below the charts. It always shows raw values. **Today: value for known date** compares the same measured date, while **Today: value** is the latest current observation. **Later observations** and **Revised values** are different counts; missing values are not counted as numbers.

For a useful revision example, choose PAYEMS and set **As known on** to January 15, 2025. At the October 29, 2026 check, December 2024 was 159,536 as known then versus 158,316 in the current download, with 59 revisions in the start-2020 window. These figures are historical verification results, not values typed into the app; a later download may differ.

An unknown ID or unavailable download produces an error for that series while the others continue working. The chart controls reuse cached downloads. Cache entries expire after one hour. If a service error persists, verify the ID and connection, then try again later or use Streamlit's menu to clear the cache and rerun. Do not enter API keys into the series box; this app does not use them.

## Files included

| File or folder | Purpose |
| --- | --- |
| `asof_app.py` | Interactive FRED/ALFRED viewer. |
| `.streamlit/config.toml` | App-specific light theme; keep it with the script. |
| `test_asof_app.py` | Offline calculation, caching, and interface checks. |
| `Lab 17 Data Card - CPIAUCSL.md` | Source, units, lag, revisions, checked observations, and Project 2 admission decision. |
| `CPIAUCSL_all_vintages.csv` / `.xlsx` | Full saved CPI publication/revision history, through October 29, 2026. |
| `CPIAUCSL_asof_2026-03-31.csv` / `.xlsx` | Illustrative historical panel; March 31 is not a selected Lab 17 trading date. |
| `asof_cpi.py` | Standard-library selector for the saved CPI archive, independent of the live app. |
| `sources/` | Original CPI responses, provenance metadata, and verification/audit records. |
| `Fixed Income Product Proposals.md` | Researched future features; implementation is deferred. |

The source-data approval is recorded below. Optional product improvements are deferred at Nicolas's request; this upload adds no further product features. API keys, local environments, and Python caches are not part of this publication.

## Economic-series viewer — asof_app.py

The current interface uses an Apple-inspired light theme, graph checkboxes, source links on each chart, and Separate/Overlay controls. The approved Start at 100 overlay uses the first date with a nonmissing observation in **every** selected series; it does not forward-fill, interpolate, resample, or mix units on a raw shared scale. Data before that shared baseline are omitted from the rebased overlay. Baseline values must be positive, and a relative rate index is not a bond return.

- **Reset chart / Reset overlay:** clear pan/zoom and optional manual y-axis limits for that chart, keeping the measured-date window and historical cutoff.
- **Reset zoom & axes:** reset all chart views and manual y-axis limits; retain selected series and dates.
- **Fit data dates:** use the full current downloaded date range across the selected series and fit chart axes; retain the “As known on” date. This can extend the measured window before 2020 and change the comparison counts accordingly.
- **Y-axis limits:** leave blank for a fitted range or enter minimum/maximum values. Shift-scroll zooms; drag pans; double-click also resets the interactive view.
- **Native-unit overlay:** supports series with matching verified units. Use Start at 100 for mixed units. Missing values remain gaps.

The comparison table always retains raw values; chart normalization and zoom never change its calculations. The six visible checkboxes replace the earlier multiselect. The optional custom ID has its own visibility checkbox. The theme lives in `.streamlit/config.toml` beside this script and is scoped to Lab 17.

[Fixed-income product proposals](Fixed%20Income%20Product%20Proposals.md) records the competitor/user-review research, the target audience, recommended next features, and approval status. Only the requested interface changes and explicitly approved start-at-100 view are implemented. Other proposals await Nicolas's approval.


[asof_app.py](asof_app.py) is a Streamlit viewer for BAA, FEDFUNDS, DGS10, MORTGAGE30US, PAYEMS, and CPIAUCSL, with a text box for one additional FRED series ID. All six presets are selected initially. The chart start defaults to January 1, 2020; the independent “As known on” control defaults to the current day, not the earlier March 31 example.

Run from the AI Finance 2026 working directory using the existing environment:

```bash
./.venv/bin/python -m streamlit run "NicolasCerioni/Project 2 FIN439/Lab 17/asof_app.py" --server.port 8503
```

Open http://localhost:8503 if the browser does not open automatically. Stop the server with Control+C in its terminal. No new packages were installed.

Data come from the public CSV downloads, without an API key or account:

- Current: `https://fred.stlouisfed.org/graph/fredgraph.csv?id=SERIES`
- Historical snapshot: `https://alfred.stlouisfed.org/graph/alfredgraph.csv?id=SERIES&vintage_date=YYYY-MM-DD`

Two separately cached download functions make one request per series/source on a cache miss. They do not request metadata, call the API, read credentials, or retry requests automatically. Entries expire after one hour, are bounded in number, and use today's date in their cache keys so yesterday's response is not presented as downloaded today. An ID/date error is displayed for that series; other series continue loading.

Each chart shows current values from the selected start date at the series' native frequency. Under it, the app shows the latest nonmissing measured date in the historical snapshot for that same window. The four interest rates are in percent; PAYEMS is in thousands of jobs and CPIAUCSL is an index (1982–1984=100). Additional IDs retain their native units, without being converted to interest rates.

The comparison table shows the latest nonmissing date/value in each window, plus today's value for the same historical last measured date. This separates revisions to an old month from a newer month's value. “Later observations” counts today's nonmissing observations strictly after the last nonmissing historical measured date. It is unavailable if there is no historical numeric observation. “Revised values” compares exact decimals on the same dates with numeric values in both snapshots, avoiding false changes from formatting such as 1.0 versus 1.00. Missing-to-numeric transitions are not counted as numeric revisions. Both counts use the selected start date, not the entire downloadable history.

A dot or blank is missing, never zero. Missing observations remain missing in the chart; they are neither filled nor counted as numeric values. The app validates the historical CSV's vintage header, rejects a snapshot later than requested, and rejects a measured date after the returned vintage. ALFRED may return a snapshot labeled earlier than requested; the app accepts it conservatively and displays the returned date. Daily availability still does not establish availability before an intraday trade.

The app does not change the saved CPI tables or run `asof_cpi.py`; its public CSV downloads are independent. No actual Lab 17 trade date has been selected by building or testing the app.

Offline parser, comparison, caching, and UI checks:

```bash
./.venv/bin/python -m unittest discover -s "NicolasCerioni/Project 2 FIN439/Lab 17" -p "test_asof_app.py" -v
```

[Lab 17 Data Card — CPIAUCSL](Lab%2017%20Data%20Card%20-%20CPIAUCSL.md) records the September 30 versus October 29 comparison, three values checked on the FRED page, publication/revision characteristics, and the clearly labeled **Quarantine** decision with admission conditions. The app was tested with last month-end and then today; its final default is today. These examples do not select the actual Project 2 trading schedule.

PAYEMS regression check: with “As known on” set to January 15, 2025, December 2024 was 159,536; today's value for the same month was 158,316, with 59 revised values in the start-2020 window. These figures were read from separate public CSVs, not hardcoded into the app. PAYEMS is no longer the initial date setting because the subsequent lab instruction ended with today's date.

## Series choice and connection to Project 2

Selected series: **CPIAUCSL — Consumer Price Index for All Urban Consumers: All Items in U.S. City Average**. Source agency: U.S. Bureau of Labor Statistics. Frequency: monthly. Seasonal adjustment: seasonally adjusted. Units: **index, 1982–1984 = 100**. These are index levels, not inflation percentages. [ALFRED series page](https://alfred.stlouisfed.org/series?seid=CPIAUCSL).

SPY would not meet the assignment's requirement to choose a series other than funds' own prices. CPI is a macroeconomic series rather than a fund price, and its revisions make it useful for this provenance exercise.

My research rationale: inflation news may change expectations for interest rates, discount rates, and business costs. Those channels are relevant to the project's broad equity, growth, dividend, infrastructure, energy, healthcare, and Treasury-bill exposures: VOO, QQQ, SCHD, PAVE, XLE, XLV, and SGOV. This is an economic hypothesis to investigate, not evidence that CPI predicts returns or that all funds respond in the same direction. A market reaction may depend on how a release differs from expectations, not simply whether inflation is high.

## Table and coverage

**The all-vintages table is an archive, not a trade-ready panel.** It contains publications after earlier decision dates so the assignment can demonstrate revisions. Using every row, or simply today's final value for each measured month, in an earlier trade would introduce hindsight.

- [Excel table](CPIAUCSL_all_vintages.xlsx): filterable table with dates and numeric values stored as typed cells.
- [CSV table](CPIAUCSL_all_vintages.csv): the same records with exactly the four requested columns: **Series name, Month measured, Published on, Value**.
- Measured window: **July 2024 through September 2026**, inclusive, or 27 calendar months.
- Coverage: **26 months with numeric observations**, plus the missing October 2025 month retained explicitly.
- Records: **50**, comprising **49 numeric initial/revised values and one missing-value marker**.
- Publication history cutoff: **October 29, 2026**. Later vintages are not included.

October 2025 appears with `.` in the Value column. That is ALFRED's missing-value marker, not zero. BLS reports that it did not collect CPI data from October 1 through November 12, 2025 during the lapse in appropriations. Do not fill this gap with an invented observation. The window starts one month earlier than a 26-calendar-month window so it still includes 26 months with numeric data. [BLS shutdown explanation](https://www.bls.gov/cpi/additional-resources/2025-federal-government-shutdown-impact-cpi.htm).

## What “every vintage” and “published on” mean here

The table retains every available initial publication and subsequent revised version for each measured month, through the cutoff. It does not select only today's final value. It also does not repeatedly copy an unchanged historical value into a new row whenever an unrelated month is released. This follows ALFRED's “New and Revised Observations Only” convention. [ALFRED download definitions](https://alfred.stlouisfed.org/help/downloaddata).

`Month measured` comes from the API observation date, displayed as YYYY-MM. An underlying first-of-month date identifies the measured month, not its publication day.

`Published on` comes from ALFRED's `realtime_start`: the first vintage date on which that particular version became available in the archive. It is the availability date used for this assignment. It is not the observation month, the retrieval date, or the end of the version's validity interval. For the missing marker, it identifies when the missing entry appears in ALFRED, not publication of a numeric CPI value.

ALFRED dates are daily, not intraday timestamps. ALFRED uses source release dates when available, provider dates next, and first FRED availability as a fallback. Do not assume this column independently verifies the precise source release time for trading within a day. [ALFRED Help](https://alfred.stlouisfed.org/help).

To reconstruct an as-of panel, retain publications on or before your decision date and then select the latest version for each measured month. Never substitute a later revision merely because it describes an earlier month.

## Example trade-date availability check

**The actual Lab 17 trade date has not been chosen.** Nicolas will choose it in lab. **March 31, 2026 is an illustrative example carried over from Lab 16**, not an approved Lab 17 decision date. To inspect that example, use the separate [as-of Excel table](CPIAUCSL_asof_2026-03-31.xlsx) or [as-of CSV](CPIAUCSL_asof_2026-03-31.csv). The original all-vintages files remain intact for the assignment.

The [standard-library selector](asof_cpi.py) filters by publication date first, then keeps the latest knowable publication for each series and measured month. Its default date is the March 31, 2026 example, inclusive. Replace it using `--decision-date` once the actual Lab 17 date is chosen.

| Step | Removed | Remaining |
| --- | ---: | ---: |
| All archived versions | — | 50 |
| Published after March 31 | 7 | 43 |
| Superseded by a version already known by March 31 | 23 | 20 |

The remaining panel contains **19 numeric observations and one missing marker**, covering July 2024 through February 2026. October 2025 remains missing, not zero or an interpolated value. The all-vintages archive's 26 numeric months do not imply that all 26 were knowable by March 31.

The latest knowable observation is **February 2026: 327.460**, published **March 11, 2026**. The BLS March release calendar lists that release at 8:30 a.m. Eastern on March 11. No retained observation has a March 31 publication date. Every retained month/value pair was independently matched to the official ALFRED snapshot for March 31. [BLS release calendar](https://www.bls.gov/schedule/2026/03_sched.htm).

From the AI Finance 2026 working directory, rebuild for a different trade date with:

```bash
./.venv/bin/python "NicolasCerioni/Project 2 FIN439/Lab 17/asof_cpi.py" --decision-date 2026-03-31
```

The command writes a date-labeled four-column CSV and an audit JSON giving every input row's inclusion or exclusion reason. It rebuilds the CSV and audit, not the formatted Excel copy. It rejects a decision date beyond the saved archive's October 29, 2026 cutoff. The archive covers only the measured months documented above, so earlier trade dates may have few or no available observations in this window.

**For a backtest, run the selector separately for every trade date.** Do not reuse the March 31 snapshot for trades before March 31. A revision known in February 2026 cannot be used for a trade made in 2024, even when the revision describes a 2024 month. Compute any monthly or year-over-year CPI changes from observations in the same trade-date snapshot, not by mixing vintages. Do not use future information to fill a missing month.

For same-day trades, verify that the release occurred before the trade time. The selector prints a warning if it includes a numeric value published on the decision date. If the release time has not been verified, add `--prior-day-only` to exclude all same-day publications. This produces a separately named CSV and audit. Availability filtering addresses publication/revision look-ahead; it does not by itself validate a trading strategy or eliminate other research biases.

## Three rows for Nicolas to check personally

**Personal checks completed and approved by Nicolas on October 29, 2026.** Nicolas confirmed in chat: “I have checked the dates and values and they are correct and I approve them.” This records his reported verification separately from the automated API checks. Approval of the checked data does not establish a Lab 17 trade date.

Open the [ALFRED series page](https://alfred.stlouisfed.org/series?seid=CPIAUCSL). Use its Download Data option and select or enter the three vintage dates below. Choose “Observations by Vintage Date, All Observations,” keep units as the original index level, and find the indicated measured month in the downloaded table. Confirm both the vintage date and value. ALFRED documents these download options in its [Download Data Help](https://alfred.stlouisfed.org/help/downloaddata).

| CSV data row (header excluded) | Month measured | Vintage / published on | Expected value | Your observed value | Your check date |
| ---: | --- | --- | ---: | --- | --- |
| 1 | 2024-07 | 2024-08-14 | 313.534 | 313.534 (confirmed by Nicolas) | 2026-10-29 |
| 2 | 2024-07 | 2025-02-12 | 313.566 | 313.566 (confirmed by Nicolas) | 2026-10-29 |
| 50 | 2026-09 | 2026-10-14 | 336.298 | 336.298 (confirmed by Nicolas) | 2026-10-29 |

- [x] Personally checked the initial July 2024 value.
- [x] Personally checked the revised July 2024 value.
- [x] Personally checked the September 2026 value.

The first two checks deliberately use the same measured month with different publication dates. They show why a later revised value cannot replace what was known earlier.

## Retrieval and verification

Retrieved through the official FRED/ALFRED API using the locally stored key. The key is absent from the tables, saved responses, and documentation. Raw JSON responses and credential-free request parameters are retained in `sources/`, including a manifest with a retrieval timestamp and CSV checksum.

Primary request: `fred/series/observations`, series CPIAUCSL, observation range 2024-07-01 through 2026-09-30, real-time range 1776-07-04 through 2026-10-29, original units, `output_type=1` (observations by real-time period). Every returned version was reshaped into the four-column table using its real-time start date. [Official endpoint documentation](https://fred.stlouisfed.org/docs/api/fred/series_observations.html).

Checks performed:

- Returned count reconciled to all 50 records; no pagination was omitted.
- Every month/publication/value tuple matched a separate `output_type=3` request for new and revised observations.
- All publication dates matched the series' vintage-date list and were on or before the cutoff.
- Confirmed 26 distinct months with numeric values, one missing month, and no duplicate month/publication/value tuples.
- Separately queried as-of snapshots for the three proposed personal-check rows; all values matched.
- Verified the Excel and CSV tables contain the same records and reviewed the Excel layout.

The saved CPI files are a static snapshot. The interactive app independently downloads current and historical public CSVs into its cache. Project files are published in the repository's `FedWebsiteUpdate (Lab 17)` folder; no public app hosting or automatic updating of the saved CPI archive is configured.
