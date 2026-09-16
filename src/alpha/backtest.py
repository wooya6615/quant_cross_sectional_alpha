"""
거래비용 반영 롱숏 백테스트
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.alpha.evaluation import MIN_VALID_TICKERS, compute_forward_returns

COST_BUY_BP = 1.5
COST_SELL_BP = 21.5
SLIPPAGE_BP_ONEWAY = 5
COST_PER_UNIT_TURNOVER_BP = (COST_BUY_BP + SLIPPAGE_BP_ONEWAY) + (COST_SELL_BP + SLIPPAGE_BP_ONEWAY)
TRADING_DAYS_PER_YEAR = 252


def _quantile_backtests(alpha_row: pd.Series, n_quantiles: int) -> tuple[set, set]:
    valid = alpha_row.dropna()
    top_cut = valid.quantile(1 - 1 / n_quantiles)
    bottom_cut = valid.quantile(1 / n_quantiles)
    long_basket = set(valid[valid >= top_cut].index)
    short_basket = set(valid[valid <= bottom_cut].index)
    return long_basket, short_basket


def backtest_long_short(
    alpha_wide: pd.DataFrame,
    price_wide: pd.DataFrame,
    holding_period: int,
    lag: int,
    n_quantiles: int = 5,
    cost_bps_oneway: float = COST_PER_UNIT_TURNOVER_BP,
    direction: int = 1,
) -> pd.DataFrame:
    """리밸런싱 시점별 gross/net 수익률과 turnover를 담은 DataFrame을 반환"""
    fwd = compute_forward_returns(price_wide, lag, holding_period)
    common_dates = alpha_wide.index.intersection(fwd.index)
    sampled_dates = common_dates[::holding_period]

    records = []
    prev_long: set = set()
    prev_short: set = set()
    for date in sampled_dates:
        a = alpha_wide.loc[date]
        r = fwd.loc[date]
        valid = a.notna() & r.notna()
        if valid.sum() < MIN_VALID_TICKERS:
            continue
        aa, rr = a[valid], r[valid]
        top_basket, bottom_basket = _quantile_backtests(aa, n_quantiles)
        if direction == 1:
            long_basket, short_basket = top_basket, bottom_basket
        else:
            long_basket, short_basket = bottom_basket, top_basket
        long_ret = rr[list(long_basket)].mean()
        short_ret = rr[list(short_basket)].mean()
        gross = long_ret - short_ret
        
        if prev_long or prev_short:
            long_turnover = 1 - len(long_basket & prev_long) / len(long_basket) if long_basket else 0.0
            short_turnover = 1 - len(short_basket & prev_short) / len(short_basket) if short_basket else 0.0
            turnover = (long_turnover + short_turnover) / 2
        else:
            turnover = 1.0
        
        cost = turnover * (cost_bps_oneway / 10000) * 2
        net = gross - cost
        
        records.append(
            {"date":date, "gross_return": gross, "turnover": turnover, "cost": cost, "net_return": net}
        )
        prev_long, prev_short = long_basket, short_basket
    
    return pd.DataFrame(records).set_index("date")


def summarize_backtest(bt: pd.DataFrame, holding_period: int) -> dict:
    """Sharpe/MDD/Calmar/Turnover 등 요약 통계"""
    ann_factor = TRADING_DAYS_PER_YEAR / holding_period
    net = bt["net_return"]
    log_net = np.log1p(net.clip(lower=-0.999))
    ann_return = np.expm1(log_net.mean() * ann_factor)
    ann_vol = net.std() * np.sqrt(ann_factor)
    sharpe = ann_return / ann_vol if ann_vol else float("nan")

    equity = (1 + net).cumprod()
    running_max = equity.cummax()
    drawdown = equity / running_max - 1
    mdd = drawdown.min()
    calmar = ann_return / abs(mdd) if mdd else float("nan")
    
    avg_turnover = bt["turnover"].mean()
    return {
        "ann_return": ann_return,
        "ann_vol": ann_vol,
        "sharpe": sharpe,
        "mdd": mdd,
        "calmar": calmar,
        "avg_turnover": avg_turnover,
        "ann_turnover": avg_turnover * ann_factor,
        "n_periods": len(net),
    }