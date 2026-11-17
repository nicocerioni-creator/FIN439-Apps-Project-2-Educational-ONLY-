"""Check candidate portfolios against the checkable investment mandate rules."""

# Editable inputs. All weights and percentage limits use percent units (0 to 100).
HOLDINGS = {
    "Cash": {"issuer": None, "business_days_to_redeem": 0, "reserve_eligible": True},
    "Treasury bills": {"issuer": "U.S. Treasury", "business_days_to_redeem": 1, "reserve_eligible": True},
    "Treasury 10-year note": {"issuer": "U.S. Treasury", "business_days_to_redeem": 1, "reserve_eligible": True},
    "Global equity index fund": {"issuer": "diversified fund", "business_days_to_redeem": 2, "reserve_eligible": False},
    "Investment-grade bond fund": {"issuer": "diversified fund", "business_days_to_redeem": 3, "reserve_eligible": False},
    "Private real estate fund": {"issuer": "diversified fund", "business_days_to_redeem": 90, "reserve_eligible": False},
    "Acme Corp bonds": {"issuer": "Acme Corp", "business_days_to_redeem": 4, "reserve_eligible": False},
    "Acme Corp stock": {"issuer": "Acme Corp", "business_days_to_redeem": 1, "reserve_eligible": False},
}

CANDIDATES = {
    "A": {
        "Cash": 2, "Treasury bills": 2, "Treasury 10-year note": 10,
        "Global equity index fund": 60, "Investment-grade bond fund": 26,
        "Private real estate fund": 0, "Acme Corp bonds": 0, "Acme Corp stock": 0,
    },
    "B": {
        "Cash": 1, "Treasury bills": 0, "Treasury 10-year note": 0,
        "Global equity index fund": 55, "Investment-grade bond fund": 20,
        "Private real estate fund": 15, "Acme Corp bonds": 5, "Acme Corp stock": 4,
    },
    "C": {
        "Cash": 1, "Treasury bills": 1, "Treasury 10-year note": 0,
        "Global equity index fund": 70, "Investment-grade bond fund": 20,
        "Private real estate fund": 0, "Acme Corp bonds": 0, "Acme Corp stock": 8,
    },
    "D": {
        "Cash": 100, "Treasury bills": 0, "Treasury 10-year note": 0,
        "Global equity index fund": 0, "Investment-grade bond fund": 0,
        "Private real estate fund": 0, "Acme Corp bonds": 0, "Acme Corp stock": 0,
    },
    # Meridian's S4 benchmark, retained for the Lab 14 mandate comparison.
    "E": {
        "Cash": 0, "Treasury bills": 0, "Treasury 10-year note": 0,
        "Global equity index fund": 60, "Investment-grade bond fund": 40,
        "Private real estate fund": 0, "Acme Corp bonds": 0, "Acme Corp stock": 0,
    },
}

RESERVE_SIZE_USD_MILLIONS = 100
QUARTERLY_DISTRIBUTION_USD_MILLIONS = 0.75
QUARTERS_TO_COVER = 4
LIQUIDITY_WINDOW_BUSINESS_DAYS = 5
MINIMUM_LIQUID_SHARE_PERCENT = 90
ISSUER_LIMIT_PERCENT = 8
EXEMPT_ISSUERS = {None, "U.S. Treasury", "diversified fund"}


def main():
    # Decimal avoids binary floating-point errors at inclusive rule boundaries.
    from decimal import Decimal

    def number(value):
        return Decimal(str(value))

    zero = number(0)
    hundred = number(100)
    reserve_minimum = (
        number(QUARTERS_TO_COVER)
        * number(QUARTERLY_DISTRIBUTION_USD_MILLIONS)
        / number(RESERVE_SIZE_USD_MILLIONS)
        * hundred
    )
    print(f"Reserve minimum: {reserve_minimum:.1f}%")

    for name, candidate in CANDIDATES.items():
        unknown = set(candidate) - set(HOLDINGS)
        if unknown:
            raise ValueError(f"Candidate {name}: unknown holdings: {sorted(unknown)}")
        weights = {holding: number(candidate.get(holding, 0)) for holding in HOLDINGS}
        total = sum(weights.values(), zero)
        lowest = min(weights.values())
        reserve = sum(
            (weights[holding] for holding, info in HOLDINGS.items() if info["reserve_eligible"]),
            zero,
        )
        liquid = sum(
            (weights[holding] for holding, info in HOLDINGS.items()
             if info["business_days_to_redeem"] <= LIQUIDITY_WINDOW_BUSINESS_DAYS),
            zero,
        )
        companies = {}
        for holding, info in HOLDINGS.items():
            issuer = info["issuer"]
            if issuer not in EXEMPT_ISSUERS:
                companies[issuer] = companies.get(issuer, zero) + weights[holding]
        largest_company = max(companies.values(), default=zero)

        checks = [
            ("Weights sum to 100%", total, total == hundred),
            ("Lowest weight (long-only)", lowest, lowest >= zero),
            ("Reserve-eligible weight", reserve, reserve >= reserve_minimum),
            ("Weight redeemable within liquidity window", liquid,
             liquid >= number(MINIMUM_LIQUID_SHARE_PERCENT)),
            ("Largest single company", largest_company,
             largest_company <= number(ISSUER_LIMIT_PERCENT)),
        ]
        print(f"\nCandidate {name}")
        for label, measured, passed in checks:
            print(f"  {label}: {measured:.1f}% — {'pass' if passed else 'FAIL'}")
        print("  Calendar-year loss rule: requires CIO clarification")
        failures = sum(not passed for _, _, passed in checks)
        print("  passes every checkable rule" if failures == 0 else f"  fails {failures} rule(s)")


if __name__ == "__main__":
    main()
