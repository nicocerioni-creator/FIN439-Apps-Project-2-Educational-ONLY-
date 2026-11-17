"""Recalculate the current Lab 15 result using only Python's standard library."""

from pathlib import Path
import runpy


def main():
    engine = runpy.run_path(
        str(Path(__file__).resolve().parent
            / "Portfolio Stability Decision (Lab 15)" / "portfolio.py")
    )
    sleeves = engine["SLEEVES"]
    objective = engine["OBJECTIVE_RETURN"]
    reserve_minimum = 0.03  # Existing Lab 15 app default; not a trust mandate rule.
    eligible = engine["RESERVE_ELIGIBLE"]
    covariance = engine["build_covariance_matrix"](sleeves, engine["CORRELATIONS"])
    best = engine["search_lowest_risk_mix"](
        sleeves, engine["CORRELATIONS"], objective, reserve_minimum, eligible
    )
    portfolios = {
        "Benchmark (60% equity / 40% bonds)": engine["benchmark_weights"](
            sleeves, engine["BENCHMARK_WEIGHTS"]
        ),
        "Equal weight": engine["equal_weights"](sleeves),
        "Inverse volatility": engine["inverse_volatility_weights"](sleeves),
    }
    if best is not None:
        portfolios["Lowest-risk feasible grid mix"] = best["weights"]

    print("CURRENT LAB 15 RESULT — NOT THE FINAL PROJECT 2 DECISION")
    print("Project 2 is still being updated. Family-trust adoption remains pending.")
    print("Educational and research use only; not investment advice.")
    print("Inputs: saved Meridian classroom assumptions, not live market data.")
    print(f"Estimated annual return objective: {objective:.2%}")
    print(f"Reserve minimum: {reserve_minimum:.2%}")
    print("Reserve-eligible: " + ", ".join(name for name in sleeves if name in eligible))
    print("Search: long-only, fully invested, 5-percentage-point weight increments.")

    for name, weights in portfolios.items():
        expected = engine["portfolio_expected_return"](weights, sleeves)
        volatility = engine["portfolio_volatility"](weights, sleeves, covariance)
        reserve = engine["reserve_eligible_weight"](weights, eligible)
        failures = []
        if expected < objective - 1e-12:
            failures.append("estimated return below objective")
        if reserve < reserve_minimum - 1e-12:
            failures.append("reserve below minimum")
        print(f"\n{name}")
        for sleeve, weight in weights.items():
            print(f"  {sleeve}: {weight:.1%}")
        print(f"  Estimated annual return: {expected:.2%}")
        print(f"  Annual volatility: {volatility:.2%}")
        print(f"  Reserve-eligible weight: {reserve:.1%}")
        print("  Lab return/reserve checks: "
              + ("FAIL — " + "; ".join(failures) if failures else "PASS"))

    if best is None:
        print("\nCurrent lab result: no grid mix meets the return/reserve requirements.")
    else:
        print("\nCurrent lab result: a feasible minimum-volatility grid mix exists.")
    print("This does not establish compliance with the full Project 2 trust mandate.")
    print("Trust payouts, turnover, point-in-time signals, and stress tests are not evaluated here.")
    print("Estimated returns are not guarantees; no additional costs or taxes are deducted.")


if __name__ == "__main__":
    main()
