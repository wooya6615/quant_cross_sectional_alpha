"""
Alpha_Mom12_1 / Alpha_MomShort IC 리포트
"""

from __future__ import annotations

import pandas as pd

from src.alpha.evaluation import load_price_panel, run_ic_report
from src.alpha.momentum import (
    MOM12_1_HOLDING_PERIODS,
    MOM_SHORT_HOLDING_PERIODS,
    compute_alpha_mom12_1,
    compute_alpha_mom_short,
)

LAG = 0

pd.set_option("display.float_format", lambda x: f"{x:.4f}")


def main() -> None:
    price_wide = load_price_panel()

    print("=" * 60)
    print("Alpha_Mom12_1")
    print("=" * 60)
    mom12_1 = compute_alpha_mom12_1(price_wide)
    print(run_ic_report(mom12_1, price_wide, LAG, MOM12_1_HOLDING_PERIODS))

    print("\n" + "=" * 60)
    print("Alpha_MomShort")
    print("=" * 60)
    mom_short = compute_alpha_mom_short(price_wide)
    print(run_ic_report(mom_short, price_wide, LAG, MOM_SHORT_HOLDING_PERIODS))


if __name__ == "__main__":
    main()