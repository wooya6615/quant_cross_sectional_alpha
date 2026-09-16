"""
유니버스(KOSPI200 구성종목) 수집
"""
from __future__ import annotations

import pandas as pd
from dotenv import load_dotenv
load_dotenv()
from pykrx import stock

KOSPI200_TICKER = "1028"
RETRY_DELAY_SECONDS = 0.5
MAX_RETRIES = 3


def _is_empty_result(result) -> bool:
    if isinstance(result, pd.DataFrame):
        return result.empty
    return not result


def get_trading_days(start: str, end: str) -> list[str]:
    """start와 end 사이의 실제 KOSPI 거래일 리스트 (YYYYMMDD)"""
    df = stock.get_index_ohlcv_by_date(start, end, KOSPI200_TICKER)
    return [d.strftime("%Y%m%d") for d in df.index]


def get_rebalance_dates(start: str, end: str) -> list[str]:
    """매월 첫 영업일을 리밸런싱 시점으로 사용"""
    trading_days = get_trading_days(start, end)
    idx = pd.to_datetime(trading_days)
    s = pd.Series(idx, index=idx)
    first_of_month = s.groupby(idx.to_period("M")).min()
    return [d.strftime("%Y%m%d") for d in first_of_month]


def get_universe_at(date: str) -> list[str]:
    """date 시점 기준 KOSPI200 구성종목 티커 리스트
    리밸런싱 시점마다 이 함수를 다시 호출"""
    for attempt in range(1, MAX_RETRIES + 1):
        result = stock.get_index_portfolio_deposit_file(KOSPI200_TICKER, date)
        if not _is_empty_result(result):
            return list(result)
        time.sleep(RETRY_DELAY_SECONDS * attempt)
        
    raise ValueError(
        f"유니버스가 비어 있음 (date={date}), {MAX_RETRIES}회 재시도 후에도 실패. "
        "영업일 문자열인지, 인자 순서(ticker, date)가 맞는지 확인할 것."
    )


def build_universe_panel(start: str, end: str) -> pd.DataFrame:
    """리밸런싱 시점 * 종목 롱포맷 패널
    columns: rebal_date, ticker"""
    rows = []
    for d in get_rebalance_dates(start, end):
        for ticker in get_universe_at(d):
            rows.append({"rebal_date": d, "ticker": ticker})
    return pd.DataFrame(rows)

if __name__ == "__main__":
    # 스팟체크용
    panel = build_universe_panel("20150101", "20151231")
    print(panel.groupby("rebal_date")["ticker"].count())
