"""
Alpha_PER / Alpha_PBR / Alpha_DivYield 계산
"""

from __future__ import annotations

import pandas as pd
import numpy as np

FUNDAMENTAL_PANEL_PATH = "data/raw/fundamental_panel.parquet"
HOLDING_PERIODS = [20, 60, 120]


def load_fundamental_panel(path: str = FUNDAMENTAL_PANEL_PATH) -> pd.DataFrame:
    """raw 밸류에이션 패널을 읽어서 date 컬럼을 datetime으로 정리"""
    df = pd.read_parquet(path)
    df.index.name = "date"
    df = df.reset_index()
    df["date"] = pd.to_datetime(df["date"])
    return df


def _wide(panel: pd.DataFrame, value_col: str) -> pd.DataFrame:
    """date * ticker wide 행렬"""
    return panel.pivot(index="date", columns="ticker", values=value_col)


def compute_alpha_per(panel: pd.DataFrame) -> pd.DataFrame:
    """Alpha_PER: cross-sectional rank(-PER) - PER 낮을수록(저평가) 랭크 높게"""
    wide = _wide(panel, "PER")
    return (-wide).rank(axis=1, pct=True)


def compute_alpha_pbr(panel: pd.DataFrame) -> pd.DataFrame:
    """Alpha_PBR: cross-sectional rank(-PBR) PBR 낮을수록(저평가) 랭크 높게"""
    wide = _wide(panel, "PBR")
    return (-wide).rank(axis=1, pct=True)


def compute_alpha_div_yield(panel: pd.DataFrame) -> pd.DataFrame:
    """Alpha_DivYield: cross-sectional rank(배당수익률) - 높을수록 랭크 높게"""
    wide = _wide(panel, "DIV")
    return wide.rank(axis=1, pct=True)


def compute_alpha_value_composite(panel: pd.DataFrame) -> pd.DataFrame:
    """Alpha_ValueComposite: PER/PBR/DivYield 세 alpha의 단순 평균"""
    per = compute_alpha_per(panel)
    pbr = compute_alpha_pbr(panel)
    div = compute_alpha_div_yield(panel)
    stacked = np.stack([per.values, pbr.values, div.values])
    combined = np.nanmean(stacked, axis=0)
    return pd.DataFrame(combined, index=per.index, columns=per.columns)


if __name__ == "__main__":
    # 스팟체크
    panel = load_fundamental_panel()
    for name, fn in [
        ("Alpha_PER", compute_alpha_per),
        ("Alpha_PBR", compute_alpha_pbr),
        ("Alpha_DivYield", compute_alpha_div_yield),
    ]:
        alpha = fn(panel)
        print(f"\n{name} 최근 날짜 분포:")
        print(alpha.iloc[-1].describe())