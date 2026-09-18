"""
Alpha_Mom12_1 / Alpha_MomShort 거래비용 반영 백테스트 (winsorize 5% 기본 적용)
"""

from __future__ import annotations

import pandas as pd

from src.alpha.backtest import backtest_long_short, summarize_backtest
from src.alpha.evaluation import load_price_panel
from src.alpha.momentum import (
    MOM12_1_HOLDING_PERIODS,
    MOM_SHORT_HOLDING_PERIODS,
    compute_alpha_mom12_1,
    compute_alpha_mom_short,
)

LAG = 0
WINSORIZE_PCT = 0.05

pd.set_option("display.float_format", lambda x: f"{x:.4f}")


def _run(name: str, alpha_wide: pd.DataFrame, price_wide: pd.DataFrame, holding_periods: list[int]) -> None:
    rows = []
    for h in holding_periods:
        bt = backtest_long_short(
            alpha_wide, price_wide, holding_period=h, lag=LAG, direction=1,
            winsorize_pct=WINSORIZE_PCT,
        )
        summary = summarize_backtest(bt, h)
        summary["holding_period"] = h
        rows.append(summary)
    report = pd.DataFrame(rows).set_index("holding_period")
    print("=" * 60)
    print(f"{name} 백테스트 (거래비용 키움증권 온라인 기준 + winsorize {WINSORIZE_PCT:.0%} 반영)")
    print("=" * 60)
    print(report)


def main() -> None:
    price_wide = load_price_panel()

    mom12_1 = compute_alpha_mom12_1(price_wide)
    _run("Alpha_Mom12_1", mom12_1, price_wide, MOM12_1_HOLDING_PERIODS)

    mom_short = compute_alpha_mom_short(price_wide)
    _run("Alpha_MomShort", mom_short, price_wide, MOM_SHORT_HOLDING_PERIODS)


if __name__ == "__main__":
    main()