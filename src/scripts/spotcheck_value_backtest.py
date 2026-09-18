"""
Alpha_DivYield 백테스트 결과 스팟체크 - 평균 vs 중앙값 롱숏 수익률 비교
"""

from __future__ import annotations

import pandas as pd

from src.alpha.evaluation import (
    compute_quantile_basket_mean_vs_median,
    compute_forward_returns,
    load_price_panel,
)
from src.alpha.value import compute_alpha_div_yield, load_fundamental_panel

LAG = 0
HOLDING_PERIODS = [20, 60, 120]

pd.set_option("display.float_format", lambda x: f"{x:.4f}")


def main() -> None:
    fundamental_panel = load_fundamental_panel()
    price_wide = load_price_panel()
    alpha_wide = compute_alpha_div_yield(fundamental_panel)

    for h in HOLDING_PERIODS:
        fwd = compute_forward_returns(price_wide, LAG, h)
        cmp = compute_quantile_basket_mean_vs_median(alpha_wide, fwd, holding_period=h)
        print(f"\n--- Alpha_DivYield, holding={h} ---")
        print(f"평균 기준 롱숏 누적: {cmp['ls_mean'].sum():.4f}")
        print(f"중앙값 기준 롱숏 누적: {cmp['ls_median'].sum():.4f}")
        print(f"두 값의 상관: {cmp['ls_mean'].corr(cmp['ls_median']):.4f}")


if __name__ == "__main__":
    main()