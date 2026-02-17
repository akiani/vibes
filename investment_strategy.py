#!/usr/bin/env python3
"""
Investment Strategy: $2.5M → Target Net Worth
==============================================
Models how to invest $2.5M to reach the retirement target (~£5M / ~$6.5M)
with minimal stress for a family in their late 30s.

Covers:
- Account structure (ISA / SIPP / GIA) and tax wrapper strategy
- Asset allocation (passive index funds)
- Growth projections with and without additional contributions
- Monte Carlo projections for timeline confidence
"""

import math
import random
from dataclasses import dataclass

# ============================================================================
# CONSTANTS
# ============================================================================

GBP_USD = 1.30
STARTING_USD = 2_500_000
STARTING_GBP = STARTING_USD / GBP_USD  # ~£1,923,077

# Targets (from retirement_model.py)
TARGET_DETERMINISTIC_GBP = 4_700_000  # 3.3% SWR
TARGET_MC90_GBP = 6_100_000           # Monte Carlo 90% success
TARGET_RECOMMENDED_GBP = 5_000_000    # Our recommended middle ground

# UK tax allowances (2025/26)
ISA_ANNUAL_ALLOWANCE = 20_000     # Per person
SIPP_ANNUAL_ALLOWANCE = 60_000    # Per person (including tax relief)
PERSONAL_ALLOWANCE = 12_570
CGT_ANNUAL_ALLOWANCE = 3_000      # Per person
DIVIDEND_ALLOWANCE = 500          # Per person

# Investment return assumptions
UK_INFLATION = 0.03
NOMINAL_RETURN_SCENARIOS = {
    "conservative": 0.06,   # ~3% real
    "moderate": 0.07,       # ~4% real
    "optimistic": 0.08,     # ~5% real
}
PORTFOLIO_VOLATILITY = 0.13  # For 80/20 equity/bond blend

MONTE_CARLO_RUNS = 10_000


# ============================================================================
# RECOMMENDED PORTFOLIO
# ============================================================================

@dataclass
class Fund:
    name: str
    ticker: str
    allocation_pct: float
    ocf_pct: float  # Ongoing charges figure
    description: str


RECOMMENDED_PORTFOLIO = [
    Fund(
        name="Vanguard FTSE All-World UCITS ETF (Acc)",
        ticker="VWRP",
        allocation_pct=80,
        ocf_pct=0.22,
        description="Global equities - 3,700+ stocks across developed & emerging markets"
    ),
    Fund(
        name="Vanguard Global Aggregate Bond UCITS ETF (GBP Hedged)",
        ticker="VAGP",
        allocation_pct=15,
        ocf_pct=0.10,
        description="Global investment-grade bonds, hedged to GBP to remove FX risk on the safe portion"
    ),
    Fund(
        name="Vanguard UK Gilt UCITS ETF",
        ticker="VGOV",
        allocation_pct=5,
        ocf_pct=0.07,
        description="UK government bonds - ultra-safe, GBP-denominated, inflation linkage to UK rates"
    ),
]

# One-fund alternative
ONE_FUND_OPTION = Fund(
    name="Vanguard LifeStrategy 80% Equity Fund (Acc)",
    ticker="LS80",
    allocation_pct=100,
    ocf_pct=0.22,
    description="All-in-one fund: ~80% global equities, ~20% bonds. Auto-rebalancing. Zero effort."
)


# ============================================================================
# ACCOUNT STRUCTURE
# ============================================================================

def calculate_account_structure(total_gbp: float) -> dict:
    """
    Recommend how to split the money across ISA, SIPP, and GIA.

    Assumes:
    - Couple (2 ISA allowances, 2 SIPP allowances)
    - Starting from scratch in ISAs (worst case)
    - Some existing pension (SIPP) may exist
    """
    # Year 1 ISA capacity: £40K (£20K x 2)
    # Existing ISAs: assume minimal (£0 for conservative modeling)
    # SIPP: can't access until 57, so don't over-allocate for someone who
    #   wants to retire in their 30s/40s - need accessible money first

    # Strategy: maximize ISA first (accessible, tax-free),
    # then SIPP for long-term (post-57), rest in GIA

    isa_current = 0  # Assume starting fresh
    sipp_current = 0

    # For someone retiring soon, we want MOST money accessible (ISA + GIA)
    # SIPP is locked until 57, so limit SIPP to ~20-25% for long-term hedge
    sipp_allocation = min(total_gbp * 0.20, 300_000)  # Cap at £300K or 20%
    isa_allocation = min(total_gbp * 0.30, total_gbp - sipp_allocation)  # Aspirational - will take years to fill
    gia_allocation = total_gbp - isa_allocation - sipp_allocation

    # But ISAs can only be filled at £40K/year for a couple
    # So realistically at start: most is in GIA, then bed-and-ISA over time
    year1_isa = min(40_000, total_gbp)
    year1_gia = total_gbp - year1_isa - sipp_allocation

    return {
        "total_gbp": total_gbp,
        "year1": {
            "isa": year1_isa,
            "sipp": sipp_allocation,
            "gia": year1_gia,
        },
        "target_long_term": {
            "isa": isa_allocation,
            "sipp": sipp_allocation,
            "gia": gia_allocation,
        },
        "annual_isa_transfer": 40_000,  # Bed-and-ISA each year
    }


# ============================================================================
# GROWTH PROJECTIONS
# ============================================================================

def project_growth_deterministic(
    starting_gbp: float,
    annual_contribution: float = 0,
    nominal_return: float = 0.07,
    years: int = 25,
) -> list:
    """Project portfolio growth year by year (deterministic)."""
    results = []
    portfolio = starting_gbp

    for year in range(1, years + 1):
        portfolio *= (1 + nominal_return)
        portfolio += annual_contribution
        results.append({
            "year": year,
            "age": 38 + year,
            "nominal_gbp": portfolio,
            "real_gbp": portfolio / ((1 + UK_INFLATION) ** year),
            "nominal_usd": portfolio * GBP_USD,
        })

    return results


def years_to_target(starting_gbp: float, target_gbp: float,
                    annual_contribution: float = 0,
                    nominal_return: float = 0.07) -> float:
    """Calculate years needed to reach target."""
    portfolio = starting_gbp
    for year in range(1, 100):
        portfolio *= (1 + nominal_return)
        portfolio += annual_contribution
        if portfolio >= target_gbp:
            # Interpolate for partial year
            prev = (portfolio - annual_contribution) / (1 + nominal_return)
            prev_grown = prev * (1 + nominal_return) + annual_contribution
            return year
    return float('inf')


def monte_carlo_years_to_target(
    starting_gbp: float,
    target_gbp: float,
    annual_contribution: float = 0,
    nominal_return: float = 0.07,
    volatility: float = PORTFOLIO_VOLATILITY,
    n_runs: int = MONTE_CARLO_RUNS,
) -> dict:
    """Monte Carlo simulation for time to reach target."""
    random.seed(42)
    years_list = []

    for _ in range(n_runs):
        portfolio = starting_gbp
        reached = False

        for year in range(1, 60):
            ret = random.gauss(nominal_return, volatility)
            portfolio *= (1 + ret)
            portfolio += annual_contribution

            if portfolio >= target_gbp:
                years_list.append(year)
                reached = True
                break

        if not reached:
            years_list.append(60)  # Cap

    years_list.sort()
    return {
        "median_years": years_list[len(years_list) // 2],
        "p25_years": years_list[len(years_list) // 4],
        "p75_years": years_list[3 * len(years_list) // 4],
        "p90_years": years_list[int(0.9 * len(years_list))],
        "mean_years": sum(years_list) / len(years_list),
        "pct_never": sum(1 for y in years_list if y >= 60) / len(years_list) * 100,
    }


# ============================================================================
# TAX EFFICIENCY MODEL
# ============================================================================

def annual_tax_drag_gia(gia_value: float, nominal_return: float) -> float:
    """
    Estimate annual tax drag on a GIA for a non-working couple.

    Growth inside GIA is subject to CGT (on rebalancing/sales) and
    dividend tax. With careful management, this can be minimized.
    """
    # Assume 1.5% dividend yield, rest is capital growth
    dividend_yield = 0.015
    capital_growth = nominal_return - dividend_yield

    dividends = gia_value * dividend_yield
    # Both adults: 2 x £500 dividend allowance + 2 x £12,570 personal allowance
    # Against dividends
    tax_free_dividends = 2 * 500 + 2 * 12_570  # But PA is shared with other income
    # If no other income, dividends up to PA are tax-free
    taxable_dividends = max(0, dividends - 2 * (12_570 + 500))
    dividend_tax = taxable_dividends * 0.0875  # Basic rate

    # CGT: only triggered on sales. With buy-and-hold, minimal.
    # Annual bed-and-ISA triggers ~£40K of sales, but within CGT allowance
    cgt_triggered = max(0, 40_000 * capital_growth / (1 + capital_growth) - 2 * 3_000)
    cgt = max(0, cgt_triggered) * 0.18

    return dividend_tax + cgt


def project_with_tax_efficiency(starting_gbp: float, nominal_return: float = 0.07,
                                annual_contribution: float = 0, years: int = 25) -> list:
    """
    Project growth with realistic tax wrapper modeling.

    Models ISA, SIPP, and GIA separately, with annual bed-and-ISA transfers.
    """
    # Initial allocation
    isa = 40_000  # Max year 1 couple ISA
    sipp = starting_gbp * 0.15  # 15% in SIPP (locked until 57)
    gia = starting_gbp - isa - sipp

    results = []
    for year in range(1, years + 1):
        # Grow each wrapper
        isa *= (1 + nominal_return)
        sipp *= (1 + nominal_return)

        # GIA has tax drag
        tax_drag = annual_tax_drag_gia(gia, nominal_return)
        gia *= (1 + nominal_return)
        gia -= tax_drag

        # Annual bed-and-ISA: sell from GIA, buy into ISA (up to £40K)
        bed_and_isa = min(40_000, gia)
        gia -= bed_and_isa
        isa += bed_and_isa

        # Add contributions (if still working)
        if annual_contribution > 0:
            # Split: fill ISA first (remaining capacity), then GIA
            isa_capacity = max(0, 40_000 - bed_and_isa)  # Already did bed-and-ISA
            to_isa = min(annual_contribution, isa_capacity)
            to_gia = annual_contribution - to_isa
            isa += to_isa
            gia += to_gia

        total = isa + sipp + gia
        results.append({
            "year": year,
            "age": 38 + year,
            "isa": isa,
            "sipp": sipp,
            "gia": gia,
            "total_gbp": total,
            "total_usd": total * GBP_USD,
            "isa_pct": isa / total * 100,
        })

    return results


# ============================================================================
# MAIN OUTPUT
# ============================================================================

def main():
    print("=" * 74)
    print("  INVESTMENT STRATEGY: $2.5M → RETIREMENT TARGET")
    print("  Starting: $2.5M USD = £{:,.0f} GBP".format(STARTING_GBP))
    print("  Target:   ~£5.0M GBP = ~$6.5M USD (recommended)")
    print("=" * 74)

    # ── Section 1: Recommended Portfolio ──
    print("\n" + "─" * 74)
    print("  1. RECOMMENDED PORTFOLIO (Minimal Stress)")
    print("─" * 74)

    print("\n  OPTION A: Three-ETF Portfolio (slightly more control)")
    print("  ┌────────────────────────────────────────────────────────────────┐")
    weighted_ocf = 0
    for fund in RECOMMENDED_PORTFOLIO:
        print(f"  │  {fund.allocation_pct:>3.0f}%  {fund.ticker:<6s}  {fund.name}")
        print(f"  │        OCF: {fund.ocf_pct:.2f}%  │  {fund.description}")
        weighted_ocf += fund.allocation_pct / 100 * fund.ocf_pct
    print(f"  │  Weighted OCF: {weighted_ocf:.2f}%")
    print(f"  │  Rebalance: Once per year (15 minutes of work)")
    print("  └────────────────────────────────────────────────────────────────┘")

    print(f"\n  OPTION B: One-Fund Solution (absolute minimum effort)")
    print("  ┌────────────────────────────────────────────────────────────────┐")
    print(f"  │  100%  {ONE_FUND_OPTION.ticker:<6s}  {ONE_FUND_OPTION.name}")
    print(f"  │        OCF: {ONE_FUND_OPTION.ocf_pct:.2f}%")
    print(f"  │        {ONE_FUND_OPTION.description}")
    print(f"  │  Rebalance: NEVER (fund does it automatically)")
    print("  └────────────────────────────────────────────────────────────────┘")

    # ── Section 2: Account Structure ──
    print("\n" + "─" * 74)
    print("  2. ACCOUNT STRUCTURE (Tax Wrapper Strategy)")
    print("─" * 74)

    acct = calculate_account_structure(STARTING_GBP)
    print(f"""
  Starting: £{acct['total_gbp']:,.0f}

  Year 1 Allocation:
    ISA  (2 x £20K):  £{acct['year1']['isa']:>10,.0f}  ← Tax-free growth & withdrawals
    SIPP:             £{acct['year1']['sipp']:>10,.0f}  ← Tax-free growth, locked til 57
    GIA:              £{acct['year1']['gia']:>10,.0f}  ← Taxable, but flexible

  Annual Actions (15 min/year):
    1. Bed-and-ISA: Sell £40K from GIA → Buy same funds in ISA
       (uses both adults' £20K ISA allowances)
    2. Rebalance if >5% drift from target allocation
    3. Harvest CGT allowance: sell/rebuy £6K of gains (2 x £3K)

  Over time, the ISA grows and shelters more income from tax.
  After ~{acct['target_long_term']['isa'] / 40_000:.0f} years, ~£{acct['target_long_term']['isa']:,.0f} will be in ISAs (tax-free).""")

    # ── Section 3: Platform Recommendation ──
    print("\n" + "─" * 74)
    print("  3. PLATFORM RECOMMENDATION")
    print("─" * 74)
    print(f"""
  For £{STARTING_GBP:,.0f}+, flat-fee platforms save thousands vs percentage-based:

  ┌─────────────────────────────────────────────────────────────────────┐
  │  RECOMMENDED: Interactive Investor (ii)                            │
  │  - Flat fee: ~£156/year (ISA + SIPP combined)                     │
  │  - vs Vanguard: £375/year (0.15% capped)                          │
  │  - vs Hargreaves Lansdown: £3,846/year (0.2% on £1.92M!)          │
  │  - Saving vs HL: ~£3,690/year                                     │
  │                                                                     │
  │  ALTERNATIVE: InvestEngine (£0 platform fee for ETFs)              │
  │  - Best if you only want ETFs (VWRP, VAGP, VGOV)                  │
  │  - Limited SIPP features compared to ii                            │
  └─────────────────────────────────────────────────────────────────────┘""")

    # ── Section 4: Growth Projections ──
    print("\n" + "─" * 74)
    print("  4. GROWTH PROJECTIONS")
    print("─" * 74)

    # Scenario A: No additional contributions (retired immediately)
    print("\n  Scenario A: No additional contributions (stop working now)")
    print(f"  {'Year':>4s}  {'Age':>3s}  {'Nominal GBP':>14s}  {'Real GBP':>14s}  {'USD':>14s}  {'Status':>12s}")
    print("  " + "-" * 68)

    for scenario_name, rate in NOMINAL_RETURN_SCENARIOS.items():
        results = project_growth_deterministic(STARTING_GBP, 0, rate, 25)
        yrs = years_to_target(STARTING_GBP, TARGET_RECOMMENDED_GBP, 0, rate)
        print(f"\n  {scenario_name.upper()} ({rate*100:.0f}% nominal / {(rate-UK_INFLATION)*100:.0f}% real):")
        for r in results:
            if r["year"] in [1, 3, 5, 7, 10, 13, 15, 20, 25]:
                hit = "TARGET!" if r["nominal_gbp"] >= TARGET_RECOMMENDED_GBP else ""
                if r["nominal_gbp"] >= TARGET_MC90_GBP:
                    hit = "MC90 TARGET!"
                print(f"  {r['year']:>4d}  {r['age']:>3d}  £{r['nominal_gbp']:>12,.0f}  "
                      f"£{r['real_gbp']:>12,.0f}  ${r['nominal_usd']:>12,.0f}  {hit}")
        print(f"  → Years to £5M target: ~{yrs:.0f} years (age {38 + yrs:.0f})")

    # Scenario B: Contributing £50K/year while still working
    print(f"\n\n  Scenario B: Contributing £50K/year (~$65K) while working")
    print(f"  {'Year':>4s}  {'Age':>3s}  {'Nominal GBP':>14s}  {'Real GBP':>14s}  {'USD':>14s}  {'Status':>12s}")
    print("  " + "-" * 68)

    contrib = 50_000
    for scenario_name, rate in NOMINAL_RETURN_SCENARIOS.items():
        results = project_growth_deterministic(STARTING_GBP, contrib, rate, 20)
        yrs = years_to_target(STARTING_GBP, TARGET_RECOMMENDED_GBP, contrib, rate)
        print(f"\n  {scenario_name.upper()} ({rate*100:.0f}% nominal / {(rate-UK_INFLATION)*100:.0f}% real):")
        for r in results:
            if r["year"] in [1, 3, 5, 7, 10, 13, 15, 20]:
                hit = "TARGET!" if r["nominal_gbp"] >= TARGET_RECOMMENDED_GBP else ""
                if r["nominal_gbp"] >= TARGET_MC90_GBP:
                    hit = "MC90 TARGET!"
                print(f"  {r['year']:>4d}  {r['age']:>3d}  £{r['nominal_gbp']:>12,.0f}  "
                      f"£{r['real_gbp']:>12,.0f}  ${r['nominal_usd']:>12,.0f}  {hit}")
        print(f"  → Years to £5M target: ~{yrs:.0f} years (age {38 + yrs:.0f})")

    # ── Section 5: Monte Carlo Timeline ──
    print("\n\n" + "─" * 74)
    print("  5. MONTE CARLO: WHEN WILL YOU HIT THE TARGET?")
    print("─" * 74)

    scenarios = [
        ("No contributions, 7% nominal", 0, 0.07),
        ("£50K/yr contributions, 7% nominal", 50_000, 0.07),
        ("£100K/yr contributions, 7% nominal", 100_000, 0.07),
        ("No contributions, 8% nominal", 0, 0.08),
    ]

    for target_name, target_val in [("£5.0M (recommended)", TARGET_RECOMMENDED_GBP),
                                     ("£4.7M (deterministic)", TARGET_DETERMINISTIC_GBP)]:
        print(f"\n  Target: {target_name}")
        print(f"  {'Scenario':<42s} {'Median':>7s} {'25th%':>7s} {'75th%':>7s} {'90th%':>7s} {'Never%':>7s}")
        print("  " + "-" * 72)

        for name, contrib, ret in scenarios:
            mc = monte_carlo_years_to_target(STARTING_GBP, target_val, contrib, ret)
            print(f"  {name:<42s} {mc['median_years']:>5d}yr {mc['p25_years']:>5d}yr "
                  f"{mc['p75_years']:>5d}yr {mc['p90_years']:>5d}yr {mc['pct_never']:>6.1f}%")

    # ── Section 6: Tax-Efficient Growth ──
    print("\n\n" + "─" * 74)
    print("  6. TAX-EFFICIENT WRAPPER PROGRESSION")
    print("─" * 74)

    tax_results = project_with_tax_efficiency(STARTING_GBP, 0.07, 0, 20)
    print(f"\n  How your money migrates from GIA → ISA over time (no contributions):")
    print(f"  {'Year':>4s} {'Age':>3s}  {'ISA':>12s}  {'SIPP':>12s}  {'GIA':>12s}  "
          f"{'Total':>12s}  {'ISA%':>5s}")
    print("  " + "-" * 62)
    for r in tax_results:
        if r["year"] in [1, 2, 3, 5, 7, 10, 15, 20]:
            print(f"  {r['year']:>4d} {r['age']:>3d}  £{r['isa']:>10,.0f}  £{r['sipp']:>10,.0f}  "
                  f"£{r['gia']:>10,.0f}  £{r['total_gbp']:>10,.0f}  {r['isa_pct']:>4.0f}%")

    # ── Section 7: Action Plan ──
    print("\n\n" + "=" * 74)
    print("  7. MINIMAL-STRESS ACTION PLAN")
    print("=" * 74)

    mc_moderate = monte_carlo_years_to_target(STARTING_GBP, TARGET_RECOMMENDED_GBP, 0, 0.07)
    mc_with_contrib = monte_carlo_years_to_target(STARTING_GBP, TARGET_RECOMMENDED_GBP, 50_000, 0.07)

    print(f"""
  ONE-TIME SETUP (~2 hours):
  ─────────────────────────
  1. Open accounts at Interactive Investor (or InvestEngine):
     - Stocks & Shares ISA (for you)
     - Stocks & Shares ISA (for partner)
     - SIPP (for you)
     - GIA (for remaining funds)

  2. Transfer/deposit funds:
     - £20,000 into each ISA (£40,000 total)
     - £{STARTING_GBP * 0.15:,.0f} into SIPP
     - £{STARTING_GBP - 40_000 - STARTING_GBP * 0.15:,.0f} into GIA

  3. Buy in ALL accounts (same allocation everywhere):
     - 80% VWRP (Vanguard FTSE All-World ETF, accumulating)
     - 15% VAGP (Vanguard Global Aggregate Bond, GBP hedged)
     -  5% VGOV (Vanguard UK Gilt ETF)
     OR simply: 100% Vanguard LifeStrategy 80% Equity (Acc)

  ANNUAL MAINTENANCE (~30 min/year, every April):
  ────────────────────────────────────────────────
  1. Bed-and-ISA: Sell £40K from GIA → buy same in new tax year ISAs
  2. Check allocation - rebalance if >5% off target
  3. Harvest CGT: sell/rebuy gains up to £6K (2 x £3K allowance)
  4. If still earning: contribute to ISA first, then GIA

  THAT'S IT. Do nothing else. Don't check daily. Don't panic-sell.

  EXPECTED TIMELINE (no additional contributions):
  ────────────────────────────────────────────────
  Median time to £5M target:  {mc_moderate['median_years']} years (age {38 + mc_moderate['median_years']})
  25th percentile (lucky):    {mc_moderate['p25_years']} years (age {38 + mc_moderate['p25_years']})
  75th percentile (unlucky):  {mc_moderate['p75_years']} years (age {38 + mc_moderate['p75_years']})

  WITH £50K/year contributions:
  Median time to £5M target:  {mc_with_contrib['median_years']} years (age {38 + mc_with_contrib['median_years']})
  25th percentile (lucky):    {mc_with_contrib['p25_years']} years (age {38 + mc_with_contrib['p25_years']})
  75th percentile (unlucky):  {mc_with_contrib['p75_years']} years (age {38 + mc_with_contrib['p75_years']})

  ╔══════════════════════════════════════════════════════════════════════╗
  ║  BOTTOM LINE:                                                      ║
  ║                                                                    ║
  ║  With $2.5M invested passively and no further contributions,       ║
  ║  you'll likely hit the £5M/$6.5M target in ~{mc_moderate['median_years']} years (age ~{38 + mc_moderate['median_years']}).  ║
  ║                                                                    ║
  ║  If you can save £50K/yr while working, that drops to ~{mc_with_contrib['median_years']} years.  ║
  ║                                                                    ║
  ║  Total effort: ~2 hours setup + ~30 minutes per year.              ║
  ╚══════════════════════════════════════════════════════════════════════╝
""")


if __name__ == "__main__":
    main()
