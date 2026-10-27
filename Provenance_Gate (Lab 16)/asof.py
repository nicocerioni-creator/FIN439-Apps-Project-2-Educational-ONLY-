"""Educational and research use only; not investment or professional advice.

Build a publication-date-aware panel and compare it with a hindsight panel.
Standard library only. Edit TABLE and DECISION_DATE below, then rerun.
"""

# EDITABLE INPUTS: keep tab separators, including the blank ticker in row 11.
TABLE = """Row\tTicker\tMonth measured\tPublished on\tPrice
1\tAAA\t2026-01\t2026-02-10\t101.0
2\tAAA\t2026-02\t2026-03-10\t104.0
3\tAAA\t2026-03\t2026-04-10\t109.0
4\tAAA\t2026-02\t2026-03-25\t103.0
5\tBBB\t2026-01\t2026-02-10\t98.0
6\tBBB\t2026-02\t2026-03-10\t97.0
7\tBBB\t2026-02\t2026-03-10\t97.0
8\tBBB\t2026-03\t2026-04-10\t92.0
9\tCCC\t2026-01\t2026-02-10\t110.0
10\tCCC\t2026-02\t2026-04-05\t112.0
11\t\t2026-02\t2026-03-10\t99.0
12\tCCC\t2026-02\t2026-03-10\t111.0
"""
DECISION_DATE = "2026-03-31"
# Classroom assumptions, not facts supplied by TABLE: comparable zero-coupon
# bonds with the same face value and remaining maturity at each measured month.
FACE_VALUE = "100"
YEARS_TO_MATURITY = "1"
CREDIT_ORDER = ("AAA", "BBB", "CCC")  # Lower to higher default risk.

import csv
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from io import StringIO


@dataclass(frozen=True)
class Row:
    number: int
    ticker: str
    month: date
    published: date
    price: Decimal


def read_rows(table):
    reader = csv.DictReader(StringIO(table.strip()), delimiter="\t")
    expected = ["Row", "Ticker", "Month measured", "Published on", "Price"]
    if reader.fieldnames != expected:
        raise ValueError("Use the five input headers and tab-separated columns.")
    rows = []
    numbers = set()
    for record in reader:
        try:
            if set(record) != set(expected) or any(v is None for v in record.values()):
                raise ValueError("Expected five columns")
            number = int(record["Row"])
            month_text = record["Month measured"].strip()
            month = date.fromisoformat(month_text + "-01")
            published_text = record["Published on"].strip()
            published = date.fromisoformat(published_text)
            price = Decimal(record["Price"].strip())
            if month.strftime("%Y-%m") != month_text:
                raise ValueError("Month must be YYYY-MM")
            if published.isoformat() != published_text:
                raise ValueError("Publication date must be YYYY-MM-DD")
            if number <= 0 or number in numbers:
                raise ValueError("Row numbers must be unique positive integers")
            if not price.is_finite() or price <= 0:
                raise ValueError("Prices must be finite and positive")
        except (ValueError, InvalidOperation) as error:
            raise ValueError(f"Invalid input record {record!r}: {error}") from error
        numbers.add(number)
        rows.append(Row(number, record["Ticker"].strip(), month, published, price))
    return rows


def remove_duplicates(rows):
    # The row number is a label, not part of an observation's identity.
    seen = set()
    kept, removed = [], []
    for row in rows:
        key = (row.ticker, row.month, row.published, row.price)
        if key in seen:
            removed.append(row)
        else:
            seen.add(key)
            kept.append(row)
    return kept, removed


def latest_publications(rows):
    groups = {}
    for row in rows:
        groups.setdefault((row.ticker, row.month), []).append(row)
    kept, removed = [], []
    for group in groups.values():
        latest_date = max(row.published for row in group)
        latest = [row for row in group if row.published == latest_date]
        if len({row.price for row in latest}) > 1:
            raise ValueError("Conflicting prices on the same latest publication date: "
                             + str([row.number for row in latest]))
        winner = latest[0]
        kept.append(winner)
        removed.extend(row for row in group if row is not winner)
    return kept, removed


def report_rule(label, kept, removed):
    numbers = ", ".join(str(row.number) for row in sorted(removed, key=lambda r: r.number))
    print(f"{label}: removed {len(removed)}; rows [{numbers}]; remaining {len(kept)}")


def print_panel(rows):
    print("Row\tTicker\tMonth measured\tPublished on\tPrice")
    for row in sorted(rows, key=lambda r: (r.ticker, r.month)):
        print(f"{row.number}\t{row.ticker}\t{row.month:%Y-%m}\t"
              f"{row.published}\t{row.price}")
    if not rows:
        print("(empty panel)")


def print_signals(panel, tickers):
    for ticker in tickers:
        months = {row.month: row for row in panel if row.ticker == ticker}
        if not months:
            print(f"{ticker}: unavailable (no months in panel)")
            continue
        latest = max(months)
        previous = (date(latest.year - 1, 12, 1) if latest.month == 1
                    else date(latest.year, latest.month - 1, 1))
        if previous not in months:
            print(f"{ticker}: {latest:%Y-%m} signal unavailable "
                  f"(previous calendar month {previous:%Y-%m} missing)")
            continue
        change = (months[latest].price / months[previous].price - 1) * 100
        rounded = change.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        print(f"{ticker}: {latest:%Y-%m} signal {rounded:+.2f}% "
              f"(vs {previous:%Y-%m}; rows {months[previous].number} "
              f"-> {months[latest].number})")


def sanity_gate(panel, face_value, years, credit_order):
    """Return diagnostic results; never alter or remove panel rows."""
    face, term = Decimal(face_value), Decimal(years)
    if not face.is_finite() or face <= 0 or not term.is_finite() or term <= 0:
        raise ValueError("Face value and years to maturity must be finite and positive")
    if not credit_order or len(set(credit_order)) != len(credit_order):
        raise ValueError("CREDIT_ORDER must contain unique ticker names")
    lookup = {(row.ticker, row.month): row for row in panel}
    results = []
    for row in sorted(panel, key=lambda r: (r.ticker, r.month)):
        annual_yield = ((face / row.price) ** (Decimal(1) / term) - 1) * 100
        breaks, unchecked = [], []
        if row.price > face:
            breaks.append("negative yield (price above face value)")
        if row.ticker not in credit_order:
            unchecked.append("ticker absent from CREDIT_ORDER")
        else:
            # Compare against every safer category in the SAME measured month.
            for safer in credit_order[:credit_order.index(row.ticker)]:
                reference = lookup.get((safer, row.month))
                if reference is None:
                    unchecked.append(f"missing {safer} price for this month")
                elif row.price >= reference.price:
                    relation = "above" if row.price > reference.price else "equal to"
                    breaks.append(f"price {relation} {safer} (row {reference.number}); "
                                  "expected lower")
        results.append((row, annual_yield, breaks, unchecked))
    return results


def print_sanity_gate(panel):
    results = sanity_gate(panel, FACE_VALUE, YEARS_TO_MATURITY, CREDIT_ORDER)
    print("\nSANITY GATE (diagnostics only; no rows removed)")
    print(f"Assumptions: zero coupons; face value {FACE_VALUE}; "
          f"remaining maturity {YEARS_TO_MATURITY} year(s) for every row.")
    print("Annual yield (%) = ((face value / price) ** (1 / years) - 1) * 100")
    print("Expected price order, same month and comparable terms: "
          + " > ".join(CREDIT_ORDER))
    print("Row\tTicker\tMonth\tPrice\tAnnual yield\tBreaks\tUnchecked")
    for row, annual_yield, breaks, unchecked in results:
        rounded = annual_yield.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        print(f"{row.number}\t{row.ticker}\t{row.month:%Y-%m}\t{row.price}\t"
              f"{rounded:+.2f}%\t{'; '.join(breaks) or 'nothing'}\t"
              f"{'; '.join(unchecked) or 'nothing'}")
    broken = [row.number for row, _, breaks, _ in results if breaks]
    incomplete = [row.number for row, _, _, unchecked in results if unchecked]
    print(f"Gate result: {'FAIL' if broken else 'INCOMPLETE' if incomplete else 'PASS'}; "
          f"{len(broken)} flagged rows {sorted(broken)}; "
          f"{len(incomplete)} rows with unchecked comparisons {sorted(incomplete)}.")
    print("Signals below retain all as-of rows, including flagged rows.")


def main():
    decision = date.fromisoformat(DECISION_DATE)
    rows = read_rows(TABLE)
    print(f"Decision date: {decision} (publications on this date are included)")
    print(f"Starting rows: {len(rows)}")
    eligible = [row for row in rows if row.ticker]
    quarantine = [row for row in rows if not row.ticker]
    report_rule("1. Quarantine missing ticker", eligible, quarantine)
    unique, duplicates = remove_duplicates(eligible)
    report_rule("2. Remove exact duplicates", unique, duplicates)
    knowable = [row for row in unique if row.published <= decision]
    future = [row for row in unique if row.published > decision]
    report_rule("3. Remove publications after decision date", knowable, future)
    panel, revisions = latest_publications(knowable)
    report_rule("4. Keep latest knowable publication per ticker/month", panel, revisions)
    print("\nAS-OF PANEL")
    print_panel(panel)
    print_sanity_gate(panel)
    tickers = sorted({row.ticker for row in eligible})
    print("\nAS-OF SIGNALS (month-over-month price returns)")
    print_signals(panel, tickers)
    # Retain ticker validation and deduplication, but ignore the decision cutoff.
    naive, _ = latest_publications(unique)
    print("\nNAIVE PANEL (latest publication per ticker/month; no date cutoff)")
    print_panel(naive)
    print("\nNAIVE SIGNALS (hindsight comparison)")
    print_signals(naive, tickers)
    print("\nEducational and research purposes only; not investment advice.")
    print("Price returns exclude distributions unless prices already reflect them.")


if __name__ == "__main__":
    main()
