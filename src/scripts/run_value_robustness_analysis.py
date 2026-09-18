"""
Alpha_PER / Alpha_PBR / Alpha_DivYield 국면(연도) robustness 리포트
"""

from __future__ import annotations

import pandas as pd

from src.alpha.evaluation import (
    compute_forward_returns,
    compute_quantile_long_short_return,
    load_price_panel,
    yearly_regime_report,
)
from src.alpha.value import (
    HOLDING_PERIODS,
    compute_alpha_div_yield,
    compute_alpha_per,
    compute_alpha_pbr,
    load_fundamental_panel,
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
    fundamental_panel = load_fundamental_panel()
    price_wide = load_price_panel()
    
    alphas = {
        "Alpha_PER": compute_alpha_per(fundamental_panel),
        "Alpha_PBR": compute_alpha_pbr(fundamental_panel),
        "Alpha_DivYield": compute_alpha_div_yield(fundamental_panel),
    }
    
    for name, alpha_wide in alphas.items():
        print("=" * 60)
        print(name)
        print("=" * 60)
        for h in HOLDING_PERIODS:
            _report_one(name, alpha_wide, price_wide, h)


if __name__ == "__main__":
    main()