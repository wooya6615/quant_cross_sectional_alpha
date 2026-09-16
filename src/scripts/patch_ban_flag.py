"""
이미 받아놓은 short_interest_panel.parquet에 in_ban_period 플래그만
로컬에서 추가한다. KRX 재수집 없음 — 1회성 패치 스크립트.

실행: (repo root에서) python -m src.scripts.patch_ban_flag
"""

from __future__ import annotations

import pandas as pd

PANEL_PATH = "data/raw/short_interest_panel.parquet"
SHORT_SELLING_BAN_START = "20231106"
SHORT_SELLING_BAN_END = "20250330"


def main() -> None:
    panel = pd.read_parquet(PANEL_PATH)

    if "in_ban_period" in panel.columns:
        print("in_ban_period 컬럼이 이미 있음 — 패치를 다시 적용하지 않고 종료.")
        return

    idx = pd.to_datetime(panel.index)
    ban_start = pd.Timestamp(SHORT_SELLING_BAN_START)
    ban_end = pd.Timestamp(SHORT_SELLING_BAN_END)
    panel["in_ban_period"] = (idx >= ban_start) & (idx <= ban_end)

    ratio = panel["in_ban_period"].mean()
    print(f"in_ban_period=True 비율: {ratio:.1%} (전체 기간 대비 금지구간 비중)")

    panel.to_parquet(PANEL_PATH)
    print(f"패치 완료: {PANEL_PATH}")


if __name__ == "__main__":
    main()