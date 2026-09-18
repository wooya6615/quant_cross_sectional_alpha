"""
Alpha_Mom12_1 / Alpha_MomShort 국면(연도) robustness 리포트
"""

from __future__ import annotations

import pandas as pd

from src.alpha.evaluation import (
    compute_forward_returns,
    compute_quantile_long_short_return,
    load_price_panel,
    yearly_regime_report,
)
from src.alpha.momentum import (
    MOM12_1_HOLDING_PERIODS,
    MOM_SHORT_HOLDING_PERIODS,
    compute_alpha_mom12_1,
    compute_alpha_mom_short,
)

LAG = 0

pd.set_option("display.float_format", lambda x: f"{x:.4f}")


def _report_one(name: str, alpha_wide: pd.DataFrame, price_wide: pd.DataFrame, h: int) -> None:
    fwd = compute_forward_returns(price_wide, LAG, h)
    ls_return = compute_quantile_long_short_return(alpha_wide, fwd, holding_period=h)
    table, verdict = yearly_regime_report(ls_return)
    print(f"\n--- {name}, holding={h} ---")
    print(table)
    print(f"판정: {verdict}")


def main() -> None:
    price_wide = load_price_panel()

    mom12_1 = compute_alpha_mom12_1(price_wide)
    print("=" * 60)
    print("Alpha_Mom12_1")
    print("=" * 60)
    for h in MOM12_1_HOLDING_PERIODS:
        _report_one("Alpha_Mom12_1", mom12_1, price_wide, h)

    mom_short = compute_alpha_mom_short(price_wide)
    print("\n" + "=" * 60)
    print("Alpha_MomShort")
    print("=" * 60)
    for h in MOM_SHORT_HOLDING_PERIODS:
        _report_one("Alpha_MomShort", mom_short, price_wide, h)


if __name__ == "__main__":
    main()