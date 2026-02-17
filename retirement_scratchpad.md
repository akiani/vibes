# Retirement Net Worth Calculator - Scratchpad

## Scenario
- Family: 2 adults (late 30s) + 1 child
- Location: Islington, London
- Housing: ~1200 sqft rental (3-bed flat)
- No car
- Lifestyle: Upper middle class (comfortable but not extravagant)
- Goal: Never work again

## Key Research Findings

### Exchange Rate
- GBP/USD as of Feb 2026: ~1.365
- Using 1.30 for conservative long-term planning (USD tends to strengthen in crises)

### Housing (Rent)
- 3-bed flat in Islington, ~1200 sqft: GBP 3,000-4,500/month
- Upper middle class quality (nice area, good condition): GBP 3,500/month
- Source: Rightmove, Foxtons, Winkworth data for Islington 2025/26

### Council Tax
- Band E (likely for a 3-bed flat in Islington): GBP 2,459/year = ~GBP 205/month
- Source: counciltax.info 2025/26

### Utilities & Internet
- Gas, electric, water for 3-bed: GBP 300-400/month
- Internet: GBP 35/month
- Mobile phones (2 adults): GBP 40/month
- TV licence: GBP 13/month
- Streaming services (Netflix, etc.): GBP 40/month
- Total utilities bundle: GBP 430/month

### Groceries & Food
- Upper middle class family of 3 (organic, Waitrose-level): GBP 800/month
- Dining out (nice restaurants 2-3x/month, casual more often): GBP 500/month
- Coffee/cafe culture: GBP 100/month
- Total food: GBP 1,400/month

### Transport (No Car)
- 2x adult Oyster/Travelcard Zone 1-2: GBP 300/month
- Child travel (free under 11, discounted after): GBP 30/month
- Occasional Uber/taxi: GBP 150/month
- Total transport: GBP 480/month

### Education
- Option A: State school (free) + tutoring/activities: GBP 500/month
- Option B: Private school: GBP 2,500/month (avg GBP 30,000/year incl. VAT)
- Using PRIVATE school for "upper middle class" assumption: GBP 2,500/month
- After-school activities, music lessons, sports: GBP 200/month
- Total education: GBP 2,700/month

### Healthcare & Insurance
- Private health insurance (family, comprehensive, London): GBP 250/month
- Dental insurance: GBP 50/month
- Life insurance (2 policies, ~GBP 500K cover each): GBP 40/month
- Total: GBP 340/month

### Clothing & Personal
- Upper middle class family: GBP 400/month
- Haircuts/grooming: GBP 100/month
- Total: GBP 500/month

### Holidays & Travel
- 2 international holidays/year (e.g., Europe, one long-haul): GBP 10,000/year
- UK weekends away: GBP 3,000/year
- Total: GBP 13,000/year = GBP 1,083/month

### Entertainment & Leisure
- Theatre, museums, cinema: GBP 200/month
- Kids activities/birthday parties: GBP 100/month
- Gym/fitness (2 adults): GBP 150/month
- Books, hobbies, subscriptions: GBP 100/month
- Total: GBP 550/month

### Home & Miscellaneous
- Home insurance (contents): GBP 30/month
- Furnishings/maintenance: GBP 150/month
- Gifts (Christmas, birthdays, etc.): GBP 150/month
- Professional services (accountant, etc.): GBP 100/month
- Emergency/buffer: GBP 300/month
- Total: GBP 730/month

## Monthly Expense Summary (GBP)

| Category                  | Monthly (GBP) |
|---------------------------|---------------|
| Rent                      | 3,500         |
| Council Tax               | 205           |
| Utilities & Internet      | 430           |
| Groceries & Food          | 1,400         |
| Transport                 | 480           |
| Education (Private)       | 2,700         |
| Healthcare & Insurance    | 340           |
| Clothing & Personal       | 500           |
| Holidays & Travel         | 1,083         |
| Entertainment & Leisure   | 550           |
| Home & Miscellaneous      | 730           |
| **TOTAL**                 | **11,918**    |

## Annual Expenses: GBP 143,016 (~GBP 143,000)

## Tax Considerations

The family needs to generate ~GBP 143,000/year in after-tax income.

### Tax-Efficient Structure (ISA + SIPP + GIA)
- ISA allowance: GBP 20,000/year per person (GBP 40,000 for couple) - tax-free
- SIPP: Can't access until age 55 (57 from 2028) - tax-free growth
- General Investment Account (GIA): Taxed on dividends and capital gains

### Effective Tax Rate on Investment Income
For GBP 143,000 of annual spending:
- First GBP 25,140 (2x personal allowance): 0% tax
- ISA withdrawals: tax-free (assume large ISA pots built over time)
- Realistically, with good tax planning: ~15-20% effective tax rate on investment income
- Gross income needed: ~GBP 165,000-175,000/year

## Safe Withdrawal Rate

- For 50+ year retirement horizon (late 30s retiring now): 3.25-3.5%
- UK-specific considerations push toward lower end
- Using 3.3% (Morningstar UK recommendation for long horizons)
- With flexibility, could use 3.5%

## Net Worth Calculation

### Scenario 1: Conservative (3.3% SWR, higher tax drag)
- Gross annual need: GBP 175,000
- Net worth needed: GBP 175,000 / 0.033 = GBP 5,303,030
- In USD: ~$6.89M (at 1.30 GBP/USD)

### Scenario 2: Moderate (3.5% SWR, moderate tax efficiency)
- Gross annual need: GBP 168,000
- Net worth needed: GBP 168,000 / 0.035 = GBP 4,800,000
- In USD: ~$6.24M (at 1.30 GBP/USD)

### Scenario 3: With State School (reduces education costs significantly)
- Annual expenses drop to ~GBP 117,000
- Gross need: ~GBP 140,000
- Net worth: GBP 140,000 / 0.033 = GBP 4,242,424
- In USD: ~$5.52M

## Adjustments & Notes

1. **Child costs are temporary**: Private school from age 4-18 = ~14 years. After that,
   expenses drop by ~GBP 30,000/year. But university costs may partially replace this.
2. **State pension**: Both adults will eventually get state pension (~GBP 12,500/year each at
   current rates, from age 67). This provides ~GBP 25,000/year supplemental income later.
3. **Inflation**: Model assumes real (inflation-adjusted) returns, so SWR already accounts for this.
4. **Housing**: Rent will increase with inflation - already embedded in real-return SWR model.
5. **Currency risk**: If investments are in USD but expenses in GBP, there's FX risk.

## Model Results (from retirement_model.py)

### Deterministic SWR Analysis
- Annual expenses: GBP 145,609
- Gross investment income needed: GBP 154,710
- Effective tax rate: ~6% (with ISA + personal allowance optimization)

| SWR   | Net Worth (GBP) | Net Worth (USD) |
|-------|-----------------|-----------------|
| 3.0%  | £5,157,000      | $6,704,000      |
| 3.3%  | £4,688,000      | $6,095,000      |
| 3.5%  | £4,420,000      | $5,746,000      |
| 4.0%  | £3,868,000      | $5,028,000      |

### Monte Carlo Simulation (10,000 runs, 60-year horizon)
| Net Worth   | Success Rate |
|-------------|-------------|
| £4,000,000  | 62.9%       |
| £4,500,000  | 73.1%       |
| £5,000,000  | 80.2%       |
| £5,500,000  | 85.5%       |
| £6,000,000  | 89.6%       |
| £7,000,000  | 94.0%       |

- 90% success rate: ~GBP 6,100,000 ($7,929,000 USD)
- 95% success rate: ~GBP 7,323,000 ($9,520,000 USD)

### Sensitivity: State School
- Annual expenses: GBP 117,709
- At 3.3% SWR: GBP 3,769,000 ($4,900,000 USD)

## FINAL ANSWER

**Central estimate (deterministic, 3.3% SWR with private school):**
- **~GBP 4.7 million / ~$6.1 million USD**

**Conservative estimate (Monte Carlo 90% success, private school):**
- **~GBP 6.1 million / ~$7.9 million USD**

**With state school (deterministic, 3.3% SWR):**
- **~GBP 3.8 million / ~$4.9 million USD**

### Recommended figure: ~$6.5 million USD (~GBP 5 million)
This is between the deterministic and Monte Carlo estimates, providing a reasonable
margin of safety while not being excessively conservative.
