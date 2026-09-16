"""
Alpha_ShortLevel / Alpha_ShortCover 국면(연도) robustness 리포트
"""

from __future__ import annotations

import pandas as pd

from src.alpha.evaluation import (
    compute_forward_returns,
    compute_quantile_long_short_return,
    load_price_panel,
    yearly_regime_report,
)
from src.alpha.short_interest import (
    compute_all_short_cover,
    compute_alpha_short_level,
    load_balance_panel,
)
from src.data.shorting import PUBLICATION_LAG_DAYS

LEVEL_HOLDING_PERIODS = [5, 10, 20]
COVER_HOLDING_PERIODS = [1, 3, 5]

pd.set_option("display.float_format", lambda x: f"{x:.4f}")


def _report_one(name: str, alpha_wide: pd.DataFrame, price_wide: pd.DataFrame, h: int) -> None:
    fwd = compute_forward_returns(price_wide, PUBLICATION_LAG_DAYS, h)
    ls_return = compute_quantile_long_short_return(alpha_wide, fwd, holding_period=h)
    table, regime_dependent = yearly_regime_report(ls_return)
    print(f"\n--- {name}, holding={h} ---")
    print(table)
    verdict = "국면 의존적 (연도 기여도 50% 초과)" if regime_dependent else "국면 의존적이지 않음"
    print(f"판정: {verdict}")


def main() -> None:
    balance_panel = load_balance_panel()
    price_wide = load_price_panel()
    
    level_alpha = compute_alpha_short_level(balance_panel)
    print("=" * 60)
    print("Alpha_ShortLevel")
    print("=" * 60)
    for h in LEVEL_HOLDING_PERIODS:
        _report_one("Alpha_ShortLevel", level_alpha, price_wide, h)
    
    covers = compute_all_short_cover(balance_panel)
    for k, cover_alpha in covers.items():
        print("=" * 60)
        print(f"Alpha_ShortCover(K={k})")
        print("=" * 60)
        for h in COVER_HOLDING_PERIODS:
            _report_one(f"Alpha_ShortCover(K={k})", cover_alpha, price_wide, h)


if __name__ == "__main__":
    main()