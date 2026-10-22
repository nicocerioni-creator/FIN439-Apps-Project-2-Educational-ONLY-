"""Interactive learning demonstration; all portfolio math lives in portfolio.py."""
import copy
import hashlib
import io

import streamlit as st

from portfolio import (SLEEVES, CORRELATIONS, OBJECTIVE_RETURN, RESERVE_ELIGIBLE,
                       estimate_from_csv, search_lowest_risk_mix)


@st.cache_data(max_entries=16, show_spinner=False)
def load_prices(content, last_36):
    return estimate_from_csv(io.BytesIO(content), last_36_months=last_36)


@st.cache_data(max_entries=64, show_spinner=False)
def search(sleeves, correlations, objective, reserve_minimum, eligible):
    return search_lowest_risk_mix(sleeves, correlations, objective, reserve_minimum, eligible)


def display_mix(result):
    if result is None:
        st.info("no mix meets the objective")
        return
    st.table({"Asset": list(result["weights"]),
              "Weight": [f"{value:.2%}" for value in result["weights"].values()]},
             alt="Optimal portfolio weights in five-percentage-point increments")
    st.metric("Expected annual return", f'{result["expected_return"]:.2%}')
    st.metric("Annual volatility", f'{result["volatility"]:.2%}')
    st.metric("Reserve-eligible weight", f'{result["reserve_eligible_weight"]:.2%}')


st.set_page_config(page_title="Portfolio learning lab", layout="wide")
st.title("Portfolio learning lab")
st.caption("Built with AI help, a learning demonstration, not investment advice.")

with st.sidebar:
    st.header("Search settings")
    objective = st.number_input("Objective annual return (%)", value=OBJECTIVE_RETURN * 100,
                                step=0.1, format="%.2f", key="objective") / 100
    reserve_minimum = st.number_input("Reserve minimum (%)", min_value=0.0, max_value=100.0,
                                      value=3.0, step=1.0, format="%.2f", key="reserve_minimum") / 100
    uploaded = st.file_uploader("Upload prices.csv", type=["csv"], key="prices",
                                help="Date first (YYYY-MM-DD), oldest first; one positive price column per ticker and one row per consecutive month.")
    last_36 = st.toggle("Last 36 months", value=False, disabled=uploaded is None, key="last_36")

try:
    if uploaded is None:
        baseline_sleeves = copy.deepcopy(SLEEVES)
        baseline_correlations = copy.deepcopy(CORRELATIONS)
        active_sleeves = copy.deepcopy(SLEEVES)
        active_correlations = copy.deepcopy(CORRELATIONS)
        source_key = "Meridian"
        default_eligible = RESERVE_ELIGIBLE
        st.caption("Source: Meridian's assumed annual returns, volatilities, and correlations.")
    else:
        content = uploaded.getvalue()
        source_key = hashlib.sha256(content).hexdigest()
        baseline = load_prices(content, False)
        active = load_prices(content, last_36)
        baseline_sleeves = baseline["sleeves"]
        baseline_correlations = baseline["correlations"]
        active_sleeves = copy.deepcopy(active["sleeves"])
        active_correlations = active["correlations"]
        default_eligible = set()
        st.caption(f'CSV estimates: {active["months"]} monthly returns, {active["start"]} to {active["end"]}. '
                   f'All-month reference: {baseline["months"]} returns. Means × 12; sample standard deviations × √12.')
        st.caption("Use distribution-adjusted prices to estimate total returns. Raw prices omit distributions. "
                   "Historical arithmetic averages are estimates, not forecasts; no extra fee or tax deduction is made.")
    st.subheader("Expected returns and reserve eligibility")
    st.caption("Edit annual returns in percent. Volatilities and correlations stay at the loaded estimates. "
               "Reserve eligibility is your designation; CSV tickers start unticked.")
    eligible = set()
    for name, info in active_sleeves.items():
        return_column, reserve_column = st.columns([3, 2], vertical_alignment="bottom")
        with return_column:
            info["expected_return"] = st.number_input(
                f"{name} — expected annual return (%)", value=info["expected_return"] * 100,
                step=0.1, format="%.4f", key=f"return:{source_key}:{last_36}:{name}") / 100
        with reserve_column:
            if st.checkbox(f"{name} — reserve-eligible", value=name in default_eligible,
                           key=f"reserve:{source_key}:{name}"):
                eligible.add(name)
    st.caption("Search: long-only, fully invested, 5-percentage-point steps. A 3% reserve minimum therefore requires at least 5% on this grid.")
    if not eligible and reserve_minimum > 0:
        st.info("No asset is marked reserve-eligible, so a positive reserve minimum cannot be met.")
    st.subheader("Lowest-risk mix")
    st.caption("Both searches use the current objective, reserve minimum, and eligibility flags. "
               "The reference keeps original loaded returns and uses all CSV months, even when the switch is on.")
    current_column, loaded_column = st.columns(2, border=True)
    with st.spinner("Searching the 5-point grid…"):
        current_result = search(active_sleeves, active_correlations, objective, reserve_minimum, eligible)
        baseline_result = search(baseline_sleeves, baseline_correlations, objective, reserve_minimum, eligible)
    with current_column:
        st.subheader("Current inputs")
        display_mix(current_result)
    with loaded_column:
        st.subheader("Inputs as loaded — all months")
        display_mix(baseline_result)
    if current_result is not None and baseline_result is not None:
        changes = {name: (weight - baseline_result["weights"][name]) * 100
                   for name, weight in current_result["weights"].items()}
        largest = max(changes, key=lambda name: abs(changes[name]))
        st.metric("Largest absolute weight change", f"{abs(changes[largest]):.2f} percentage points")
        st.caption(f"{largest}: {changes[largest]:+.2f} points (current minus loaded; first asset shown if tied).")
    else:
        st.caption("Largest weight change: unavailable unless both searches find a feasible mix.")
except (ValueError, UnicodeError, OverflowError) as error:
    st.error(str(error))
