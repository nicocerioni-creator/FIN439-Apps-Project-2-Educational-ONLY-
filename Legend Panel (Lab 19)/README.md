# Legend panel (Lab 19)

An educational Streamlit investment panel: **the same SEC facts, separate philosophies,
independent written judgments, and an auditable panel summary**. Built with AI help.
These are AI interpretations inspired by Warren Buffett, Cathie Wood, and Michael Burry,
not their actual opinions, research, holdings, or endorsements.

For educational and research purposes only. Not investment or other professional advice.
Historical results do not guarantee future results. The final investment verdict and
judgment belong to the investor, not the panel.

[GitHub project folder](https://github.com/nicocerioni-creator/FIN439-Apps-Project-2-Educational-ONLY-/tree/main/Legend%20Panel%20%28Lab%2019%29)

## Open the app

Python 3.11 or newer. From this folder:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run streamlit_app.py
```

Windows activation: `.venv\Scripts\activate`.

The app opens COST, its coded checks, and all three saved AI-written memos immediately,
without internet, credentials, API keys, or model downloads. Memos display side by side;
use **Stacked** for a wider reading area. Text labels identify every check result, so
status does not depend on color. Tables have accessible names and columns adapt to narrow screens.

Choose **Live SEC**, enter a ticker and a real SEC operator contact, and load a company
for refreshed facts. SEC access can be blocked or rate limited; the saved example remains
available. Unsupported issuers or tags produce missing evidence rather than estimates.
Never silently reuse the saved COST memos for a new snapshot or ticker.

## COST result and threshold choice

Saved SEC retrieval: November 17, 2026. Fiscal ends: August 28, 2022 through August 30, 2026.

| Investor | Check | Result |
|---|---|---|
| Warren Buffett | ROE at least 15% every year | pass |
| Warren Buffett | Owner earnings proxy positive every year | pass |
| Warren Buffett | Owner earnings proxy grew first year to last | pass |
| Cathie Wood | Revenue CAGR at least **5%** | **pass** |
| Cathie Wood | Latest R&D at least 5% of revenue | **not known** |
| Michael Burry | OCF at least net income every year | pass |
| Michael Burry | Latest liabilities no more than twice equity | pass |

Revenue CAGR is **7.51%**: `(last revenue / first revenue)^(1/4) - 1`.
Five annual observations span four annual intervals. The originally requested 15% Wood
growth threshold failed COST; the user then selected **5%**. Only the growth threshold
changed; the R&D threshold stays 5%. The reason is recorded in one line beneath Wood's
memo: a user-selected sensitivity test for a mature retailer, not a validated innovation hurdle.
Lowering a threshold after observing results can introduce confirmation bias; it does
not improve the underlying business or prove a disruptive-growth thesis.

Buffett: **own the business**. Wood: **watch it**. Burry: **own the business**.
Panel summary: **own the business**, provisionally, as a business-quality judgment only.
Wood's growth test passes, but unavailable R&D and insufficient innovation evidence
still justify watch it. Passing checks does not automatically determine a memo's verdict.
All saved memos pass the printed-number, snapshot, decision-line, and source-URL audits.

Trust the panel provisionally as a research aid. Its useful agreement is cash-backed
business quality; its split is whether that supports an innovation-focused mandate.
Shared SEC data and a shared AI author create correlated blind spots. This is not
independent confirmation by actual investors. No valuation, share-price attractiveness,
fraud finding, or short opportunity is established.

## No model API charges or exposed keys

The app contains no model integration, AI API client, key input, or owner's model account.
It does not run a paid model. It preserves Lab 18's bring-your-own-AI workflow:

1. Download a **separate investor packet** for each skill.
2. Give each packet to a fresh AI conversation without the other memos. Your chosen
   external service has its own pricing, terms, and usage limits.
3. Ask for Markdown, preserving the Snapshot line and exactly one Decision line.
4. Paste or upload each memo in its corresponding panel column.
5. Review the audit and citations, then download the final evidence/memos/skills ZIP.

Pasted and uploaded content stays in the app session/process and is not saved to the
repository. Only submit material appropriate for the host running the app. No secrets
are needed. `.env` and `.streamlit/secrets.toml` are ignored.

## What determines the panel result?

Each memo chooses `own the business`, `watch it`, or `pass`. Its skill has its own coded
checks and writing instructions. The saved memos were written by the same AI through
separate frameworks; they are not separate models or independent human votes.

Only after every memo passes the audit does a transparent aggregation rule apply:
at least two `own the business` verdicts produce that panel summary; at least two `pass`
verdicts produce `pass`; otherwise the summary is `watch it`. This is a display rule,
not a statistical confidence estimate. Missing memos or audit failures withhold synthesis
and default the displayed cautionary verdict to `watch it`.

The audit flags numerical occurrences absent from the printed output, including new
rounding, abbreviations, number words, or new calculations. It separately checks the
snapshot fingerprint, exactly one recognized decision, and supplied citation URLs.
It cannot prove that a printed number was used for the right metric or year, or that a
source actually supports a claim. Human review remains necessary. Zero numerical flags
does not mean all aspects of a memo are validated.

## Lab 18 evidence rules retained

- Only form exactly `10-K`, US-GAAP tags, USD facts. No amendments or quarterly financial values.
- Last five available fiscal-year-end `reportDate` values from SEC submissions, not a
  comparative fact's `fy`. Annual flows span 364, 365, 366, or 371 inclusive days.
- Latest eligible filing wins per metric/period; preferred tags break ties within a filing.
  Conflicting annual contexts become not found. Missing inputs yield not known checks.
- Revenue tags: `RevenueFromContractWithCustomerExcludingAssessedTax`, then `Revenues`.
- `NetIncomeLoss`, `NetCashProvidedByUsedInOperatingActivities`, `StockholdersEquity`,
  `Liabilities`, and the added `ResearchAndDevelopmentExpense`.
- Capital spending: `PaymentsToAcquirePropertyPlantAndEquipment`, then
  `PaymentsToAcquireProductiveAssets`. Preserve reported signs.
- ROE = net income / year-end equity. Owner earnings proxy = OCF − total capex, with
  matched annual periods. This is not Buffett's complete owner-earnings calculation.
- Nonpositive equity makes ROE and liabilities/equity not known. R&D intensity requires
  positive revenue and matching annual periods. Missing R&D is never set to zero.
- Checks use unrounded inputs, including exact Wood threshold comparisons. The CAGR
  display rounds to two decimals; it does not determine pass/fail.
- Retain accession, tag, filing date, reporting interval, and SEC URL for each fact.
- Selected 10-K/10-Q passages supply qualitative context only. Financial numbers in
  those excerpts are not allowed in memos unless printed in the script output.
- No estimates, forecasts, prices, targets, holdings, confidence scores, or news.

The source Wood/Burry philosophy material was supplied by the user as FAskills content.
It was adapted to the agreed evidence contract; its full forecast-heavy JSON templates
are intentionally not required. The checked-in `.agents/skills` folders are the reusable
skills; each new expert has its own `scripts/checks.py` operating on the shared report.
The Buffett skill and numerical pipeline are copied from Lab 18; Lab 18 itself is preserved.

## Reproduce and verify

```sh
python3 panel.py COST
python -m unittest discover -s tests -v
```

The CLI writes printed calculations, a source-linked `report.json`, and separate memo
packets to `outputs/COST/`. It also saves raw SEC responses under `sources/` locally;
raw responses are excluded from GitHub. Fresh AI memos are an explicit user step, not
automatically generated by the CLI. The completed demonstration includes the saved
memos, panel judgment, review, and export ZIP in `outputs/COST/`. `examples/` supplies
the stable app default. New downloads do not automatically replace the default example.

Tests cover the Lab 18 selection contract, exact thresholds, missing R&D, period
mismatches, nonpositive equity, revised Wood check, all memo audits, blocked synthesis,
exports, default app rendering, pasted numerical flags, and stacked reading.

## Public browser access

GitHub hosts the source and outputs; it does not itself run Streamlit. To create a
shareable browser app, use [Streamlit Community Cloud](https://share.streamlit.io/) and:

- Repository: `nicocerioni-creator/FIN439-Apps-Project-2-Educational-ONLY-`
- Branch: `main`
- Main file: `Legend Panel (Lab 19)/streamlit_app.py`
- No secrets or API keys. Use Python 3.12 or another supported version compatible with requirements.

Community Cloud can use the dependency manifest beside the entrypoint. Follow the
[official deployment instructions](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy).
No paid hosting, billing setup, or billable GitHub workflow is configured by this project.

## Primary sources

- [SEC EDGAR APIs](https://www.sec.gov/search-filings/edgar-application-programming-interfaces)
- [SEC scripted access](https://www.sec.gov/about/webmaster-frequently-asked-questions)
- [COST annual filing used for qualitative evidence](https://www.sec.gov/Archives/edgar/data/909832/000090983226000093/cost-20260830.htm)
- [COST quarterly filing used for qualitative context](https://www.sec.gov/Archives/edgar/data/909832/000090983226000051/cost-20260510.htm)
- [Streamlit documentation](https://docs.streamlit.io/)

- [FAskills Wood source philosophy](https://github.com/CinderZhang/FAskills/blob/main/financial-researcher/experts/cathie_wood.md)
- [FAskills Burry source philosophy](https://github.com/CinderZhang/FAskills/blob/main/financial-researcher/experts/michael_burry.md)

Deployment status: browser access reached Streamlit account setup, which requires completing profile fields and accepting its Terms of Service. No live app has been deployed. The owner must complete this account step before deployment can continue.
