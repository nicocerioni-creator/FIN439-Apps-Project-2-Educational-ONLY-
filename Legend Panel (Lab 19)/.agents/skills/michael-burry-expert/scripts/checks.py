"""Burry-inspired cash backing and reported balance-sheet checks."""
from decimal import Decimal


def evaluate(report):
    rows = report['rows']
    cash = leverage = 'not known'
    if len(rows) == 5:
        comparisons = []
        for row in rows:
            m = row['metrics']
            cf, ni = m['operating_cash_flow'], m['net_income']
            if cf['value'] is None or ni['value'] is None:
                break
            if cf['sources'][0]['start'] != ni['sources'][0]['start']:
                break
            comparisons.append(cf['value'] >= ni['value'])
        if len(comparisons) == 5:
            cash = 'pass' if all(comparisons) else 'fail'
    if rows:
        m = rows[-1]['metrics']
        liab, eq = m['liabilities']['value'], m['equity']['value']
        if liab is not None and eq is not None and eq > 0:
            leverage = 'pass' if Decimal(str(liab)) <= Decimal('2') * Decimal(str(eq)) else 'fail'
    return {'OCF at least net income every year': cash, 'Latest liabilities / equity at most 2': leverage}
