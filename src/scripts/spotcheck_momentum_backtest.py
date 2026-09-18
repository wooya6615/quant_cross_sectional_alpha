"""
Alpha_Mom12_1 / Alpha_MomShort 백테스트 결과 스팟체크 - 평균 vs 중앙값 롱숏 수익률 비교

Mom12_1의 IC(Pearson) > Rank IC(Spearman)로 나온 게(holding=120: 0.058 vs 0.026)
value_alpha_v1(Rank IC만 강하고 Pearson은 0 근처/음수)와 정반대 패턴이라 의심스러움
— 소수 극단치가 선형 상관을 끌어올리고 있을 가능성. quantile 평균 기준 백테스트가
왜곡될 수 있으므로 백테스트 돌리기 전에 먼저 확인.
"""

from __future__ import annotations

import pandas as pd

from src.alpha.evaluation import (
    compute_quantile_basket_mean_vs_median,
    compute_forward_returns,
    load_price_panel,
)
from src.alpha.momentum import (
    MOM12_1_HOLDING_PERIODS,
    MOM_SHORT_HOLDING_PERIODS,
    compute_alpha_mom12_1,
    compute_alpha_mom_short,
)

LAG = 0

pd.set_option("display.float_format", lambda x: f"{x:.4f}")


def _spotcheck(name: str, alpha_wide: pd.DataFrame, price_wide: pd.DataFrame, holding_periods: list[int]) -> None:
    for h in holding_periods:
        fwd = compute_forward_returns(price_wide, LAG, h)
        cmp = compute_quantile_basket_mean_vs_median(alpha_wide, fwd, holding_period=h)
        print(f"\n--- {name}, holding={h} ---")
        print(f"평균 기준 롱숏 누적: {cmp['ls_mean'].sum():.4f}")
        print(f"중앙값 기준 롱숏 누적: {cmp['ls_median'].sum():.4f}")
        print(f"두 값의 상관: {cmp['ls_mean'].corr(cmp['ls_median']):.4f}")


def main() -> None:
    price_wide = load_price_panel()

    mom12_1 = compute_alpha_mom12_1(price_wide)
    print("=" * 60)
    print("Alpha_Mom12_1")
    print("=" * 60)
    _spotcheck("Alpha_Mom12_1", mom12_1, price_wide, MOM12_1_HOLDING_PERIODS)

    mom_short = compute_alpha_mom_short(price_wide)
    print("\n" + "=" * 60)
    print("Alpha_MomShort")
    print("=" * 60)
    _spotcheck("Alpha_MomShort", mom_short, price_wide, MOM_SHORT_HOLDING_PERIODS)


if __name__ == "__main__":
    main()