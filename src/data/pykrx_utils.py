from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Callable

import pandas as pd

CHUNK_DAYS = 600
REQUEST_DELAY_SECONDS = 0.3
MAX_RETRIES = 3
CONSECUTIVE_FAILURE_WARNING_THRESHOLD = 5


def chunk_date_ranges(start: str, end: str, chunk_days: int = CHUNK_DAYS) -> list[tuple[str, str]]:
    """(start, end) 문자열 구간을 chunk_days 단위 리스트로 쪼갬"""
    s = pd.to_datetime(start)
    e = pd.to_datetime(end)
    ranges = []
    cur = s
    while cur < e:
        chunk_end = min(cur + pd.Timedelta(days=chunk_days - 1), e)
        ranges.append((cur.strftime("%Y%m%d"), chunk_end.strftime("%Y%m%d")))
        cur = chunk_end + pd.Timedelta(days=1)
    return ranges


def _fetch_one_chunk(
    fetch_fn: Callable[[str, str, str], pd.DataFrame],
    ticker: str,
    s: str,
    e: str,
    fail_counter: list[int],
    failed_chunks: list[dict],
    label: str,
) -> pd.DataFrame | None:
    "청크 하나를 재시도와 함께 가져온다"
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            df = fetch_fn(s, e, ticker)
            fail_counter[0] = 0
            time.sleep(REQUEST_DELAY_SECONDS)
            return df
        except KeyError:
            time.sleep(REQUEST_DELAY_SECONDS * attempt)
    
    fail_counter[0] += 1
    failed_chunks.append({"source": label, "ticker": ticker, "start": s, "end": e})
    print(
        f"[{label}] {ticker} {s}~{e}: 데이터 없음(KeyError, {MAX_RETRIES}회 재시도 후) "
        "— 빈 구간으로 처리"
    )
    if fail_counter[0] == CONSECUTIVE_FAILURE_WARNING_THRESHOLD:
        print(
            f"[{label}] 경고: {fail_counter[0]}개 청크가 연속으로 실패 중. "
            "중단하지는 않지만, 계속 이러면 REQUEST_DELAY_SECONDS를 올리는 걸 고려할 것."
        )
    return None


def fetch_series(
    fetch_fn: Callable[[str, str, str], pd.DataFrame],
    ticker: str,
    start: str,
    end: str,
    label: str,
    fail_counter: list[int] | None = None,
    failed_chunks: list[dict] | None = None,
) -> pd.DataFrame:
    """종목 하나에 대해 기간을 청킹해서 fetch_fn을 반복 호출하고 이어붙임"""
    if fail_counter is None:
        fail_counter = [0]
    if failed_chunks is None:
        failed_chunks = []
    chunks = []
    for s, e in chunk_date_ranges(start, end):
        df = _fetch_one_chunk(fetch_fn, ticker, s, e, fail_counter, failed_chunks, label)
        if df is not None:
            chunks.append(df)
    if not chunks:
        return pd.DataFrame()
    return pd.concat(chunks).sort_index()


def collect_with_checkpoint(
    tickers: list[str],
    start: str,
    end: str,
    fetch_fn: Callable[[str, str, str], pd.DataFrame],
    label: str,
    checkpoint_dir: str | Path | None = None,
    failed_chunks_path: str | Path | None = None,
) -> tuple[dict[str, pd.DataFrame], list[str]]:
    """종목별 raw 데이터를 {ticker: df} 딕셔너리로 모음"""
    fail_counter = [0]
    failed_chunks: list[dict] = []
    empty_tickers: list[str] = []
    result: dict[str, pd.DataFrame] = {}

    ckpt = Path(checkpoint_dir) if checkpoint_dir else None
    if ckpt:
        ckpt.mkdir(parents=True, exist_ok=True)

    for ticker in tickers:
        ticker_path = ckpt / f"{ticker}.parquet" if ckpt else None
        if ticker_path and ticker_path.exists():
            raw = pd.read_parquet(ticker_path)
        else:
            raw = fetch_series(fetch_fn, ticker, start, end, label, fail_counter, failed_chunks)
            if ticker_path:
                raw.to_parquet(ticker_path)
        if raw.empty:
            empty_tickers.append(ticker)
        result[ticker] = raw
    
    if empty_tickers:
        print(
            f"[{label}] 데이터를 전혀 못 받은 종목 {len(empty_tickers)}개: "
            f"{empty_tickers[:20]}{' ...' if len(empty_tickers) > 20 else ''}"
        )
    if failed_chunks_path and failed_chunks:
        path = Path(failed_chunks_path)
        existing = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
        existing.extend(failed_chunks)
        path.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[{label}] 실패한 청크 {len(failed_chunks)}개를 {failed_chunks_path}에 추가 기록")
    
    return result, empty_tickers