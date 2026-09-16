"""
Alpha_ShortLevel 거래비용 반영 백테스트
"""

from __future__ import annotations

import pandas as pd

from src.alpha.backtest import backtest_long_short, summarize_backtest
from src.alpha.evaluation import load_price_panel
from src.alpha.short_interest import compute_alpha_short_level, load_balance_panel
from src.data.shorting import PUBLICATION_LAG_DAYS

LEVEL_HOLDING_PERIODS = [5, 10, 20]

pd.set_option("display.float_format", lambda x: f"{x:.4f}")


def main() -> None:
    balance_panel = load_balance_panel()
    price_wide = load_price_panel()
    level_alpha = compute_alpha_short_level(balance_panel)

    rows = []
    for h in LEVEL_HOLDING_PERIODS:
        bt = backtest_long_short(
            level_alpha, price_wide, holding_period=h, lag=PUBLICATION_LAG_DAYS,
            direction=-1
        )
        summary = summarize_backtest(bt, h)
        summary["holding_period"] = h
        rows.append(summary)
    
    report = pd.DataFrame(rows).set_index("holding_period")
    print("=" * 60)
    print("Alpha_ShortLevel 백테스트 (거래비용 편도 30bp 반영)")
    print("=" * 60)
    print(report)


if __name__ == "__main__":
    main()