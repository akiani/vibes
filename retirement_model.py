#!/usr/bin/env python3
"""
Retirement Net Worth Calculator
================================
For a family of 2 adults (late 30s) + 1 child in Islington, London.
~1200 sqft rental, no car, upper middle class lifestyle, never work again.

Calculates required net worth using Monte Carlo simulation and
deterministic SWR analysis with UK-specific tax considerations.
"""

import json
import random
import math
from dataclasses import dataclass, field
from typing import Optional

# ============================================================================
# CONFIGURATION & ASSUMPTIONS
# ============================================================================

GBP_USD_RATE = 1.30  # Conservative long-term GBP/USD rate

# Current ages
ADULT_AGE = 38  # Late thirties
CHILD_AGE = 5   # Young child (worst case for education costs)

# Planning horizon
PLANNING_YEARS = 60  # Plan to age ~98
STATE_PENSION_AGE = 67
STATE_PENSION_ANNUAL_PER_PERSON = 12_570  # GBP, current full new state pension ~£12.5K

# Inflation assumption (UK long-term)
UK_INFLATION = 0.03  # 3% - UK historically higher than US

# Investment return assumptions (nominal)
NOMINAL_EQUITY_RETURN = 0.08  # 8% nominal
NOMINAL_BOND_RETURN = 0.04   # 4% nominal
EQUITY_ALLOCATION = 0.75     # 75/25 stock/bond split
BOND_ALLOCATION = 0.25

# Real return (after inflation)
REAL_RETURN = (EQUITY_ALLOCATION * NOMINAL_EQUITY_RETURN +
               BOND_ALLOCATION * NOMINAL_BOND_RETURN) - UK_INFLATION
# = 0.75*0.08 + 0.25*0.04 - 0.03 = 0.06 + 0.01 - 0.03 = 0.04 (4% real)

# Volatility for Monte Carlo
EQUITY_VOLATILITY = 0.17
BOND_VOLATILITY = 0.06
PORTFOLIO_VOLATILITY = math.sqrt(
    (EQUITY_ALLOCATION * EQUITY_VOLATILITY) ** 2 +
    (BOND_ALLOCATION * BOND_VOLATILITY) ** 2 +
    2 * EQUITY_ALLOCATION * BOND_ALLOCATION * 0.2 * EQUITY_VOLATILITY * BOND_VOLATILITY
)

MONTE_CARLO_RUNS = 10_000


# ============================================================================
# ANNUAL EXPENSES (in GBP, 2026 prices)
# ============================================================================

@dataclass
class AnnualExpenses:
    """All annual expenses in GBP at 2026 price levels."""

    # Housing
    rent: float = 3_500 * 12             # £3,500/month for nice 3-bed in Islington
    council_tax: float = 2_459           # Band E Islington 2025/26

    # Utilities
    gas_electric_water: float = 350 * 12  # £350/month avg for 3-bed
    internet: float = 35 * 12
    mobile_phones: float = 40 * 12       # 2 adults
    tv_licence: float = 170
    streaming: float = 40 * 12           # Netflix, Spotify, etc.

    # Food
    groceries: float = 800 * 12          # Waitrose/M&S level, family of 3
    dining_out: float = 500 * 12         # Nice restaurants 2-3x/month + casual
    coffee_cafes: float = 100 * 12

    # Transport (no car)
    travelcards: float = 300 * 12        # 2 adult Oyster Zone 1-2
    child_travel: float = 30 * 12        # Free <11, minimal after
    taxis_uber: float = 150 * 12

    # Education - PRIVATE SCHOOL (upper middle class assumption)
    school_fees: float = 30_000          # ~£10K/term incl. VAT (primary/secondary avg)
    school_extras: float = 2_000         # Uniform, trips, supplies
    after_school_activities: float = 200 * 12  # Music, sports, tutoring

    # Healthcare & Insurance
    private_health_insurance: float = 250 * 12  # Comprehensive family, London premium
    dental_insurance: float = 50 * 12
    life_insurance: float = 40 * 12      # 2 policies, £500K each

    # Clothing & Personal
    clothing: float = 400 * 12           # Family of 3, upper middle class
    grooming: float = 100 * 12

    # Holidays & Travel
    international_holidays: float = 10_000  # 2 intl trips/year
    uk_breaks: float = 3_000

    # Entertainment & Leisure
    culture: float = 200 * 12            # Theatre, cinema, museums
    kids_activities: float = 100 * 12    # Parties, playdates
    gym_fitness: float = 150 * 12        # 2 adult memberships
    hobbies_subscriptions: float = 100 * 12

    # Home & Misc
    contents_insurance: float = 360
    furnishings_maintenance: float = 150 * 12
    gifts: float = 150 * 12
    professional_services: float = 1_200  # Accountant for tax planning
    emergency_buffer: float = 300 * 12

    @property
    def total(self) -> float:
        return sum(getattr(self, f.name) for f in self.__dataclass_fields__.values()
                   if isinstance(getattr(self, f.name), (int, float)))

    def breakdown(self) -> dict:
        """Return expenses grouped by category."""
        categories = {
            "Housing": self.rent + self.council_tax,
            "Utilities & Internet": (self.gas_electric_water + self.internet +
                                     self.mobile_phones + self.tv_licence + self.streaming),
            "Food & Dining": self.groceries + self.dining_out + self.coffee_cafes,
            "Transport": self.travelcards + self.child_travel + self.taxis_uber,
            "Education": self.school_fees + self.school_extras + self.after_school_activities,
            "Healthcare & Insurance": (self.private_health_insurance +
                                       self.dental_insurance + self.life_insurance),
            "Clothing & Personal": self.clothing + self.grooming,
            "Holidays & Travel": self.international_holidays + self.uk_breaks,
            "Entertainment & Leisure": (self.culture + self.kids_activities +
                                        self.gym_fitness + self.hobbies_subscriptions),
            "Home & Miscellaneous": (self.contents_insurance + self.furnishings_maintenance +
                                     self.gifts + self.professional_services +
                                     self.emergency_buffer),
        }
        return categories


# ============================================================================
# TAX MODEL
# ============================================================================

def calculate_uk_tax_on_investment_income(gross_income: float, year_offset: int = 0) -> float:
    """
    Estimate UK tax on investment income for a non-working couple.

    Assumes:
    - Income split between two adults
    - Mix of ISA (tax-free) and taxable investment income
    - Dividends + capital gains as primary income sources
    - ISA pot provides some tax-free income

    Returns the total tax payable.
    """
    # Assume over time, a well-managed portfolio has significant ISA holdings
    # Couple can shelter £40K/year into ISAs (£20K each)
    # Over 10+ years, ISA pots become substantial
    # Assume 40% of income comes from ISAs (tax-free) for a mature portfolio
    isa_fraction = 0.35  # 35% from ISAs tax-free

    taxable_income = gross_income * (1 - isa_fraction)

    # Split between two adults
    per_person = taxable_income / 2

    # Personal allowance: £12,570
    personal_allowance = 12_570

    # Assume income is mix of dividends (60%) and capital gains (40%)
    dividend_fraction = 0.60
    cg_fraction = 0.40

    dividend_income = per_person * dividend_fraction
    cg_income = per_person * cg_fraction

    # Dividend tax (per person)
    dividend_allowance = 500
    taxable_dividends = max(0, dividend_income - dividend_allowance)

    # Use personal allowance against dividends first
    pa_remaining = max(0, personal_allowance - 0)  # No other income
    taxable_dividends_after_pa = max(0, taxable_dividends - pa_remaining)

    # Dividend tax rates (2025/26)
    basic_rate_limit = 37_700  # £50,270 - £12,570
    dividend_tax = 0
    if taxable_dividends_after_pa > 0:
        basic_portion = min(taxable_dividends_after_pa, basic_rate_limit)
        higher_portion = max(0, taxable_dividends_after_pa - basic_rate_limit)
        dividend_tax = basic_portion * 0.0875 + higher_portion * 0.3375

    # Capital gains tax (per person)
    cg_allowance = 3_000
    taxable_cg = max(0, cg_income - cg_allowance)

    # CGT rates: 18% basic, 24% higher
    # Need to check if basic rate band is used up by dividends
    basic_band_used = min(dividend_income, basic_rate_limit + personal_allowance)
    basic_band_remaining = max(0, (basic_rate_limit + personal_allowance) - basic_band_used)

    cg_basic = min(taxable_cg, basic_band_remaining)
    cg_higher = max(0, taxable_cg - basic_band_remaining)
    cg_tax = cg_basic * 0.18 + cg_higher * 0.24

    total_tax_per_person = dividend_tax + cg_tax
    total_tax = total_tax_per_person * 2

    return total_tax


def gross_income_needed(net_spending: float) -> float:
    """Binary search for gross income that yields desired net spending after tax."""
    low, high = net_spending, net_spending * 2
    for _ in range(100):
        mid = (low + high) / 2
        tax = calculate_uk_tax_on_investment_income(mid)
        net = mid - tax
        if abs(net - net_spending) < 100:
            return mid
        if net < net_spending:
            low = mid
        else:
            high = mid
    return high


# ============================================================================
# EXPENSE PROJECTION OVER TIME
# ============================================================================

def project_annual_expenses(base_expenses: AnnualExpenses, year: int) -> float:
    """
    Project real (inflation-adjusted) expenses for a given year.

    Accounts for:
    - Child aging out of school fees (after ~13-14 years)
    - University costs (3-4 years)
    - State pension kicking in (year ~29 for age 67)
    - Reduced expenses in later life
    """
    child_age_in_year = CHILD_AGE + year
    adult_age_in_year = ADULT_AGE + year

    base = base_expenses.total

    # Education cost adjustments (all in real terms)
    education_cost = (base_expenses.school_fees + base_expenses.school_extras +
                      base_expenses.after_school_activities)

    if child_age_in_year > 18:
        # Child finished secondary school
        base -= education_cost

        if 18 <= child_age_in_year <= 21:
            # University years - assume some parental support
            # Tuition ~£9,250/year + living costs ~£12,000/year
            base += 21_000
        elif child_age_in_year > 21:
            # Child independent - reduce some family costs
            base -= 3_000  # Less food, activities, etc.

    # State pension (from age 67, for both adults)
    if adult_age_in_year >= STATE_PENSION_AGE:
        state_pension_income = STATE_PENSION_ANNUAL_PER_PERSON * 2
        base -= state_pension_income  # Reduces amount needed from investments

    # Later life adjustment (reduced spending from ~age 75)
    if adult_age_in_year >= 75:
        # Less travel, dining out, but more healthcare
        base *= 0.90  # Net ~10% reduction

    if adult_age_in_year >= 85:
        base *= 0.90  # Further reduction (compounding with above = ~19% total)

    return max(base, 20_000)  # Floor of £20K/year minimum


# ============================================================================
# DETERMINISTIC SWR ANALYSIS
# ============================================================================

def deterministic_analysis(expenses: AnnualExpenses):
    """Calculate required net worth using fixed SWR assumptions."""
    print("=" * 70)
    print("DETERMINISTIC SAFE WITHDRAWAL RATE ANALYSIS")
    print("=" * 70)

    # Calculate base expenses
    annual_spend = expenses.total
    breakdown = expenses.breakdown()

    print(f"\n--- Annual Expense Breakdown (GBP, 2026 prices) ---")
    for category, amount in sorted(breakdown.items(), key=lambda x: -x[1]):
        pct = amount / annual_spend * 100
        print(f"  {category:<30s} £{amount:>10,.0f}  ({pct:5.1f}%)")
    print(f"  {'─' * 50}")
    print(f"  {'TOTAL':<30s} £{annual_spend:>10,.0f}")

    # Gross income needed (after tax)
    gross = gross_income_needed(annual_spend)
    tax = calculate_uk_tax_on_investment_income(gross)
    effective_tax_rate = tax / gross * 100

    print(f"\n--- Tax Analysis ---")
    print(f"  Net spending needed:        £{annual_spend:>10,.0f}")
    print(f"  Gross investment income:    £{gross:>10,.0f}")
    print(f"  Estimated tax:              £{tax:>10,.0f}")
    print(f"  Effective tax rate:          {effective_tax_rate:>9.1f}%")

    print(f"\n--- Required Net Worth by SWR ---")
    swr_rates = [0.030, 0.033, 0.035, 0.040]

    results = {}
    for swr in swr_rates:
        net_worth_gbp = gross / swr
        net_worth_usd = net_worth_gbp * GBP_USD_RATE
        results[swr] = net_worth_gbp
        print(f"  SWR {swr*100:.1f}%: £{net_worth_gbp:>12,.0f} GBP "
              f"(${net_worth_usd:>12,.0f} USD)")

    return results


# ============================================================================
# MONTE CARLO SIMULATION
# ============================================================================

def monte_carlo_simulation(initial_net_worth: float, expenses: AnnualExpenses,
                           n_runs: int = MONTE_CARLO_RUNS) -> dict:
    """
    Run Monte Carlo simulation to test if a given net worth survives.

    Returns dict with success rate and statistics.
    """
    random.seed(42)
    successes = 0
    final_values = []
    min_ever = []
    years_survived = []

    for _ in range(n_runs):
        portfolio = initial_net_worth
        survived = True
        min_val = portfolio

        for year in range(PLANNING_YEARS):
            # Random return (log-normal)
            real_return = random.gauss(REAL_RETURN, PORTFOLIO_VOLATILITY)

            # Calculate this year's expenses
            real_expenses = project_annual_expenses(expenses, year)
            gross_needed = gross_income_needed(real_expenses)

            # Withdraw and grow
            portfolio -= gross_needed
            portfolio *= (1 + real_return)

            min_val = min(min_val, portfolio)

            if portfolio <= 0:
                survived = False
                years_survived.append(year)
                break

        if survived:
            successes += 1
            final_values.append(portfolio)
            years_survived.append(PLANNING_YEARS)

        min_ever.append(min_val)

    success_rate = successes / n_runs
    avg_final = sum(final_values) / len(final_values) if final_values else 0
    median_final = sorted(final_values)[len(final_values) // 2] if final_values else 0
    avg_min = sum(min_ever) / len(min_ever)
    avg_years = sum(years_survived) / len(years_survived)

    return {
        "success_rate": success_rate,
        "avg_final_value": avg_final,
        "median_final_value": median_final,
        "avg_minimum_value": avg_min,
        "avg_years_survived": avg_years,
        "n_runs": n_runs,
    }


def find_required_net_worth(expenses: AnnualExpenses,
                            target_success: float = 0.95) -> float:
    """Binary search for the net worth that achieves target success rate."""
    low = 2_000_000
    high = 10_000_000

    for _ in range(20):  # ~20 iterations gives good precision
        mid = (low + high) / 2
        result = monte_carlo_simulation(mid, expenses, n_runs=5_000)
        if result["success_rate"] >= target_success:
            high = mid
        else:
            low = mid

    return (low + high) / 2


# ============================================================================
# MAIN
# ============================================================================

def main():
    expenses = AnnualExpenses()

    print("\n" + "=" * 70)
    print("  RETIREMENT NET WORTH CALCULATOR")
    print("  Family: 2 Adults (38yo) + 1 Child (5yo)")
    print("  Location: Islington, London")
    print("  Lifestyle: Upper Middle Class, No Car, ~1200sqft Rental")
    print("=" * 70)

    # ── Part 1: Deterministic Analysis ──
    det_results = deterministic_analysis(expenses)

    # ── Part 2: Monte Carlo Simulation ──
    print("\n" + "=" * 70)
    print("MONTE CARLO SIMULATION (10,000 runs, 60-year horizon)")
    print("=" * 70)

    # Test several net worth levels
    test_amounts = [4_000_000, 4_500_000, 5_000_000, 5_500_000, 6_000_000, 7_000_000]

    print(f"\n{'Net Worth (GBP)':>20s} | {'Success Rate':>12s} | {'Avg Final (GBP)':>16s} | "
          f"{'Median Final':>14s} | {'Avg Yrs':>8s}")
    print("-" * 85)

    for amount in test_amounts:
        result = monte_carlo_simulation(amount, expenses)
        print(f"  £{amount:>14,.0f} | {result['success_rate']:>11.1%} | "
              f"£{result['avg_final_value']:>14,.0f} | "
              f"£{result['median_final_value']:>12,.0f} | "
              f"{result['avg_years_survived']:>7.1f}")

    # ── Part 3: Find exact net worth for 95% success ──
    print(f"\n--- Finding Net Worth for 95% Success Rate ---")
    required_95 = find_required_net_worth(expenses, target_success=0.95)
    print(f"  95% success: £{required_95:>12,.0f} GBP (${required_95 * GBP_USD_RATE:>12,.0f} USD)")

    print(f"\n--- Finding Net Worth for 90% Success Rate ---")
    required_90 = find_required_net_worth(expenses, target_success=0.90)
    print(f"  90% success: £{required_90:>12,.0f} GBP (${required_90 * GBP_USD_RATE:>12,.0f} USD)")

    # ── Part 4: Sensitivity Analysis ──
    print("\n" + "=" * 70)
    print("SENSITIVITY ANALYSIS")
    print("=" * 70)

    # State school scenario
    state_school_expenses = AnnualExpenses(
        school_fees=0,
        school_extras=500,
        after_school_activities=500 * 12,  # More activities to compensate
    )
    # Keep all other defaults but override education
    state_school_expenses.school_fees = 0
    state_school_expenses.school_extras = 500
    state_school_expenses.after_school_activities = 500 * 12

    state_annual = state_school_expenses.total
    state_gross = gross_income_needed(state_annual)

    print(f"\n  Scenario: State School (no private school fees)")
    print(f"  Annual expenses: £{state_annual:>10,.0f}")
    print(f"  Gross needed:    £{state_gross:>10,.0f}")
    for swr in [0.033, 0.035]:
        nw = state_gross / swr
        print(f"  SWR {swr*100:.1f}%: £{nw:>12,.0f} GBP (${nw * GBP_USD_RATE:>12,.0f} USD)")

    # More frugal scenario (still comfortable)
    frugal_expenses = AnnualExpenses(
        rent=2_800 * 12,            # Slightly less prime location
        groceries=600 * 12,         # Still good quality
        dining_out=300 * 12,        # Less frequent
        international_holidays=6_000,
        uk_breaks=2_000,
        clothing=250 * 12,
        school_fees=30_000,         # Still private school
    )
    frugal_annual = frugal_expenses.total
    frugal_gross = gross_income_needed(frugal_annual)

    print(f"\n  Scenario: More Moderate (still comfortable)")
    print(f"  Annual expenses: £{frugal_annual:>10,.0f}")
    print(f"  Gross needed:    £{frugal_gross:>10,.0f}")
    for swr in [0.033, 0.035]:
        nw = frugal_gross / swr
        print(f"  SWR {swr*100:.1f}%: £{nw:>12,.0f} GBP (${nw * GBP_USD_RATE:>12,.0f} USD)")

    # ── Part 5: Final Summary ──
    print("\n" + "=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)

    central_gbp = det_results[0.033]
    central_usd = central_gbp * GBP_USD_RATE

    print(f"""
  Base annual expenses:     £{expenses.total:>10,.0f} GBP
  Gross income needed:      £{gross_income_needed(expenses.total):>10,.0f} GBP

  ┌─────────────────────────────────────────────────────────┐
  │  RECOMMENDED NET WORTH (Private School, 3.3% SWR):     │
  │                                                         │
  │     £{central_gbp:>10,.0f} GBP  /  ${central_usd:>10,.0f} USD          │
  │                                                         │
  │  Monte Carlo 95% success:                               │
  │     £{required_95:>10,.0f} GBP  /  ${required_95 * GBP_USD_RATE:>10,.0f} USD          │
  └─────────────────────────────────────────────────────────┘

  With state school:  £{state_gross / 0.033:>10,.0f} GBP  (${state_gross / 0.033 * GBP_USD_RATE:>10,.0f} USD)

  Key assumptions:
  - 3.3% safe withdrawal rate (50+ year horizon, UK-adjusted)
  - 75/25 equity/bond allocation
  - 4% real return after inflation
  - ~{calculate_uk_tax_on_investment_income(gross_income_needed(expenses.total)) / gross_income_needed(expenses.total) * 100:.0f}% effective tax rate on investment income
  - Private school until age 18, partial university support
  - State pension supplements income from age 67
  - GBP/USD rate: {GBP_USD_RATE}

  ═══════════════════════════════════════════════════════════
  BOTTOM LINE: ~£5 million GBP / ~$6.5 million USD
  ═══════════════════════════════════════════════════════════
""")


if __name__ == "__main__":
    main()
