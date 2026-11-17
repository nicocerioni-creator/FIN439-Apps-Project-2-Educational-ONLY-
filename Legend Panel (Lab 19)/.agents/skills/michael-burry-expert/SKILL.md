---
name: michael-burry-expert
description: Review cash-backed earnings and reported balance-sheet leverage through a Michael Burry-inspired lens using Lab 19's shared SEC snapshot and coded checks. Use for a skeptical printed-numbers-only memo, without short calls or price targets.
---

# Michael Burry-inspired business review

Adapted from the FAskills expert material supplied by the user. Educational AI analysis,
not Michael Burry, Scion research, or an actual investor statement. Lab 18's evidence
contract overrides demands in the source template for prices, predictions, holdings,
confidence scores, mispricing estimates, or unsupported forensic accusations.

## Evidence and checks

Run `python3 panel.py TICKER` from the Lab 19 project root. Read the shared
`outputs/TICKER/script_output.md` and `burry_memo_packet.md`. The sibling Buffett skill's
EDGAR script selects facts; `scripts/checks.py` in this skill checks:

- Operating cash flow at least net income in every year of the five-year window,
  using matching annual start/end dates.
- Latest reported `us-gaap:Liabilities` no more than twice
  `us-gaap:StockholdersEquity`. Missing or nonpositive equity makes this not known.

Use exact 10-K, USD, US-GAAP facts and Lab 18's annual selection. Latest filing wins
per metric/period. Missing data is not zero. Incomplete required inputs yield `not known`.
Liabilities are total reported liabilities, not merely debt. Do not infer hidden items.

## Independent memo

Read no other investor's memo. Question whether cash supports earnings, whether leverage
is manageable, and what the supplied filing evidence fails to establish. Construct a
qualitative bear case from available evidence. Do not infer channel stuffing, fraud,
hidden liabilities, insider actions, consensus sentiment, or accounting tricks from
these simple ratios. Cash above net income is supportive but can reflect working capital.
Passing this screen does not establish valuation attractiveness or a complete forensic review.

Write a short AI-attributed memo with exactly one standalone decision line:
`Decision: own the business`, `Decision: watch it`, or `Decision: pass`.
Preserve `Snapshot:` exactly. Cite only supplied filing URLs. Use only printed financial
numbers in their exact formatting. Include coded results, a skeptical business-quality
judgment, the biggest uncertainty, evidence that changes it, and whether you trust the
verdict. No projections, scores, numerical price targets, or implied personal endorsement.
Save `outputs/TICKER/burry_memo.md`. Validate with `panel.audit_memo(memo, report)`;
fix numerical flags, snapshot or decision errors, and unknown citations before delivery.
Human review must still check the meaning of claims and support in the filing text.

Source philosophy: [FAskills expert page](https://github.com/CinderZhang/FAskills/blob/main/financial-researcher/experts/michael_burry.md). Use the adapted evidence rules above for this lab.
