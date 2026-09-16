"""
Alpha_ShortLevel / Alpha_ShortCover(K=5/10/20) 전체 IC 리포트

Level holding period 후보: 5/10/20
Cover holding period 후보: 1/3/5
"""

from __future__ import annotations

import pandas as pd

from src.alpha.evaluation import load_price_panel, run_ic_report
from src.alpha.short_interest import (
    compute_all_short_cover,
    compute_alpha_short_level,
    load_balance_panel,
)
from src.data.shorting import PUBLICATION_LAG_DAYS

LEVEL_HOLDING_PERIODS = [5, 10, 20]
COVER_HOLDING_PERIODS = [1, 3, 5]

pd.set_option("display.float_format", lambda x: f"{x:.4f}")


def main() -> None:
    balance_panel = load_balance_panel()
    price_wide = load_price_panel()
    
    print("=" * 60)
    print("Alpha_ShortLevel")
    print("=" * 60)
    level_alpha = compute_alpha_short_level(balance_panel)
    level_report = run_ic_report(level_alpha, price_wide, PUBLICATION_LAG_DAYS, LEVEL_HOLDING_PERIODS)
    print(level_report)
    
    covers = compute_all_short_cover(balance_panel)
    for k, cover_alpha in covers.items():
        print("=" * 60)
        print(f"Alpha_ShortCover(K={k})")
        print("=" * 60)
        cover_report = run_ic_report(
            cover_alpha, price_wide, PUBLICATION_LAG_DAYS, COVER_HOLDING_PERIODS
        )
        print(cover_report)


if __name__ == "__main__":
    main()
