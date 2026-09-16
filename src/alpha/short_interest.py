"""
Alpha_ShortLevel / Alpha_ShortCover 계산 (cross-sectional 정규화)
"""
from __future__ import annotations

import pandas as pd

from src.data.shorting import SHORT_SELLING_BAN_END, SHORT_SELLING_BAN_START

BALANCE_PANEL_PATH = "data/raw/short_balance_panel.parquet"
VALUE_COL = "비중"
COVER_K_CANDIDATES = [5, 10, 20]


def load_balance_panel(path: str = BALANCE_PANEL_PATH) -> pd.DataFrame:
    """raw 잔고 패널을 읽어서 data 컬럼을 datetime으로 정리함"""
    df = pd.read_parquet(path)
    df.index.name = "date"
    df = df.reset_index()
    df["date"] = pd.to_datetime(df["date"])
    return df


def _wide(panel: pd.DataFrame, value_col: str = VALUE_COL) -> pd.DataFrame:
    """date * ticker wide 행렬"""
    masked = panel.copy()
    masked[value_col] = masked[value_col].where(masked["is_shortable"])
    return masked.pivot(index="date", columns="ticker", values=value_col)


def _cover_window_crosses_ban(dates: pd.DataFrameIndex, k: int) -> pd.Series:
    ban_start = pd.Timestamp(SHORT_SELLING_BAN_START)
    ban_end = pd.Timestamp(SHORT_SELLING_BAN_END)
    n = len(dates)
    crosses = pd.Series(False, index=dates)
    for i in range(k, n):
        window_start, window_end = dates[i - k], dates[i]
        if window_start <= ban_start <= window_end or window_start <= ban_end <= window_end:
            crosses.iloc[i] = True
    return crosses


def compute_alpha_short_level(panel: pd.DataFrame) -> pd.DataFrame:
    """Alpha_ShortLevel: cross-sectional rank(공매도잔고비율)"""
    wide = _wide(panel)
    return wide.rank(axis=1, pct=True)


def compute_alpha_short_cover(panel: pd.DataFrame, k: int) -> pd.DataFrame:
    """Alpha_ShortCover(K): -d(비중, K거래일)을 구한 뒤 cross-sectional rank"""
    wide = _wide(panel)
    delta = wide.diff(k)
    crosses = _cover_window_crosses_ban(wide.index, k)
    delta.loc[crosses, :] = pd.NA
    raw_cover = -delta
    return raw_cover.rank(axis=1, pct=True)


def compute_all_short_cover(panel: pd.DataFrame) -> dict[int, pd.DataFrame]:
    """K 후보 전부 계산해서 {K: alpha_df} 딕셔너리로 반환"""
    return {k: compute_alpha_short_cover(panel, k) for k in COVER_K_CANDIDATES}


if __name__ == "__main__":
    # 스팟 체크용
    panel = load_balance_panel()
    level = compute_alpha_short_level(panel)
    print("Alpha_ShortLevel 최근 날짜 분포:")
    print(level.iloc[-1].describe())
    
    covers = compute_all_short_cover(panel)
    for k, cover in covers.items():
        print(f"\nAlpha_ShortCover(K={k}) 최근 날짜 분포:")
        print(cover.iloc[-1].describe())