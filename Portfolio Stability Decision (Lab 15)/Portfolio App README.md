# Portfolio learning app

## Educational and research use only

This project, including its code, data, models, analyses, and outputs, is for educational and research purposes only. It does not constitute investment, financial, legal, tax, or other professional advice, or a recommendation or solicitation to buy or sell any security. Assumptions, estimates, and historical results may be incomplete or inaccurate and do not guarantee future performance. Do not rely on this project as the basis for real-world investment or financial decisions.

`app.py` imports the Meridian inputs, grid search, and CSV estimator from `portfolio.py`. This Lab 15 version includes the additions made October 22, 2026. Lab 14 retains its original engine without these additions; both versions preserve the original command-line output.

## Run from the AI Finance 2026 folder

```bash
source .venv/bin/activate
python -m streamlit run "NicolasCerioni/Project 2 FIN439/Lab 15/app.py"
```

Press Control+C in the terminal to stop the server. Streamlit is already installed in this project's `.venv`; no new dependencies were installed for this change.

## Inputs and comparison

- Without an upload, use Meridian's supplied estimates. The initial objective is 6.5% and reserve minimum is 3%; bills and the 10-year note are initially reserve-eligible.
- Upload a CSV with ISO dates first, oldest first, followed by one uniquely named column per ticker. Supply positive finite prices for the same consecutive months across all assets. Blank/missing prices, duplicate months, gaps, and unsorted dates are rejected. Use distribution-adjusted prices for total-return estimates.
- Monthly simple return = current price / previous price − 1. Expected annual return = arithmetic monthly mean × 12. Annual volatility = sample monthly standard deviation × √12. Correlations are sample correlations between synchronized monthly returns.
- The last-36 switch selects up to the last 36 returns AFTER calculating returns (36 returns require 37 price rows). The app shows the actual count. Constant-return assets use zero off-diagonal correlation by convention; zero volatility makes their covariance zero.
- Each annual return is editable; volatility and correlations come from the active window. Changing data source or window initializes new return fields. Switching windows may restore earlier edits for that window within the session.
- CSV assets initially have no reserve eligibility. Check eligible assets explicitly, or set the reserve minimum to zero for a stock-only demonstration. A check box is a user assumption, not verification of an asset's eligibility.
- Both result panels use the CURRENT objective, reserve minimum, and eligibility checkboxes. The reference uses original returns as loaded and all CSV months; the current panel uses edits and the selected window. This keeps constraints constant when comparing estimation assumptions.
- The largest weight change is the maximum absolute difference between corresponding weights, in percentage points. It is unavailable if either search is infeasible.

## Search and limits

The search covers every long-only, fully invested mix in five-percentage-point increments, including zero weights and 100% in one asset. Branches that cannot meet the return or reserve constraint are skipped. Among feasible grid mixes, it returns the one with lowest volatility using the shared engine. Equal-volatility ties retain the first candidate in deterministic insertion/increasing-weight order. A numerical tolerance of 1e-12 handles equality at a constraint.

At a 3% reserve minimum, the smallest positive reserve allocation on this grid is 5%. This finds the grid optimum, not a continuous optimum. Search size grows combinatorially with the asset count; large uploads may take time. Results are cached to avoid repeating unchanged searches.

Annualized historical arithmetic means are estimates, not forecasts or compounded growth rates. No extra cost or tax deduction is applied. Annualization does not model serial dependence. Volatility does not guarantee a maximum loss, and this app does not test all Meridian mandate rules.

## Verify

```bash
python -m unittest discover -s "NicolasCerioni/Project 2 FIN439/Lab 15" -p "test_portfolio_extensions.py" -v
```

## portfolio.py flowcharts

These diagrams follow the Lab 15 code. Running `portfolio.py` directly prints the three original baselines. Importing it from `app.py` makes its inputs and functions available without running `main()` or printing those baselines. The app calls the CSV estimator and grid search separately.

### Entry point and original terminal path

```mermaid
flowchart TD
    A["Load Meridian inputs and define functions"] --> B{"Run portfolio.py directly?"}
    B -->|No: imported| C["Expose inputs and functions to app.py; do not run main"]
    B -->|Yes| D["main: validate correlations and volatilities"]
    D --> E["Build covariance matrix: correlation times both asset volatilities"]
    E --> F["Build benchmark, equal-weight, and inverse-volatility allocations"]
    F --> G["For each allocation: calculate weighted expected return, portfolio volatility, and reserve weight"]
    G --> H["Compare unrounded expected return with objective"]
    H --> I["Print objective, CPI estimate, margin, and all three baseline results"]
    D -->|Invalid inputs| J["Stop with Cannot run error"]
    E -->|Invalid inputs| J
    F -->|Invalid inputs| J
    G -->|Invalid inputs| J
```

### CSV estimation path — estimate_from_csv

```mermaid
flowchart TD
    A["Receive CSV path or uploaded file and last-36 flag"] --> B["Read CSV; validate unique ticker names, numeric positive prices, and consecutive ascending months"]
    B --> C{"At least three monthly price rows?"}
    B -->|Invalid data| X["Raise error; app displays message"]
    C -->|No| X
    C -->|Yes| D["Calculate monthly simple returns: current price divided by previous price minus 1"]
    D --> E{"Last 36 months selected?"}
    E -->|Yes| F["Keep up to the last 36 returns, after calculating returns"]
    E -->|No| G["Keep all monthly returns"]
    F --> H["Calculate monthly arithmetic means and sample standard deviations"]
    G --> H
    H --> I["Annualize: mean times 12; standard deviation times square root of 12"]
    I --> J["Calculate symmetric correlation matrix; diagonal is 1"]
    J --> K["Constant-return asset: set its off-diagonal correlations to 0"]
    K --> L["Return asset estimates, correlations, month count, and return-period dates"]
```

### Portfolio search path — search_lowest_risk_mix

```mermaid
flowchart TD
    A["Receive asset estimates, correlations, objective, reserve minimum, and eligible assets"] --> B["Validate inputs and build covariance matrix using shared functions"]
    B -->|Invalid inputs| X["Raise error; app displays message"]
    B --> C["Start with 20 allocation units, each worth 5 percentage points; best mix is None"]
    C --> D{"Any remaining search branch?"}
    D -->|Yes| E{"Can this branch still meet return and reserve requirements?"}
    E -->|No| D
    E -->|Yes| F["Assign next asset 0 to remaining units; last asset receives all remaining units"]
    F --> G{"Fully allocated across all assets?"}
    G -->|No| E
    G -->|Yes| H["Use shared functions to calculate weighted expected return and reserve weight"]
    H --> I{"Both constraints met within numerical tolerance?"}
    I -->|No| D
    I -->|Yes| J["Use portfolio_volatility: square root of weighted covariance sum"]
    J --> K{"First feasible mix, or lower volatility than best?"}
    K -->|Yes| L["Save weights, expected return, volatility, and reserve weight as best"]
    K -->|No| D
    L --> D
    D -->|No| M{"Was a feasible mix found?"}
    M -->|Yes| N["Return lowest-volatility grid mix"]
    M -->|No| O["Return None; app shows no mix meets the objective"]
```

The search diagram summarizes the recursive `visit()` loop: a failed branch returns to the previous allocation and tries the next one. Correlations affect portfolio volatility; they do not directly change the weighted expected return. The search considers fully invested, long-only mixes and retains the first candidate when volatilities tie.

### Compare with my paper drawing

Compare each box and decision with the path you drew on paper. Any box you did not draw becomes a question to investigate, for example: “Why does the code calculate monthly returns before selecting the last 36 months?” The diagrams describe the code; they do not claim to reproduce a paper drawing that has not been supplied.
