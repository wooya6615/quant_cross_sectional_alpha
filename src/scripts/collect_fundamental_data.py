"""
밸류에이션(PER/PBR/DIV) raw 데이터 수집 오케스트레이션
"""

from __future__ import annotations

from dotenv import load_dotenv
load_dotenv()

from src.data.fundamental import build_fundamental_panel
from src.data.universe import build_universe_panel

START = "20150101"
END = "20251231"
OUT_PATH = "data/raw/fundamental_panel.parquet"
CHECKPOINT_DIR = "data/raw/fundamental_by_ticker"
FAILED_CHUNKS_PATH = "data/raw/failed_chunks.json"


def main() -> None:
    universe_panel = build_universe_panel(START, END)
    tickers = sorted(universe_panel["ticker"].unique())
    print(f"유니버스 종목 수: {len(tickers)}")
    
    panel = build_fundamental_panel(
        tickers,
        START,
        END,
        checkpoint_dir=CHECKPOINT_DIR,
        failed_chunks_path=FAILED_CHUNKS_PATH,
    )
    panel.to_parquet(OUT_PATH)
    print(f"저장 완료: {OUT_PATH}")
    
    collected = set(panel["ticker"].unique())
    missing = sorted(set(tickers) - collected)
    coverage = len(collected) / len(tickers) if tickers else 0.0
    print(f"유니버스 대비 실제 수집 커버리지: {coverage:.1%} ({len(collected)}/{len(tickers)})")
    if missing:
        print(f"데이터 전혀 없는 종목 {len(missing)}개 (앞 20개만): {missing[:20]}")
 
    print(f"적자(is_loss) 비율: {panel['is_loss'].mean():.1%}")
    print(f"자본잠식(is_negative_book) 비율: {panel['is_negative_book'].mean():.1%}")


if __name__ == "__main__":
    main()