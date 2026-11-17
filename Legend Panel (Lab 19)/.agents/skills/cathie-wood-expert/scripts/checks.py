"""Wood-inspired historical growth and reinvestment checks; no forecasts."""
from decimal import Decimal


def evaluate(report):
    rows = report['rows']
    growth = intensity = 'not known'
    if len(rows) == 5:
        first, last = [rows[i]['metrics']['revenue']['value'] for i in (0, -1)]
        if first is not None and last is not None and first > 0 and last >= 0:
            # Equivalent to CAGR >= 5%, without rounding a fourth root.
            growth = 'pass' if Decimal(str(last)) >= Decimal(str(first)) * Decimal('1.05') ** 4 else 'fail'
    if rows:
        m = rows[-1]['metrics']
        rd, revenue = m['research_and_development'], m['revenue']
        if rd['value'] is not None and revenue['value'] is not None and revenue['value'] > 0:
            if rd['sources'][0]['start'] == revenue['sources'][0]['start']:
                intensity = 'pass' if Decimal(str(rd['value'])) >= Decimal('.05') * Decimal(str(revenue['value'])) else 'fail'
    return {'Revenue CAGR at least 5%': growth, 'Latest R&D / revenue at least 5%': intensity}
