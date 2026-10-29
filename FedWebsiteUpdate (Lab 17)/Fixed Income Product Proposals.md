# Fixed-income product proposals — approval required

Research date: October 29, 2026. Target user: **individual fixed-income investors**, as selected by Nicolas.

Current status: **additional product improvements deferred at Nicolas's request**. Publication of the existing Lab 17 app does not approve implementation of the proposals below.

## What is implemented and authorized

Nicolas requested an Apple-inspired interface, clear links, graph checkboxes, reset controls for dates and axes, and graph overlays. Nicolas separately approved an optional **start-at-100** overlay for comparing different units. Those interface changes are implemented. The app retains its public no-key CSV downloads and historical-value checks.

**Every additional feature below is a proposal, not an implemented feature.** No alerts, accounts, brokerage connections, portfolio uploads, subscriptions, deployment, or new data services have been added.

## What the research suggests

Apple's site provides useful visual references: restrained colors, clear typography, generous spacing, and prominent primary/secondary links. The app adopts those principles through Streamlit's native theme and components rather than copying Apple's branding or product imagery. [Apple](https://www.apple.com/).

Yahoo's own app guide emphasizes user-organized watchlists, chart comparisons, and custom alerts. A commenter in an investor discussion praised the ability to quickly scan a watchlist's daily performance. This is a useful signal about convenience, not a representative study or proof of fixed-income demand. [Yahoo's app guide](https://in.help.yahoo.com/kb/started-yahoo-finance-mobile-ios-sln22069.html), [investor discussion](https://www.reddit.com/r/stocks/comments/m2pxet/if_you_had_to_subscribe_to_one_of_the_services/).

Bloomberg's consumer app offers market data, a watchlist, news, and alerts. A visible App Store reviewer criticized excessive clicks and interruption recovery in audio playback. The lesson I would carry over is to keep frequent tasks obvious and preserve the user's working state; this is not evidence that its full interface should be copied. The consumer news app is also distinct from the Bloomberg Terminal. [Bloomberg App Store listing and reviews](https://apps.apple.com/us/app/bloomberg-business-news-daily/id281941097).

Investopedia is useful here primarily as a reference for approachable explanations of bond concepts, not as a claim that investors prefer a particular trading interface. Its bond-ladder and duration explainers suggest educational context that could sit beside practical planning tools. [Bond ladders](https://www.investopedia.com/terms/b/bondladder.asp), [duration](https://www.investopedia.com/terms/d/duration.asp).

For a concrete fixed-income product example, Fidelity offers a bond-ladder tool. It is more directly relevant to an individual investor's income and maturity planning than a general stock-news feed. [Fidelity bond-ladder tool](https://www.fidelity.com/fixed-income-bonds/fixed-income-tools-services/bond-ladder-tool).

These are selected official product descriptions, editorial references, and individual user comments. Reviewer identities and actual investment experience were not independently verified. They support hypotheses for testing, not a market-size estimate or willingness-to-pay conclusion.

## My assessment of the product

The current app is an economic-data explorer with point-in-time comparisons. It is not yet a bond screener, an income planner, or a portfolio risk engine. Better visual design helps usability, but a chart viewer alone is a weak paid proposition when FRED and other charting tools are available free.

My recommended positioning to test: **a simple workspace for individual bond investors to understand rates, plan income, and see exactly what information was available at the time**. The historical audit is a differentiator; whether individual investors value it enough to pay remains uncertain. Interview prospective users about a recent decision and observe them performing that task before committing to a large build.

## Additional features — none implemented

| Priority | Proposal | User benefit | Scope and dependency | Approval |
| --- | --- | --- | --- | --- |
| 1 | Saved workspaces and preferences | Reopen chosen series, chart mode, dates, colors, and ranges without rebuilding the view. | Start with local preference import/export, without brokerage access. Cross-device sync would be a separate decision. | Pending |
| 2 | Treasury yield curve and basis-point comparisons | Compare short- and long-term yields, and show changes in the units bond investors use. | Add explicitly selected Treasury series, align measurement/publication dates, and label any spread's construction. Do not call mismatched-maturity spreads pure default-risk measures. | Pending |
| 3 | Income and maturity planner | See when interest payments and principal would arrive; explore a Treasury/CD ladder. | Begin with manually entered contractual cash flows. Handle maturity, coupons, calls, and reinvestment assumptions explicitly. This is a planning demonstration, not a claim of executable inventory. | Pending |
| 4 | Interest-rate sensitivity scenarios | Explore how a chosen yield move might affect a bond or fund. | Requires duration and, where available, convexity inputs. Show approximations and assumptions instead of presenting scenario estimates as certain returns. | Pending |
| 5 | Release, freshness, and revision panel | Distinguish old data, newly published observations, and revised history at a glance. | Use release metadata and actual retrieval times. Background alerts require a running service and separate notification approval. | Pending |
| 6 | Short, contextual explanations | Explain yield, coupon, maturity, duration, basis points, and credit spreads where the user encounters them. | Keep the main screen concise, with optional explanations and worked examples. | Pending |
| 7 | More appearance choices | Let users choose light/dark appearance, compact/comfortable spacing, and accessible palettes. | The current light theme is implemented; these additional user-facing preference options are not. | Pending |
| 8 | Shareable research exports | Export a chart plus its source, units, retrieval date, and vintage cutoff. | Export only approved data and the user's chosen scope. No account or public publishing is needed for a first version. | Pending |

My preferred next step is **saved workspaces plus Treasury curve/basis-point comparisons**: these extend the current tool without immediately introducing private holdings or a large pricing-data dependency. If the first customers are retirees planning cash needs, prioritize the income planner instead. If they are research-focused individual investors, prioritize the revision/freshness panel and reproducible exports.

## Commercial data constraint to resolve

Free download access is not blanket permission to redistribute every series commercially. The current BAA page identifies Moody's data as proprietary and states that redistribution requires prior written consent. Resolve that source's permissions, or replace/remove that source for a commercial offering, before selling a product that republishes it. This is an actual constraint in the current data set, not a reason to stop the local coursework demo. [BAA source and usage notice](https://fred.stlouisfed.org/series/BAA).

## Approval record

- Approved: requested interface controls and Apple-inspired visual polish.
- Approved in chat: individual fixed-income investors as the initial audience.
- Approved in chat: optional start-at-100 comparison, clearly labeled as relative trends rather than investment returns.
- Pending: all eight additional feature proposals above. Ask Nicolas before implementing any of them.

## Educational and research purposes only

This project and proposal are for educational and research purposes only. They do not constitute investment, financial, legal, tax, or other professional advice, or a recommendation or solicitation to buy or sell securities. Historical observations and hypothetical scenarios do not guarantee future results.
