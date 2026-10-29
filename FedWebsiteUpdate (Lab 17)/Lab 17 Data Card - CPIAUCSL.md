# Lab 17 Data Card — CPIAUCSL

## Source, measurement, and download date

| Field | Details |
| --- | --- |
| Series ID | **CPIAUCSL** |
| Series name | Consumer Price Index for All Urban Consumers: All Items in U.S. City Average |
| Original producer | U.S. Bureau of Labor Statistics (BLS) |
| Distributor | FRED and ALFRED, Federal Reserve Bank of St. Louis |
| FRED page | https://fred.stlouisfed.org/series/CPIAUCSL |
| ALFRED page | https://alfred.stlouisfed.org/series?seid=CPIAUCSL |
| What it measures | Changes in prices paid by urban consumers for a basket of goods and services. It is a consumer-price index, not a fund price or investment return. |
| Frequency and adjustment | Monthly, seasonally adjusted |
| Units | Index, 1982–1984 = 100. The level is not an inflation percentage. |
| Download and page-check date | **October 29, 2026** |
| Comparison dates tested | September 30, 2026 (last day of last month), then October 29, 2026 (today) |
| Chart and revision-count window | January 1, 2020 onward |

The definition, frequency, and units were checked on the [FRED series page](https://fred.stlouisfed.org/series/CPIAUCSL). Public CSV downloads were used without an API key or account. No credentials were read or included in this card.

## Publication lag

CPI normally becomes available during the following month, roughly two weeks after the measured month ends; use actual release dates rather than assuming a constant lag. For this check, **September 2026 CPI was released October 14, 2026 at 8:30 a.m. Eastern**, 14 calendar days after September month-end. Thus the September value was not knowable on September 30. [BLS October release calendar](https://www.bls.gov/schedule/2026/10_sched.htm).

The measured date `2026-09-01` labels September. It does not mean that the observation was published on September 1. A trading decision earlier on release day still requires a release-time check; a daily vintage label alone cannot establish intraday availability.

## Revisions

**Yes, this seasonally adjusted series can be revised.** BLS re-estimates seasonal factors annually, and previously published seasonally adjusted indexes are subject to revision for up to five years. This differs from treating unadjusted CPI as routinely revised for late survey responses. [BLS CPI FAQ, “When should I use seasonally adjusted data?”](https://www.bls.gov/cpi/questions-and-answers.htm).

There were **zero changed numeric values on common dates** between the September 30 snapshot and today's download in the start-2020 window. That describes this short comparison interval, not the series' entire revision policy. The saved vintage history provides a direct counterexample: July 2024 was initially 313.534, revised to 313.566, and later to 313.569.

## App comparison: last month-end, then today

| Requested as-known date | Latest CPI month known | Value then | Today's value for that same month | Later observations today | Revised values |
| --- | --- | ---: | ---: | ---: | ---: |
| 2026-09-30 | August 2026 | 334.131 | 334.131 | 1 | 0 |
| 2026-10-29 | September 2026 | 336.298 | 336.298 | 0 | 0 |

The September observation disappears when the cutoff is moved back to September 30 because it had not yet been published. It must not be inserted into a September 30 signal.

For the October 29 CPI request, ALFRED returned a CSV labeled **October 28**. The app displays that earlier returned snapshot date and rejects any returned snapshot later than the requested cutoff. Its CPI values matched today's FRED values in this check. This is conservative use of the returned snapshot, not a claim to verify every intraday update on October 29.

### Daily market-rate comparison

**DGS10 shows almost no publication lag and no revisions in this comparison.** On September 30, its latest available measured date was September 29, at 5.26%. On October 29, its latest measured date was October 28, at 5.05%. That is approximately a one-business-day lag, rather than CPI's multiweek lag. The overlapping-date revision count was **0**, and there were **20** later numeric daily observations. Missing days are excluded from that count.

This observed zero is not a universal promise that a data correction can never occur. DGS10 is a daily Treasury market-yield series, not a monthly survey estimate. [FRED DGS10 page](https://fred.stlouisfed.org/series/DGS10).

### PAYEMS check that the two downloads are different

With the cutoff set to **January 15, 2025**, PAYEMS's latest measured month was December 2024, at **159,536 thousand jobs**. Today's value for that same month was **158,316**, with **59** revised numeric monthly values in the start-2020 window. This live check confirms the historical and current downloads were not simply today's values read twice. PAYEMS remains selectable; January 15 is a test example, not a chosen Project 2 trading date.

## Three values checked directly against the FRED page

The assistant read these three values on the [FRED CPIAUCSL page](https://fred.stlouisfed.org/series/CPIAUCSL) on October 29, 2026 and matched them to the current public CSV. This is a separate assistant check from Nicolas's earlier approved source checks.

| Month measured | FRED page value | Downloaded CSV value | Result |
| --- | ---: | ---: | --- |
| July 2026 | 332.813 | 332.813 | Match |
| August 2026 | 334.131 | 334.131 | Match |
| September 2026 | 336.298 | 336.298 | Match |

Recorded comparison results and returned CSV headers are in [sources/lab17_data_card_checks.json](sources/lab17_data_card_checks.json).

## Project 2 admission decision — QUARANTINE

**Quarantine:** CPIAUCSL is published after the measured month, and its seasonally adjusted history can be revised annually. September 2026's 336.298 was not available on September 30. Today's historical values with a fixed lag would still introduce later revisions. Admit only the vintage available on each actual decision date, with release timing verified for same-day trades and missing months left missing.

The source data have been checked and approved; the quarantine applies to using them in Project 2 historical trading signals. The actual Lab 17 decision date or trading schedule has not yet been chosen. The March 31 panel remains an example only.

**What would change the decision to Admit:**

1. Choose and record the actual decision dates and trade-time convention.
2. Build a separate as-of snapshot for every decision date, filtering availability before selecting revisions. Never apply today's revised history with a fixed calendar lag.
3. Verify release timing for same-day use, or exclude same-day publications when timing is unknown.
4. Keep `.` as missing, including October 2025. Any inflation-change calculation requiring a missing month must stay unavailable rather than use future data to fill it.
5. Confirm the values used in each signal agree with the appropriate ALFRED snapshot, and retain the selection audit.

Successful admission would establish eligibility as a point-in-time research input. It would not establish that CPI predicts fund returns or that a trading strategy is profitable. Inflation's relevance to the Project 2 universe remains a hypothesis to test.

## Educational and research purposes only

This lab, including its code, data, analyses, and outputs, is for educational and research purposes only. It is not investment, financial, legal, tax, or other professional advice, or a recommendation or solicitation to buy or sell securities. Historical results do not guarantee future performance.
