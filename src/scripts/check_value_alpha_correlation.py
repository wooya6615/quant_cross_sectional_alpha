"""
Alpha_PER / Alpha_PBR / Alpha_DivYield 간 상관관계
"""

from __future__ import annotations

import pandas as pd

from src.alpha.value import (
    compute_alpha_div_yield,
    compute_alpha_pbr,
    compute_alpha_per,
    load_fundamental_panel,
)

def main() -> None:
    panel = load_fundamental_panel()
    alphas = {
        "PER": compute_alpha_per(panel),
        "PBR": compute_alpha_pbr(panel),
        "DivYield": compute_alpha_div_yield(panel),
    }
    
    stacked = pd.DataFrame({name: a.stack() for name, a in alphas.items()})
    corr = stacked.corr()
    print("Alpha 간 상관계수 (rank 값 기준, 공통 (날짜,종목) 쌍):")
    print(corr)
    print(f"\n유효 관측치 수: {len(stacked.dropna())}")


if __name__ == "__main__":
    main()