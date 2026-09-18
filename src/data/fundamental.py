"""
밸류에이션 지표(PER/PBR/EPS/BPS/DIV/DPS) 수집
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from pykrx import stock

from src.data.pykrx_utils import collect_with_checkpoint


def _fetch(s: str, e: str, ticker: str) -> pd.DataFrame:
    return stock.get_market_fundamental(s, e, ticker)


def build_fundamental_panel(
    tickers: list[str],
    start: str,
    end: str,
    checkpoint_dir: str | Path | None = None,
    failed_chunks_path: str | Path | None = None,
) -> pd.DataFrame:
    """종목별 밸류에이션 지표를 모아 하나의 롱포맷 패널로 합침"""
    raw_by_ticker, _ = collect_with_checkpoint(
        tickers,
        start,
        end,
        _fetch,
        label="fundamental",
        checkpoint_dir=checkpoint_dir,
        failed_chunks_path=failed_chunks_path,
    )
    frames = []
    for ticker, raw in raw_by_ticker.items():
        df = raw.copy()
        df["is_available"] = df.notna().any(axis=1) if not df.empty else df.index.to_series().astype(bool)
        
        if "PER" in df.columns:
            df["is_loss"] = df["PER"] <= 0
            df.loc[df["is_loss"], "PER"] = pd.NA
        if "PBR" in df.columns:
            df["is_negative_book"] = df["PBR"] < 0
            df.loc[df["is_negative_book"], "PBR"] = pd.NA
        
        df["ticker"] = ticker
        frames.append(df)
    return pd.concat(frames)


if __name__ == "__main__":
    # 스팟체크
    sample = _fetch("20240101", "20241231", "005930")
    print(sample.head())