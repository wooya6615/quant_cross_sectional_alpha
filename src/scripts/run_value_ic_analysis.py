"""
Alpha_PER / Alpha_PBR / Alpha_DivYield 전체 IC 리포트
"""

from __future__ import annotations

import pandas as pd

from src.alpha.evaluation import load_price_panel, run_ic_report
from src.alpha.value import (
    HOLDING_PERIODS,
    compute_alpha_div_yield,
    compute_alpha_per,
    compute_alpha_pbr,
    load_fundamental_panel,
)

LAG = 0

pd.set_option("display.float_format", lambda x: f"{x:.4f}")


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
        report = run_ic_report(alpha_wide, price_wide, LAG, HOLDING_PERIODS)
        print(report)


if __name__ == "__main__":
    main()