"""
Alpha 평가: forward return 계산 + IC / Rank IC / ICIR
"""

from __future__ import annotations

import math
import pandas as pd

PRICE_PANEL_PATH = "data/raw/price_panel.parquet"
CLOSE_COL = "종가"
MIN_VALID_TICKERS = 30


def load_price_panel(path: str = PRICE_PANEL_PATH) -> pd.DataFrame:
    """raw 가격 패널을 읽어서 data * ticker 종가 wide 행렬로 반환함"""
    df = pd.read_parquet(path)
    df.index.name = "date"
    df = df.reset_index()
    df["date"] = pd.to_datetime(df["date"])
    return df.pivot(index="date", columns="ticker", values=CLOSE_COL)


def compute_forward_returns(
    price_wide: pd.DataFrame, lag: int, holding_period: int
) -> pd.DataFrame:
    """t행 = (t+lag+holding_period 시점 가격) / (t+lag 시점 가격) -1"""
    entry = price_wide.shift(-lag)
    exit_ = price_wide.shift(-(lag + holding_period))
    return exit_ / entry - 1


def compute_ic_series(
    alpha_wide: pd.DataFrame, forward_return_wide: pd.DataFrame, method: str
) -> pd.Series:
    """날짜별 cross-sectional correlation(alpha, forward_return)을 구함"""
    common_dates = alpha_wide.index.intersection(forward_return_wide.index)
    common_cols = alpha_wide.columns.intersection(forward_return_wide.columns)
    ics: dict[pd.Timestamp, float] = {}
    for date in common_dates:
        a = alpha_wide.loc[date, common_cols]
        r = forward_return_wide.loc[date, common_cols]
        valid = a.notna() & r.notna()
        if valid.sum() < MIN_VALID_TICKERS:
            continue
        ics[date] = a[valid].corr(r[valid], method=method)
    return pd.Series(ics).sort_index()


def summarize_ic(ic_series: pd.Series) -> dict:
    mean = ic_series.mean()
    std = ic_series.std()
    return {
        "ic_mean": mean,
        "ic_std": std,
        "icir": mean / std if std else float("nan"),
        "n_dates": len(ic_series),
    }


def run_ic_report(
    alpha_wide: pd.DataFrame,
    price_wide: pd.DataFrame,
    lag: int,
    holding_periods: list[int],
) -> pd.DataFrame:
    """holding_period별로 IC/Rank IC 요약을 표로 만듦"""
    rows = []
    for h in holding_periods:
        fwd = compute_forward_returns(price_wide, lag, h)
        ic = compute_ic_series(alpha_wide, fwd, method="pearson")
        rank_ic = compute_ic_series(alpha_wide, fwd, method="spearman")
        row = {"holding_period": h}
        row.update({f"ic_{k}": v for k, v in summarize_ic(ic).items()})
        row.update({f"rank_ic_{k}": v for k, v in summarize_ic(rank_ic).items() if k != "n_dates"})
        rows.append(row)
    return pd.DataFrame(rows).set_index("holding_period")


def compute_quantile_long_short_return(
    alpha_wide: pd.DataFrame,
    forward_return_wide: pd.DataFrame,
    holding_period: int,
    n_quantiles: int = 5,
) -> pd.Series:
    """상위/하위 분위 평균 forward_return의 차이를 날짜별로 구함"""
    common_dates = alpha_wide.index.intersection(forward_return_wide.index)
    sampled_dates = common_dates[::holding_period]
    ls_returns: dict[pd.Timestamp, float] = {}
    for date in sampled_dates:
        a = alpha_wide.loc[date]
        r = forward_return_wide.loc[date]
        valid = a.notna() & r.notna()
        if valid.sum() < MIN_VALID_TICKERS:
            continue
        aa, rr = a[valid], r[valid]
        top_cut = aa.quantile(1 - 1 / n_quantiles)
        bottom_cut = aa.quantile(1 / n_quantiles)
        top_ret = rr[aa >= top_cut].mean()
        bottom_ret = rr[aa <= bottom_cut].mean()
        ls_returns[date] = top_ret - bottom_ret
    return pd.Series(ls_returns).sort_index()


def yearly_regime_report(ls_return: pd.Series) -> tuple[pd.DataFrame, bool]:
    log_ret = (1 + ls_return).apply(lambda x: pd.NA if x <= 0 else x)
    log_ret = log_ret.dropna().astype(float).apply(math.log)
    by_year = log_ret.groupby(log_ret.index.year).sum()
    total = log_ret.sum()
    contribution = by_year / total if total != 0 else by_year * float("nan")
    table = pd.DataFrame({"log_return_sum": by_year, "contribution": contribution})
    regime_dependent = contribution.abs().max() > 0.5 if total != 0 else True
    return table, regime_dependent