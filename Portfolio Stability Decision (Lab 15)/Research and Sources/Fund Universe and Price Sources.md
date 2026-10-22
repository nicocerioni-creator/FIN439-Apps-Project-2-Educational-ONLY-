# Lab 15 — Fund Universe, Mandate, and Price Sources

Prepared and data downloaded: **October 22, 2026**. AI-assisted preparation for FIN 439, Project 2.

## My mandate and selected hard constraint

My client has a $10 million family trust supporting four children over their lifetimes, with an initial 20-year planning period. The comparison benchmark is the S&P 500 Total Return Index.

**Numerical objective: target a 10.0% nominal annualized portfolio total return.** For this exercise, interpret annualized performance as compounded growth over the five-year evaluation period, before trust-level taxes and administration costs. This is a target, not a guaranteed return or an independently established expected return.

**One hard constraint for this exercise: annualized portfolio return volatility must be no greater than 25.0%.** Proposed measurement definition: calculate monthly portfolio total returns, take their sample standard deviation over the latest 60 completed months, and multiply by the square root of 12. Evaluate monthly; a breach flags the portfolio for review. This makes the mandate's previously unspecified measurement convention explicit. A 25% volatility limit is not a 25% maximum-loss guarantee.

This selects one constraint for the lab; it does not cancel the full mandate's education payments, lifetime distributions, or turnover limit. No portfolio weights have been selected or compliance established.

## Selected universe: six equity ETFs and one Treasury reserve ETF

| Ticker | Fund and primary source | Intended role |
|---|---|---|
| VOO | [Vanguard S&P 500 ETF](https://advisors.vanguard.com/investments/products/voo/vanguard-sp-500-etf) | Broad U.S. large-company core; aligned with the mandate's benchmark exposure. |
| QQQ | [Invesco QQQ Trust, Series 1](https://www.invesco.com/us/en/financial-products/etfs/invesco-qqq-trust-series-1.html) | Nasdaq-100 growth tilt. |
| SCHD | [Schwab U.S. Dividend Equity ETF](https://www.schwabassetmanagement.com/products/schd) | Dividend/value emphasis; dividends do not guarantee payment coverage. |
| PAVE | [Global X U.S. Infrastructure Development ETF](https://www.globalxetfs.com/funds/pave) | Infrastructure development exposure. |
| XLE | [State Street Energy Select Sector SPDR ETF](https://www.ssga.com/us/en/individual/etfs/state-street-energy-select-sector-spdr-etf-xle) | Traditional energy exposure. |
| XLV | [State Street Health Care Select Sector SPDR ETF](https://www.ssga.com/us/en/individual/etfs/state-street-health-care-select-sector-spdr-etf-xlv) | Healthcare exposure. |
| SGOV | [iShares 0-3 Month Treasury Bond ETF](https://www.ishares.com/us/insights/portfolio-insights/cash-alternatives-put-cash-to-work-sgov) | Short-term Treasury reserve candidate, added October 22, 2026. Treat as reserve-eligible for the classroom model; this designation is an assumption, not an independently approved mandate amendment. |

These funds narrow my existing ten-fund research list to six. VOO fills the core role, so SCHB is omitted as a substantially overlapping broad-market alternative. QQQ supplies a growth tilt without adding separate AIQ and SMH positions; PAVE represents infrastructure instead of the narrower GRID theme. These are selection judgments, not optimal-weight conclusions.

The original six funds form the equity portion; SGOV was subsequently added to permit a Treasury reserve allocation. Sector funds overlap with VOO and may increase concentration. Six equity tickers do not create six independent sources of risk. This universe alone does not establish that the full trust's future payments can be funded reliably.

## Price file and sources

File: **prices.csv**, in this folder. Updated layout: `Date,VOO,QQQ,SCHD,PAVE,XLE,XLV,SGOV`. Dates appear first, oldest first, with one USD adjusted-close price column per ticker. The original six-fund CSV is preserved as `sources/prices_before_SGOV_2026-10-22.csv`.

| Ticker | Historical price source | Download date |
|---|---|---|
| VOO | [Yahoo Finance historical prices](https://finance.yahoo.com/quote/VOO/history/) | 2026-10-22 |
| QQQ | [Yahoo Finance historical prices](https://finance.yahoo.com/quote/QQQ/history/) | 2026-10-22 |
| SCHD | [Yahoo Finance historical prices](https://finance.yahoo.com/quote/SCHD/history/) | 2026-10-22 |
| PAVE | [Yahoo Finance historical prices](https://finance.yahoo.com/quote/PAVE/history/) | 2026-10-22 |
| XLE | [Yahoo Finance historical prices](https://finance.yahoo.com/quote/XLE/history/) | 2026-10-22 |
| XLV | [Yahoo Finance historical prices](https://finance.yahoo.com/quote/XLV/history/) | 2026-10-22 |
| SGOV | [Yahoo Finance historical prices](https://finance.yahoo.com/quote/SGOV/history/) | 2026-10-22 |

Actual downloads used Yahoo Finance's chart endpoint, `https://query1.finance.yahoo.com/v8/finance/chart/{TICKER}`, with `interval=1d`, `includeAdjustedClose=true`, and a September 1, 2021 inclusive to October 1, 2026 exclusive date window. Exact request URLs and UTC retrieval timestamps are saved in [sources/price_download_manifest.json](sources/price_download_manifest.json); original responses are preserved alongside it as `{TICKER}_yahoo_daily_2026-10-22.json`.

The original manifest describes the original six equity columns. SGOV's matching request, retrieval timestamp, and monthly observations are saved separately in [sources/SGOV_price_download_manifest.json](sources/SGOV_price_download_manifest.json), with its raw response in `sources/SGOV_yahoo_daily_2026-10-22.json`. The six original CSV columns were preserved exactly when SGOV was appended.

Method: select each calendar month's final available trading-day observation from the returned `indicators.adjclose[0].adjclose` field. Retain the actual trading date and full returned numerical precision. No interpolation, forward filling, averaging of daily prices, or substitution of ordinary Close was used. [Yahoo's adjusted-close explanation](https://in.help.yahoo.com/kb/adjusted-close-sln28256.html) describes adjustments for splits and cash distributions. Adjusted prices are analytical values, not historical transaction prices; the vendor may revise them after later corporate actions.

Coverage: **September 30, 2021–September 30, 2026**. There are **61 month-end price observations per fund**, providing exactly **60 monthly return intervals**, or five years of returns. The first observation is the starting-price anchor. October 2026 is excluded because it is incomplete.

## Historical return estimates — not forecasts

For each fund, monthly simple total-return proxy: `r[t] = AdjClose[t] / AdjClose[t-1] - 1`.

The sample-based return estimate below is **12 × the arithmetic mean of the 60 monthly returns**. It estimates the historical annualized arithmetic mean; it is not the compounded return actually earned and is not a forecast. Historical CAGR is shown separately as `(ending price / starting price)^(1/5) - 1`.

| Ticker | Historical annualized arithmetic mean estimate | Historical realized CAGR |
|---|---:|---:|
| VOO | 14.18% | 13.77% |
| QQQ | 17.35% | 16.32% |
| SCHD | 10.19% | 9.46% |
| PAVE | 17.87% | 16.45% |
| XLE | 24.13% | 23.00% |
| XLV | 8.31% | 7.49% |

SGOV was added after this original six-fund return table. Its annualized arithmetic mean over the same 60 monthly returns is 3.72%, and its sample annualized volatility is 0.50%. These are historical estimates, not current yields or forward forecasts.

These calculations use the saved CSV, with rounding only for this table. They are adjusted-market-price return proxies, not issuer-reported NAV returns, and contain no separate deduction for trust costs or personal taxes. Do not deduct fund operating expenses a second time from the fund price series. **A five-year average is history, not a forecast.** No forward-looking return estimate has been established. The 10% objective remains a separate mandate target.

## Verification

- Confirmed six ETF tickers, USD denomination, and use of the source's adjusted-close field.
- Confirmed 61 unique dates in ascending order, identical month-end trading dates across all funds, one observation per month, and no unfinished month.
- Confirmed all 366 prices are positive, finite, and present; all six series produce 60 monthly returns.
- Checked the spreadsheet price matrix against downloaded values before CSV export and visually reviewed a preview. The CSV contains only dates, ticker headers, and prices.
- Original ETF research and Lab 13/14 assignments were preserved.

### Reserve addition verification

- Matched all 61 SGOV month-end trading dates to the existing CSV, retaining 60 monthly return intervals for seven assets and 427 positive, finite adjusted-close prices.
- Compared every original date and equity price string against the preserved six-fund CSV; all unchanged.
- Loaded the revised CSV through `estimate_from_csv` for all 60 and the latest 36 returns. With SGOV designated reserve-eligible, searches found feasible mixes at both 6.5% and 10% objectives with a 3% reserve minimum. This verifies model behavior, not future performance or full mandate compliance.
- In the current app, uploaded assets start unticked. Re-upload the revised CSV and check only SGOV as reserve-eligible for this exercise. The five-percentage-point grid requires at least 5% in eligible assets to meet a 3% minimum.
- None of VOO, QQQ, SCHD, PAVE, XLE, or XLV is designated reserve-eligible. SGOV's short Treasury maturities make it a more suitable reserve candidate than TLT's 20-plus-year bonds, which carry substantial interest-rate exposure. The app's checkbox does not determine actual mandate eligibility.
