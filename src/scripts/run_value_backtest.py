"""
Alpha_PER / Alpha_PBR / Alpha_DivYield 거래비용 반영 백테스트
"""

from __future__ import annotations

import pandas as pd

from src.alpha.backtest import backtest_long_short, summarize_backtest
from src.alpha.evaluation import load_price_panel
from src.alpha.value import (
    HOLDING_PERIODS,
    compute_alpha_div_yield,
    compute_alpha_pbr,
    compute_alpha_per,
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
        rows = []
        for h in HOLDING_PERIODS:
            bt = backtest_long_short(
                alpha_wide, price_wide, holding_period=h, lag=LAG, direction=1,
                winsorize_pct=0.05,
            )
            summary = summarize_backtest(bt, h)
            summary["holding_period"] = h
            rows.append(summary)
        report = pd.DataFrame(rows).set_index("holding_period")
        print("=" * 60)
        print(f"{name} 백테스트 (거래비용 키움증권 온라인 기준 반영)")
        print("=" * 60)
        print(report)


if __name__ == "__main__":
    main()
