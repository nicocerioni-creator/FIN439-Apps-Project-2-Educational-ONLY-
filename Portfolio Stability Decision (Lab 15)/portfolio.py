"""Compare three Meridian baselines. All returns and risks are estimates."""

# Editable inputs: use decimals for returns, volatilities, and weights.
SLEEVES = {
    "Treasury bills": {"expected_return": 0.035, "volatility": 0.005},
    "Treasury 10-year note": {"expected_return": 0.043, "volatility": 0.07},
    "Investment-grade bond fund": {"expected_return": 0.05, "volatility": 0.06},
    "Global equity index fund": {"expected_return": 0.08, "volatility": 0.16},
}
# Rows and columns follow SLEEVES insertion order: bills, 10-year, IG, equity.
CORRELATIONS = [
    [1.00, 0.10, 0.05, 0.00],
    [0.10, 1.00, 0.80, -0.10],
    [0.05, 0.80, 1.00, 0.25],
    [0.00, -0.10, 0.25, 1.00],
]
CPI_ESTIMATE = 0.025  # Labelled estimate, not an observed inflation figure.
REAL_RETURN_MARGIN = 0.04
OBJECTIVE_RETURN = CPI_ESTIMATE + REAL_RETURN_MARGIN
BENCHMARK_WEIGHTS = {
    "Treasury bills": 0.0,
    "Treasury 10-year note": 0.0,
    "Investment-grade bond fund": 0.4,
    "Global equity index fund": 0.6,
}
RESERVE_ELIGIBLE = {"Treasury bills", "Treasury 10-year note"}

import math


def validate_correlations(correlations, sleeve_count):
    """Reject malformed, nonfinite, out-of-range, or asymmetric tables."""
    if len(correlations) != sleeve_count or any(
        len(row) != sleeve_count for row in correlations
    ):
        raise ValueError("Correlation table must have one row and column per sleeve.")
    for i in range(sleeve_count):
        for j in range(sleeve_count):
            value = correlations[i][j]
            if not math.isfinite(value) or not -1 <= value <= 1:
                raise ValueError(
                    f"Correlation at row {i + 1}, column {j + 1} must be between -1 and 1."
                )
            if value != correlations[j][i]:
                raise ValueError("Correlation table must be symmetric.")
        if correlations[i][i] != 1:
            raise ValueError("Correlation table diagonal must equal 1.")


def build_covariance_matrix(sleeves, correlations):
    """Return covariance in sleeve order: corr(i,j) * vol(i) * vol(j)."""
    validate_correlations(correlations, len(sleeves))
    volatilities = [sleeve["volatility"] for sleeve in sleeves.values()]
    if any(not math.isfinite(vol) or vol < 0 for vol in volatilities):
        raise ValueError("Sleeve volatilities must be finite and nonnegative.")
    return [
        [correlations[i][j] * vol_i * vol_j
         for j, vol_j in enumerate(volatilities)]
        for i, vol_i in enumerate(volatilities)
    ]


def benchmark_weights(sleeves, allocations):
    """Return benchmark weights in sleeve order, checking allocation names."""
    if set(allocations) - set(sleeves):
        raise ValueError("Benchmark contains an unknown sleeve.")
    weights = {name: allocations.get(name, 0.0) for name in sleeves}
    if not math.isclose(sum(weights.values()), 1.0, rel_tol=0, abs_tol=1e-12):
        raise ValueError("Benchmark weights must sum to 100%.")
    return weights


def equal_weights(sleeves):
    """Allocate equally across the supplied sleeves."""
    return {name: 1 / len(sleeves) for name in sleeves}


def inverse_volatility_weights(sleeves):
    """Normalize reciprocal sleeve volatilities to sum to one."""
    if any(not math.isfinite(info["volatility"]) or info["volatility"] <= 0
           for info in sleeves.values()):
        raise ValueError("Inverse volatility requires strictly positive, finite volatilities.")
    reciprocals = {name: 1 / info["volatility"] for name, info in sleeves.items()}
    total = sum(reciprocals.values())
    return {name: value / total for name, value in reciprocals.items()}


def portfolio_expected_return(weights, sleeves):
    """Calculate the weighted expected return without rounding inputs."""
    return sum(weights[name] * info["expected_return"] for name, info in sleeves.items())


def portfolio_volatility(weights, sleeves, covariance):
    """Calculate sqrt(w' Sigma w), using sleeve order for both matrix axes."""
    ordered_weights = [weights[name] for name in sleeves]
    variance = sum(
        weight_i * weight_j * covariance[i][j]
        for i, weight_i in enumerate(ordered_weights)
        for j, weight_j in enumerate(ordered_weights)
    )
    if variance < 0:
        raise ValueError("Negative portfolio variance: check the correlation inputs.")
    return math.sqrt(variance)


def reserve_eligible_weight(weights, eligible_sleeves):
    """Sum the weights of sleeves designated reserve-eligible."""
    return sum(weight for name, weight in weights.items() if name in eligible_sleeves)


def meets_objective(expected_return, objective_return):
    """Compare unrounded expected return with the objective."""
    return expected_return >= objective_return


def search_lowest_risk_mix(sleeves, correlations, objective_return,
                          reserve_minimum, eligible_sleeves):
    """Return the least-volatile feasible 5-percentage-point mix, or None.

    Weights are long-only and sum to 100%. Every grid mix is covered;
    branches provably unable to meet either constraint are skipped.
    Ties retain the first mix in deterministic sleeve/increasing-weight order.
    """
    if not sleeves:
        raise ValueError("At least one asset is required.")
    if not math.isfinite(objective_return):
        raise ValueError("Objective return must be finite.")
    if not math.isfinite(reserve_minimum) or not 0 <= reserve_minimum <= 1:
        raise ValueError("Reserve minimum must be between 0% and 100%.")
    if set(eligible_sleeves) - set(sleeves):
        raise ValueError("Reserve eligibility contains an unknown asset.")
    names = list(sleeves)
    returns = [sleeves[name]["expected_return"] for name in names]
    if any(not math.isfinite(value) for value in returns):
        raise ValueError("Expected returns must be finite.")
    covariance = build_covariance_matrix(sleeves, correlations)
    eligible = [name in eligible_sleeves for name in names]
    best = None
    weights = {}
    tolerance = 1e-12  # Accept equality despite binary floating-point noise.

    def visit(index, remaining, partial_return, partial_reserve):
        nonlocal best
        if partial_return + remaining / 20 * max(returns[index:]) < objective_return - tolerance:
            return
        possible_reserve = remaining / 20 if any(eligible[index:]) else 0.0
        if partial_reserve + possible_reserve < reserve_minimum - tolerance:
            return
        units_to_try = [remaining] if index == len(names) - 1 else range(remaining + 1)
        for units in units_to_try:
            weight = units / 20
            weights[names[index]] = weight
            expected_return = partial_return + weight * returns[index]
            reserve = partial_reserve + weight * eligible[index]
            if index < len(names) - 1:
                visit(index + 1, remaining - units, expected_return, reserve)
            else:
                # Reuse the original engine for all final portfolio statistics.
                expected_return = portfolio_expected_return(weights, sleeves)
                reserve = reserve_eligible_weight(weights, eligible_sleeves)
                if expected_return < objective_return - tolerance or reserve < reserve_minimum - tolerance:
                    continue
                volatility = portfolio_volatility(weights, sleeves, covariance)
                if best is None or volatility < best["volatility"]:
                    best = {"weights": weights.copy(), "expected_return": expected_return,
                            "volatility": volatility, "reserve_eligible_weight": reserve}

    visit(0, 20, 0.0, 0.0)
    return best


def estimate_from_csv(source, last_36_months=False):
    """Estimate annual arithmetic means, sample volatilities and correlations.

    source is a path or a text/binary file-like object. CSV: ISO date first,
    followed by unique ticker columns, positive monthly prices, oldest first.
    Uses complete consecutive months, never fills missing observations.
    Last-36 means up to 36 RETURNS (37 prices), selected after differencing.
    Constant-return assets have zero off-diagonal correlations by convention;
    their zero volatility makes those covariances zero.
    """
    import csv
    import io
    import statistics
    from datetime import date
    from pathlib import Path

    raw = source.read() if hasattr(source, "read") else Path(source).read_bytes()
    text = raw.decode("utf-8-sig") if isinstance(raw, bytes) else raw.lstrip("\ufeff")
    rows = list(csv.reader(io.StringIO(text)))
    rows = [row for row in rows if any(cell.strip() for cell in row)]
    if not rows or len(rows[0]) < 2:
        raise ValueError("CSV needs a date column and at least one ticker column.")
    tickers = [cell.strip() for cell in rows[0][1:]]
    if any(not ticker for ticker in tickers) or len(set(tickers)) != len(tickers):
        raise ValueError("Ticker names must be nonempty and unique.")
    dates, prices = [], []
    for line_number, row in enumerate(rows[1:], 2):
        if len(row) != len(tickers) + 1:
            raise ValueError(f"CSV row {line_number} has missing or extra columns.")
        try:
            observed = date.fromisoformat(row[0].strip())
            values = [float(cell) for cell in row[1:]]
        except ValueError as error:
            raise ValueError(f"CSV row {line_number}: use YYYY-MM-DD dates and numeric prices.") from error
        if any(not math.isfinite(value) or value <= 0 for value in values):
            raise ValueError(f"CSV row {line_number}: prices must be positive and finite.")
        if dates:
            previous = dates[-1]
            month_gap = (observed.year - previous.year) * 12 + observed.month - previous.month
            if observed <= previous or month_gap != 1:
                raise ValueError("Dates must be oldest first, with exactly one row per consecutive month.")
        dates.append(observed)
        prices.append(values)
    if len(prices) < 3:
        raise ValueError("At least three monthly price rows are needed for sample statistics.")
    monthly_returns = [[current / previous - 1 for current, previous in zip(now, before)]
                       for before, now in zip(prices, prices[1:])]
    return_dates = dates[1:]
    if last_36_months:
        monthly_returns = monthly_returns[-36:]
        return_dates = return_dates[-36:]
    columns = list(zip(*monthly_returns))
    means = [statistics.mean(column) for column in columns]
    deviations = [statistics.stdev(column) for column in columns]
    correlations = [[0.0] * len(tickers) for _ in tickers]
    for i in range(len(tickers)):
        correlations[i][i] = 1.0
        for j in range(i):
            if deviations[i] == 0 or deviations[j] == 0:
                value = 0.0
            else:
                sample_covariance = sum((a - means[i]) * (b - means[j])
                                        for a, b in zip(columns[i], columns[j])) / (len(monthly_returns) - 1)
                value = max(-1.0, min(1.0, sample_covariance / (deviations[i] * deviations[j])))
            correlations[i][j] = correlations[j][i] = value
    sleeves = {ticker: {"expected_return": mean * 12, "volatility": deviation * math.sqrt(12)}
               for ticker, mean, deviation in zip(tickers, means, deviations)}
    return {"sleeves": sleeves, "correlations": correlations,
            "months": len(monthly_returns), "start": return_dates[0].isoformat(),
            "end": return_dates[-1].isoformat()}


def main():
    try:
        covariance = build_covariance_matrix(SLEEVES, CORRELATIONS)
        portfolios = {
            "Benchmark": benchmark_weights(SLEEVES, BENCHMARK_WEIGHTS),
            "Equal weight": equal_weights(SLEEVES),
            "Inverse volatility": inverse_volatility_weights(SLEEVES),
        }
        # Calculate every result before printing so invalid inputs stop the run.
        results = [
            (name, weights, portfolio_expected_return(weights, SLEEVES),
             portfolio_volatility(weights, SLEEVES, covariance),
             reserve_eligible_weight(weights, RESERVE_ELIGIBLE))
            for name, weights in portfolios.items()
        ]
    except ValueError as error:
        raise SystemExit(f"Cannot run: {error}") from None

    print(f"Objective return: {OBJECTIVE_RETURN:.2%}")
    print(f"CPI estimate: {CPI_ESTIMATE:.2%}; real-return margin: {REAL_RETURN_MARGIN:.2%}")
    for name, weights, expected_return, volatility, reserve in results:
        print(f"\n{name}")
        for sleeve, weight in weights.items():
            print(f"  {sleeve}: {weight:.1%}")
        print(f"  Expected return: {expected_return:.2%}")
        print(f"  Volatility: {volatility:.2%}")
        print(f"  Reserve-eligible weight: {reserve:.1%}")
        print(f"  Expected return meets objective: {'yes' if meets_objective(expected_return, OBJECTIVE_RETURN) else 'no'}")


if __name__ == "__main__":
    main()
