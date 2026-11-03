# Legend Investor as a Skill (Lab 18)

A reusable AI skill and Streamlit demonstration: code computes the financial evidence;
the AI judges business quality as **own the business**, **watch it**, or **pass**.

For educational and research purposes only. Built with AI help. Not investment or other
professional advice. No guarantee of future results. Buffett-inspired AI analysis is not
an actual statement by Warren Buffett or Berkshire Hathaway.

## Run the app

Use Python 3.11 or later. From this folder:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run streamlit_app.py
```

Windows activation: `.venv\Scripts\activate`.

The app initially opens a saved AAPL SEC snapshot and AI-written memo without network
access, credentials, or model downloads. Enter `COST` and click **Load company** to view
the saved Costco example, including its verdict-confidence sentence. Choose **Live SEC**, enter a ticker, and click
**Load company** for fresh financials and qualitative filing excerpts. Data can change
when a new filing is published. SEC/network restrictions can temporarily block live access;
the included example remains available. Foreign issuers without 10-Ks or the specified
US-GAAP USD tags may have missing data or be unsupported.

## Fresh AI memos without exposing a key

The app makes **no paid AI API calls**, collects no API keys, and has no owner's model
account to charge. It does not automatically run a model inside Streamlit.

1. Load a company and download its memo packet.
2. Paste the contents of `memo_packet.md` into your chosen AI chat, or attach that file.
3. Ask for the memo as Markdown. Preserve its snapshot line and add exactly one decision
   line: `Decision: own the business`, `Decision: watch it`, or `Decision: pass`.
4. Save the answer as `TICKER_memo.md`, upload it in the app, or paste its contents.
5. Review the unsupported-number list, snapshot status, citation warnings, and the memo.
   Download the final Markdown to save it permanently.

Use your own AI account subject to its pricing and usage limits; a free plan may be
sufficient but is not guaranteed. No visitor can spend the author's API tokens through
this app because it contains no model integration. Running locally requires no purchased
hosting. A GitHub repository contains code; a public browser demo needs separate hosting.
No deployment, paid hosting, or billable GitHub automation is configured by this project.

Uploads and pasted text are held in the browser session/app process, not written into the
repository. On shared hosting, only upload material you are comfortable sending to that
host. The download ZIP includes the exact numerical snapshot and the reusable skill.

## Use the installed skill

The shareable skill is `.agents/skills/buffett-business-review/`. Codex discovers skills
from `.agents/skills` in the working directory/ancestors and `~/.agents/skills` for user
skills. This project also links a personal installation on the author's computer. For your own
setup, copy the skill folder to your user skills directory or open Codex in this Lab folder.
Invoke `$buffett-business-review` and give it a ticker. If the selector does not refresh,
restart the app. See [official skill locations](https://learn.chatgpt.com/docs/build-skills).

The skill's script runs without Streamlit or third-party packages:

```sh
python3 .agents/skills/buffett-business-review/scripts/edgar.py AAPL --output outputs
```

It prints the numbers and XBRL tags and saves `report.json`, `report.md`, `memo_packet.md`,
and raw SEC source responses under `outputs/AAPL/`. The AI following the skill writes
`outputs/AAPL/AAPL_memo.md`. Validate a memo independently with:

```sh
python3 .agents/skills/buffett-business-review/scripts/memo_validation.py outputs/AAPL/report.json outputs/AAPL/AAPL_memo.md
```

The SEC User-Agent identifies Nicolas Cerioni and the authorized contact email. Forks
should set their own contact, through the app sidebar or the `SEC_USER_AGENT` environment
variable. This contact is sent to SEC and is not an API key. No credential files are needed.

## Numerical contract

- Only facts from form exactly **10-K**, not 10-K/A, 10-Q, or other forms.
- Last five available fiscal years, labelled by fiscal-year-end `reportDate` from 10-K
  submissions, not the `fy` field on comparative XBRL facts. If fewer are available,
  show those available and mark five-year checks `not known`.
- Flows use annual start/end intervals of 364, 365, 366, or 371 inclusive days, allowing 52/53-week
  fiscal years. Partial transition years are excluded. Instant equity uses year end.
- The latest eligible filing wins for each metric/period across allowed tags. Within the
  same filing, the preferred tag wins; ambiguous annual contexts become `not found`.
- Revenue: `RevenueFromContractWithCustomerExcludingAssessedTax`, then `Revenues`.
- Net income: `NetIncomeLoss`.
- Operating cash flow: `NetCashProvidedByUsedInOperatingActivities`.
- Capital spending: `PaymentsToAcquirePropertyPlantAndEquipment`, then
  `PaymentsToAcquireProductiveAssets`. Preserve reported signs; do not estimate maintenance spending.
- Equity: `StockholdersEquity`. Supplemental liabilities: `Liabilities`.
- ROE = net income / year-end equity, displayed as a percentage; thresholds use unrounded
  amounts. Liabilities/equity and ROE are `not known` with nonpositive equity or missing inputs.
- Owner earnings **proxy** = operating cash flow − total capital spending, only when the
  annual periods match. This is not Buffett's complete owner-earnings definition.
- Missing reported values print `not found`, never an estimate. Missing check inputs yield
  `not known`, including when the five-year window is incomplete.
- Checks: ROE at least 15% in every year; owner earnings strictly positive every year;
  last-year owner earnings strictly greater than first-year owner earnings. The growth
  check compares endpoints; it does not require growth in every intervening year.
- Source accession, filing date, period, tag, and SEC URL accompany each selected fact.
  Comparative facts may originate in later 10-Ks, reflecting the latest-filing rule.
- Qualitative evidence: automatically selected passages from the latest available 10-K
  and latest 10-Q. Excerpts are incomplete and may be older/newer than each other.
  They cannot establish all aspects of moat, competence, or management quality.
- No financial numbers from 10-Q passages, news, prices, forecasts, or invented scores
  may be added to the memo. Passing a screen does not establish business quality.

## Number-check limitations

The audit compares numerical occurrences against printed financial values, fiscal-year-end
dates, and the specified ROE threshold. It accepts comma/currency formatting variations,
but conservatively flags number words, new rounding, abbreviations, and new calculations.
URL identifiers, filing labels, snapshot IDs, and filing-date citation metadata are not
financial claims. Unknown citation URLs and mismatched snapshots get separate warnings.

A number appearing in the script output can still be misused in a sentence. The audit
cannot verify the meaning of a claim, detect every linguistic expression of quantity,
or prove a citation supports a qualitative assertion. Human review is essential.

## Verify

```sh
python -m unittest discover -s tests -v
```

The suite covers annual selection, comparative filing revisions, tag precedence, missing
inputs, zero/negative equity, exact thresholds, and number validation; Streamlit's headless
AppTest covers example rendering and pasted memos. No paid API or browser server is needed.

## Sources

- [SEC EDGAR APIs](https://www.sec.gov/search-filings/edgar-application-programming-interfaces)
- [SEC scripted access and User-Agent](https://www.sec.gov/about/webmaster-frequently-asked-questions)
- [Streamlit documentation](https://docs.streamlit.io/)
- [Official Codex skill locations](https://learn.chatgpt.com/docs/build-skills)

The saved example contains its retrieval timestamp, financial snapshot fingerprint, and
SEC source links. Source SHA-256 values identify the downloaded facts and filing content;
raw downloads from the CLI stay in the ignored `outputs/` folder.
