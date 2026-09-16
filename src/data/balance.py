"""공매도 잔고 데이터 수집"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
load_dotenv()
from pykrx import stock

from src.data.pykrx_utils import collect_with_checkpoint
from src.data.shorting import flag_short_selling_ban


def _fetch(s: str, e: str, ticker: str) -> pd.DataFrame:
    return stock.get_shorting_balance_by_date(s, e, ticker)


def build_balance_panel(
    tickers: list[str],
    start: str,
    end: str,
    checkpoint_dir: str | Path | None = None,
    failed_chunks_path: str | Path | None = None,
) -> pd.DataFrame:
    """종목별 공매도 잔고를 모아 하나의 롱포맷 패널로 합침"""
    raw_by_ticker, _ = collect_with_checkpoint(
        tickers,
        start,
        end,
        _fetch,
        label="shorting_balance",
        checkpoint_dir=checkpoint_dir,
        failed_chunks_path=failed_chunks_path,
    )
    frames = []
    for ticker, raw in raw_by_ticker.items():
        flagged = flag_short_selling_ban(raw)
        flagged["ticker"] = ticker
        flagged["is_shortable"] = (
            flagged.drop(columns=["ticker", "in_ban_period"]).notna().any(axis=1)
        )
        frames.append(flagged)
    return pd.concat(frames)


if __name__ == "__main__":
    sample = _fetch("20240101", "20241231", "005939")
    print(sample.head())