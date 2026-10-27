# Lab 16 — Zero-coupon bonds, credit risk, and as-of data

## Educational and research purposes only

This project, including its code, data, models, analyses, and outputs, is for educational and research purposes only. It does not constitute investment, financial, legal, tax, or other professional advice, or a recommendation or solicitation to buy or sell securities. Estimates and historical results do not guarantee future performance. Do not rely on this project as the basis for real-world investment or financial decisions.

## Zero-coupon bond pricing

A zero-coupon bond pays no periodic coupons. Its contractual payment is its face value at maturity; actual repayment remains subject to default risk. See the [SEC's zero-coupon bond explanation](https://www.investor.gov/introduction-investing/investing-basics/glossary/zero-coupon-bond).

Discounting that single promised payment using an effective annual yield gives:

```text
P = F / (1 + y)^T

y = (F / P)^(1 / T) - 1
```

- `P`: price today.
- `F`: face value promised at maturity, in the same units as P.
- `y`: effective annual yield to maturity, expressed as a decimal.
- `T`: years remaining until maturity; T must be positive.

These formulas assume a single payment and an annual effective compounding convention. Yield to maturity is calculated from promised cash flows; it is not a guarantee of the return actually received if default occurs.

For a zero-coupon bond promising 100 at maturity:

| Price | Implied yield to maturity |
| --- | --- |
| Below 100 | Positive |
| Exactly 100 | Zero |
| Above 100 | Negative |

For example, paying 105 today for a single promised payment of 100 one year later implies `100 / 105 - 1 = -4.76%`. This conclusion requires the zero-coupon assumption. Coupon-paying bonds can trade above face value and still have positive yields, as illustrated in the [RBA's bond price and yield example](https://www.rba.gov.au/education/resources/explainers/bonds-and-the-yield-curve.html).

## Greater default risk requires a higher yield

Default risk is the possibility that an issuer fails to make promised payments. Investors generally demand a higher yield to accept greater default risk. That additional required yield is compensation for bearing risk, often described as a risk premium. A credit spread over a comparable low-risk benchmark can also reflect expected default losses, liquidity, and other factors; it is not purely extra profit. See the [SEC's high-yield bond explanation](https://www.investor.gov/introduction-investing/investing-basics/glossary/high-yield-bond-or-junk-bond).

For this classroom comparison, treat AAA, BBB, and CCC as credit-quality categories: AAA is lower risk, BBB intermediate, and CCC higher risk. With equal face values, the same remaining maturity, currency, zero-coupon structure, and otherwise comparable terms, the expected ordering is:

```text
Default risk:  AAA < BBB < CCC
Required yield: AAA < BBB < CCC
Price:         AAA > BBB > CCC
```

Why? A higher required yield increases the denominator in `P = F / (1 + y)^T`, reducing the price. A CCC bond is cheaper than a comparable AAA bond because investors require more compensation for the risk of not receiving the promised payment. This is an all-else-equal comparison, not a universal ranking across different bonds or bond funds.

Illustrative assumptions: each bond promises 100 in one year, with yields chosen only to demonstrate the formula.

| Category | Assumed annual yield | Price: 100 / (1 + yield) |
| --- | --- | --- |
| AAA | 4% | 96.15 |
| BBB | 6% | 94.34 |
| CCC | 12% | 89.29 |

## The as-of training table

The accompanying [asof.py](asof.py) extends the Lab 15 copy with a sanity gate. Editable inputs at the top include the training table and decision date **2026-03-31**. Apply these rules in order:

1. Quarantine rows with no ticker.
2. Remove exact duplicates, ignoring the row-number label.
3. Remove publications after the decision date; publications on March 31 are included.
4. For each ticker and measured month, retain the latest publication available by the decision date.

The program prints the row funnel, remaining panel, and price-return signals, then compares them with a naive panel that ignores the publication cutoff. The monthly signal is `(latest price / previous calendar month's price - 1) * 100`. This monthly holding-period price return is different from annualized yield to maturity.

The supplied table contains prices above 100 and CCC prices above AAA. If interpreted as comparable zero-coupon bonds, these raise economic questions: prices above 100 imply negative promised yields, and the credit-price ranking conflicts with the classroom assumption. The four data-cleaning rules alone do not resolve these issues.

## Sanity gate

After the four rules, the script prints each remaining row's annualized zero-coupon yield and a `Breaks` column. Editable inputs `FACE_VALUE = "100"`, `YEARS_TO_MATURITY = "1"`, and `CREDIT_ORDER = ("AAA", "BBB", "CCC")` are explicit classroom assumptions, not metadata supplied by the training table. The same remaining maturity is assumed for every row; this does not establish that observations represent one fixed-maturity security through time.

The gate flags negative yields and a riskier category's price being above or equal to a safer category's price in the same measured month. CCC is compared with both AAA and BBB. `nothing` means no tested condition broke. Missing safer-category observations or unknown ticker categories appear separately under `Unchecked`; they are not treated as evidence of a pass. The overall result is FAIL for any break, INCOMPLETE for unchecked comparisons without breaks, and PASS otherwise.

These are diagnostic flags under the stated assumptions, not automatic proof of erroneous market data. Negative yields are mathematically possible. The gate does not remove rows or change the four-rule funnel or either set of signals. The annual yield is distinct from the monthly price-return signal. Lab 15's original script remains unchanged.

## Run

From the repository root (Python 3, standard library only):

```bash
python3 "Provenance_Gate (Lab 16)/asof.py"
```

Or, from inside `Provenance_Gate (Lab 16)` with Python available:

```bash
python asof.py
```
