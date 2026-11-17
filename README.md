# FIN 439 — Project 2 (in progress)

AI attribution: OpenAI Codex helped develop and document the lab code and prepared this reproducibility command and README. Analysis and final decisions remain the student's responsibility.

**Educational and research purposes only. This is not investment or other professional advice, and estimated or historical results do not guarantee future performance.**

**Status — November 17, 2026: Project 2 is still being updated. The result below is the current Lab 15 portfolio demonstration, NOT the final Project 2 decision. The final family-trust allocation and adoption recommendation are pending.**

## Reproduce the current result with one command

Prerequisite: Python 3.10 or newer, available as `python3`. Download this repository using **Code → Download ZIP** and extract it, or clone it. Open a terminal in the extracted/cloned repository's top-level folder (the folder containing this README), then run:

```bash
python3 reproduce_decision.py
```

This command uses Python's standard library and the repository's existing [Lab 15 calculation engine](Portfolio%20Stability%20Decision%20%28Lab%2015%29/portfolio.py). It recalculates the three baselines, searches for the lowest-volatility feasible allocation, and prints the weights, return, volatility, reserve weight, and failed return/reserve checks. No package installation, API key, account, internet connection after download, or private local files are required. It prints to the terminal without launching the web app or changing saved inputs.

## Expected result, readable without running code

Under the saved **Meridian classroom assumptions**, a feasible minimum-volatility grid mix exists:

| Sleeve | Weight |
| --- | ---: |
| Treasury bills | 0% |
| Treasury 10-year note | 20% |
| Investment-grade bond fund | 25% |
| Global equity index fund | 55% |

| Portfolio | Estimated annual return | Annual volatility | Reserve-eligible weight | Lab return/reserve checks |
| --- | ---: | ---: | ---: | --- |
| Benchmark: 60% equity / 40% bonds | 6.80% | 10.46% | 0.0% | FAIL: reserve below minimum |
| Equal weight | 5.20% | 5.21% | 50.0% | FAIL: return below objective |
| Inverse volatility | 3.77% | 1.05% | 90.3% | FAIL: return below objective |
| Lowest-risk feasible grid mix | 6.51% | 9.44% | 20.0% | PASS |

These checks cover the lab's estimated-return and reserve requirements only. They are not full Project 2 mandate verdicts. The current result supports further classroom evaluation of the feasible mix; it does not establish approval for the family trust.

## Inputs, method, and limits

- The command uses the four-sleeve Meridian defaults in `portfolio.py`, matching the Lab 15 app's initial settings. It does **not** load the separate seven-ETF `prices.csv` or use live prices.
- Annual return assumptions are 3.5% for bills, 4.3% for the 10-year note, 5.0% for investment-grade bonds, and 8.0% for global equities. Annual volatility assumptions are 0.5%, 7.0%, 6.0%, and 16.0%, respectively; the saved correlation matrix is in the calculation engine.
- The return objective is 6.5%: an assumed 2.5% CPI estimate plus a 4.0% real-return margin. These are classroom assumptions, not observed point-in-time inflation data. There is no market-data as-of date for this default-input run.
- The reserve minimum is 3%; bills and the 10-year note are designated eligible in this lab. These are Meridian settings, not approved family-trust rules.
- The engine minimizes volatility across long-only allocations summing to 100%, in five-percentage-point increments. It uses weighted expected returns and the square root of portfolio covariance. The result is the grid optimum, not a continuous optimum. Displayed numbers are rounded; checks use unrounded values with a numerical tolerance of `1e-12`.
- No additional transaction-cost or tax deduction is applied. This reproduction does not evaluate trust payouts, turnover, a point-in-time signal, stress scenarios, or the complete trust mandate. It does not run a changed-input experiment. A feasible lab allocation does not establish sustainable trust funding or future returns.

## Repository guide

- [Reproduction script](reproduce_decision.py): one-command terminal result.
- [Lab 13 mandate](Portfolio%20Mandate%20%28Lab%2013%29/Lab%2013%20CIO%20Mandate%20and%20Discussion.md): original mandate discussion, including the separate family-trust case.
- [Lab 15 app](Portfolio%20Stability%20Decision%20%28Lab%2015%29/app.py) and [method documentation](Portfolio%20Stability%20Decision%20%28Lab%2015%29/Portfolio%20App%20README.md): interactive portfolio exploration. The terminal command above reproduces its default calculation without needing Streamlit. The older app guide includes author-specific local paths; they are not needed for this reproduction.
- [Lab 18](Legend%20Investor%20as%20a%20Skill%20%28Lab%2018%29/README.md): SEC business-quality research.
- [Lab 19](Legend%20Panel%20%28Lab%2019%29/README.md): investor-inspired panel research and the completed COST example. Its business-quality judgment is separate from a trust allocation decision.

## Educational and research use only

This project, including its code, data, models, analyses, and outputs, is for educational and research purposes only. It does not constitute investment, financial, legal, tax, or other professional advice, or a recommendation or solicitation to buy or sell any security. Assumptions, estimates, and historical results may be incomplete or inaccurate and do not guarantee future performance. Do not rely on this project as the basis for real-world investment or financial decisions.
