"""
Alpha_Mom12_1 / Alpha_MomShort 계산 (cross-sectional 정규화)
"""

from __future__ import annotations

import pandas as pd

FORMATION_LONG = 240  # 약 12개월(영업일 기준)
EXCLUDE_RECENT = 20  # 최근 1개월 제외
FORMATION_SHORT = 20  # MomShort formation window(1개월)

MOM12_1_HOLDING_PERIODS = [20, 60, 120]
MOM_SHORT_HOLDING_PERIODS = [5, 10, 20]


def compute_alpha_mom12_1(price_wide: pd.DataFrame) -> pd.DataFrame:
    """Alpha_Mom12_1: cross-sectional rank(t-20 ~ t-240 구간 수익률)
    최근 1개월은 formation에서 제외 — 표준 12-1 모멘텀 컨벤션"""
    formation_ret = price_wide.shift(EXCLUDE_RECENT) / price_wide.shift(FORMATION_LONG) - 1
    return formation_ret.rank(axis=1, pct=True)


def compute_alpha_mom_short(price_wide: pd.DataFrame) -> pd.DataFrame:
    """Alpha_MomShort: cross-sectional rank(-최근 1개월 수익률)
    단기 반전 가정 — 최근 급락 종목의 랭크를 높게"""
    formation_ret = price_wide / price_wide.shift(FORMATION_SHORT) - 1
    return (-formation_ret).rank(axis=1, pct=True)


if __name__ == "__main__":
    # 스팟체크용
    from src.alpha.evaluation import load_price_panel

    price_wide = load_price_panel()
    for name, fn in [
        ("Alpha_Mom12_1", compute_alpha_mom12_1),
        ("Alpha_MomShort", compute_alpha_mom_short),
    ]:
        alpha = fn(price_wide)
        print(f"\n{name} 최근 날짜 분포:")
        print(alpha.iloc[-1].describe())