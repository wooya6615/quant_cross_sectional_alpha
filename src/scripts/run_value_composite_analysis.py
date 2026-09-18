"""
Alpha_ValueComposite (PER+PBR+DivYield 단순 평균) IC + 백테스트
"""

from __future__ import annotations

import pandas as pd

from src.alpha.backtest import backtest_long_short, summarize_backtest
from src.alpha.evaluation import load_price_panel, run_ic_report
from src.alpha.value import HOLDING_PERIODS, compute_alpha_value_composite, load_fundamental_panel

LAG = 0

pd.set_option("display.float_format", lambda x: f"{x:.4f}")


def main() -> None:
    panel = load_fundamental_panel()
    price_wide = load_price_panel()
    composite = compute_alpha_value_composite(panel)

    print("=" * 60)
    print("Alpha_ValueComposite — IC 리포트")
    print("=" * 60)
    print(run_ic_report(composite, price_wide, LAG, HOLDING_PERIODS))
    
    rows = []
    for h in HOLDING_PERIODS:
        bt = backtest_long_short(
            composite, price_wide, holding_period=h, lag=LAG, direction=1, winsorize_pct=0.05
        )
        summary = summarize_backtest(bt, h)
        summary["holding_period"] = h
        rows.append(summary)
    
    print("\n" + "=" * 60)
    print("Alpha_ValueComposite — 백테스트 (거래비용+winsorize 5% 반영)")
    print("=" * 60)
    print(pd.DataFrame(rows).set_index("holding_period"))


if __name__ == "__main__":
    main()