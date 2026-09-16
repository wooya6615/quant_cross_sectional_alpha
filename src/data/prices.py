"""
종목별 OHLCV(수정주가) 수집
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from dotenv import load_dotenv
load_dotenv()
from pykrx import stock

from src.data.pykrx_utils import collect_with_checkpoint


def _fetch(s: str, e: str, ticker: str) -> pd.DataFrame:
    return stock.get_market_ohlcv(s, e, ticker)


def build_price_panel(
    tickers: list[str],
    start: str,
    end: str,
    checkpoint_dir: str | Path | None = None,
    failed_chunks_path: str | Path | None = None,
) -> pd.DataFrame:
    """종목별 OHLCV를 모아 하나의 롱포맷 패널로 합침"""
    raw_by_ticker, _ = collect_with_checkpoint(
        tickers,
        start,
        end,
        _fetch,
        label="price",
        checkpoint_dir=checkpoint_dir,
        failed_chunks_path=failed_chunks_path,
    )
    frames = []
    for ticker, raw in raw_by_ticker.items():
        df = raw.copy()
        df["ticker"] = ticker
        frames.append(df)
    return pd.concat(frames)


if __name__ == "__main__":
    # 스팟체크용
    sample = _fetch("20240101", "20241231", "005930")
    print(sample.head())