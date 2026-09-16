"""
공매도 거래량/잔고 데이터 수집
"""

from __future__ import annotations

import pandas as pd
from dotenv import load_dotenv
load_dotenv()
from pykrx import stock
import time

import json
from pathlib import Path

CHUNK_DAYS = 600
SHORT_SELLING_BAN_START = "20231106"
SHORT_SELLING_BAN_END = "20250330"

PUBLICATION_LAG_DAYS = 1

REQUEST_DELAY_SECONDS = 0.3
MAX_RETRIES = 3

MAX_CONSECUTIVE_FAILURES = 5

PUBLICATION_LAG_DAYS = 1

class TooManyConsecutiveFailures(RuntimeError):
    """"""

def _chunk_date_ranges(start: str, end: str, chunk_days: int = CHUNK_DAYS) -> list[tuple[str, str]]:
    """start와 end의 문자열 구간을 chunk_days 단위 (start, end) 리스트로 쪼갬"""
    s = pd.to_datetime(start)
    e = pd.to_datetime(end)
    ranges = []
    cur = s
    while cur <= e:
        chunk_end = min(cur + pd.Timedelta(days=chunk_days - 1), e)
        ranges.append((cur.strftime("%Y%m%d"), chunk_end.strftime("%Y%m%d")))
        cur = chunk_end + pd.Timedelta(days=1)
    return ranges

def _fetch_one_chunk(ticker: str, s: str, e: str, fail_counter: list[int], failed_chunks: list[dict]) -> pd.DataFrame | None:
    """청크 하나를 재시도와 함께 가져옴"""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            df = stock.get_shorting_volume_by_date(s, e, ticker)
            fail_counter[0] = 0
            time.sleep(REQUEST_DELAY_SECONDS)
            return df
        except KeyError:
            time.sleep(REQUEST_DELAY_SECONDS * attempt)

    fail_counter[0] += 1
    failed_chunks.append({"ticker": ticker, "start": s, "end": e})
    print(
        f"[shorting] {ticker} {s}~{e}: 데이터 없음(KeyError, {MAX_RETRIES}회 재시도 후) "
        "— 빈 구간으로 처리"
    )
    if fail_counter[0] == MAX_CONSECUTIVE_FAILURES:
        print(
            f"[shorting] 경고: {fail_counter[0]}개 청크가 연속으로 실패 중. "
            "중단하지는 않지만, 계속 이러면 REQUEST_DELAY_SECONDS를 올리는 걸 고려할 것."
        )
    return None

def get_shorting_volume(
    ticker: str,
    start: str,
    end: str,
    fail_counter: list[int] | None = None,
    failed_chuncks: list[dict] | None = None,
    ) -> pd.DataFrame:
    """종목 하나의 공매도 거래량을 청킹해서 이어붙임"""
    if fail_counter is None:
        fail_counter = [0]
    if failed_chuncks is None:
        failed_chuncks = []
    chunks = []
    for s, e in _chunk_date_ranges(start, end):
        df = _fetch_one_chunk(ticker, s, e, fail_counter, failed_chuncks)
        if df is not None:
            chunks.append(df)
    if not chunks:
        return pd.DataFrame()
    return pd.concat(chunks).sort_index()

def flag_short_selling_ban(df: pd.DataFrame) -> pd.DataFrame:
    idx = pd.to_datetime(df.index)
    ban_start = pd.Timestamp(SHORT_SELLING_BAN_START)
    ban_end = pd.Timestamp(SHORT_SELLING_BAN_END)
    out = df.copy()
    out["in_ban_period"] = (idx >= ban_start) & (idx <= ban_end)
    return out

def build_short_ratio_panel(
    tickers: list[str],
    start: str,
    end: str,
    checkpoint_dir: str | Path | None = None,
    failed_chunks_path: str | Path | None = None,
    ) -> pd.DataFrame:
    """
    종목 리스트에 대해:
    1) 공매도 거래량 수집
    2) 공매도 자체가 없는 종목은 NaN + is_shortable=False 플래그
    를 거친 raw 패널을 반환
    """
    fail_counter = [0]
    failed_chunks: list[dict] = []
    empty_tickers: list[str] = []
    frames = []
    
    ckpt = Path(checkpoint_dir) if checkpoint_dir else None
    if ckpt:
        ckpt.mkdir(parents=True, exist_ok=True)
    
    for ticker in tickers:
        ticker_path = ckpt / f"{ticker}.parquet" if ckpt else None
        if ticker_path and ticker_path.exists():
            raw = pd.read_parquet(ticker_path)
        else:    
            raw = get_shorting_volume(ticker, start, end, fail_counter, failed_chunks)
            if ticker_path:
                raw.to_parquet(ticker_path)
        if raw.empty:
            empty_tickers.append(ticker)
        flagged = flag_short_selling_ban(raw)
        flagged["ticker"] = ticker
        flagged["is_shortable"] = flagged.drop(columns=["ticker"]).notna().any(axis=1)
        frames.append(flagged)
    
    if empty_tickers:
        print(
            f"[shorting] 데이터를 전혀 못 받은 종목 {len(empty_tickers)}개: "
            f"{empty_tickers[:20]}{' ...' if len(empty_tickers) > 20 else ''}"
        )
    if failed_chunks_path and failed_chunks:
        Path(failed_chunks_path).write_text(
            json.dumps(failed_chunks, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"[shorting] 실패한 청크 {len(failed_chunks)}개를 {failed_chunks_path}에 기록")

    return pd.concat(frames)


if __name__ == "__main__":
    # 스팟체크
    sample = get_shorting_volume("005930", "20240101", "20241231")
    print(sample.head())