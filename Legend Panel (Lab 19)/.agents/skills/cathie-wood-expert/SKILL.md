---
name: cathie-wood-expert
description: Review a US company's historical growth and R&D reinvestment through a Cathie Wood-inspired lens using Lab 19's shared SEC snapshot and coded checks. Use for a printed-numbers-only business-quality memo, without forecasts or valuation.
---

# Cathie Wood-inspired business review

Adapted from the FAskills expert material supplied by the user. This is an educational
interpretation, not Cathie Wood, ARK research, or an actual investor statement.
The Lab 18 evidence contract overrides the source template's demand for price targets,
TAM estimates, holdings, confidence scores, and predictions. Do not fabricate these fields.

## Evidence and checks

Run `python3 panel.py TICKER` from the Lab 19 project root. Read the printed
`outputs/TICKER/script_output.md` and `wood_memo_packet.md`. The sibling Buffett skill's
EDGAR script supplies the shared financial facts; `scripts/checks.py` here evaluates:

- Revenue CAGR at least 5%, from the first to last of five annual observations:
  `(last revenue / first revenue)^(1/4) - 1`. Use code's unrounded threshold result.
- Latest `us-gaap:ResearchAndDevelopmentExpense` at least 5% of matching annual revenue.

Only exact 10-K, USD, US-GAAP facts are eligible. Latest filing wins per metric/period;
preferred revenue tag wins within the same filing. Use Lab 18's annual period selection.
Missing data prints `not found`; a check without required inputs is `not known`.
Missing R&D is not zero and does not establish that the company does no innovation.
Research expense classification differs across industries; this screen can favor technology businesses.

## Independent memo

Use the supplied packet without reading the other panel memos. Assess growth and the
evidence for reinvestment, platform convergence, disruption, and cost advantages only to
the extent supported by cited filing passages. State when innovation claims, learning
curves, TAM, patents, or technology positioning cannot be established. A retailer can
be a good business while failing this growth screen. Do not invent a bearish price call.

Write direct prose with AI attribution and exactly one `Decision: own the business`,
`Decision: watch it`, or `Decision: pass` line. Preserve the exact `Snapshot:` line.
Use only financial numbers printed by the panel, with exactly the printed formatting.
No price targets, forecasts, scores, holdings, news, or outside numerical claims.
Include the coded results, the business-quality judgment, biggest uncertainty, evidence
that would change it, and a sentence explaining whether you trust this verdict.
Save `outputs/TICKER/wood_memo.md`; validate with `panel.audit_memo(memo, report)`.
Fix flags, snapshot or decision errors, and unknown citations before delivery.
The audit checks numerical vocabulary, not whether a statement is true.

Threshold kept: 5% annual revenue growth, selected by the user to test a mature retailer; this is a sensitivity choice, not an empirically validated innovation hurdle.

Source philosophy: [FAskills expert page](https://github.com/CinderZhang/FAskills/blob/main/financial-researcher/experts/cathie_wood.md). Use the adapted evidence rules above for this lab.
