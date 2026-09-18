"""
Value alpha 사전 검증
"""

from __future__ import annotations

from dotenv import load_dotenv
load_dotenv()

import pandas as pd
from pykrx import stock

from src.data.pykrx_utils import fetch_series

TICKER = "005930"
START = "20180101"
END = "20221231"

def _fetch(s:str, e: str, ticker: str) -> pd.DataFrame:
    return stock.get_market_fundamental(s, e, ticker)


def main() -> None:
    raw = fetch_series(_fetch, TICKER, START, END, label="fundamental")
    raw.index = pd.to_datetime(raw.index)
    raw = raw.sort_index()
    
    print(f"컬럼: {list(raw.columns)}")
    for col in ["EPS", "BPS"]:
        if col not in raw.columns:
            print(f"'{col}' 컬럼이 없음 — 실제 반환 컬럼명 확인 필요")
            continue
        changed = raw[col].diff().fillna(0) != 0
        change_dates = raw.index[changed]
        print(f"\n{col} 값이 바뀐 날짜들 ({len(change_dates)}번):")
        for d in change_dates:
            print(f"  {d.date()}  ->  {raw.loc[d, col]}")


if __name__ == "__main__":
    main()