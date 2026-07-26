"""
metrics.py
============================================================
Stylized fact metrics for the agent-based market simulation.

Computes, from a single run's MARKET_STATE_DATA.csv:
  1. Fat tails               -> excess kurtosis of log returns
  2. Volatility clustering   -> mean autocorrelation of |returns|
  3. Volume-volatility corr  -> Spearman correlation of volume vs volatility

All three are computed AFTER dropping the burn-in period, since
early-simulation dynamics are not representative of steady-state
behavior.

This is intentionally a "black box" utility module: you call
compute_all_stylized_facts(csv_path) and get back a dict of scalars.
You don't need to touch the internals to use it in your analysis.
============================================================
"""

import numpy as np
import pandas as pd
from scipy.stats import kurtosis, spearmanr


def load_market_state(csv_path, burn_in=50):
    """
    Loads MARKET_STATE_DATA.csv and drops the burn-in period.
    Assumes a 'price' column and a 'time' column exist.
    Adjust the volume column name below if yours differs
    (see the note in experiment_runner.py about total_volume).
    """
    df = pd.read_csv(csv_path)
    df = df.sort_values("time").reset_index(drop=True)
    df = df[df["time"] >= burn_in].reset_index(drop=True)
    return df


def compute_log_returns(price_series):
    prices = np.asarray(price_series, dtype=float)
    prices = np.clip(prices, 1e-8, None)  # guard against zero/negative price edge cases
    log_returns = np.diff(np.log(prices))
    return log_returns


def fat_tails(log_returns):
    """
    Excess kurtosis (Fisher definition: normal distribution -> 0).
    Positive values indicate fatter-than-normal tails, which is the
    stylized fact we expect real markets (and hopefully this sim) to show.
    """
    if len(log_returns) < 4:
        return np.nan
    return float(kurtosis(log_returns, fisher=True, bias=False))


def volatility_clustering(log_returns, max_lag=20):
    """
    Mean autocorrelation of |returns| across lags 1..max_lag.
    Volatility clustering shows up as persistent positive autocorrelation
    in absolute (or squared) returns, even when raw returns are
    close to uncorrelated (near-random-walk prices).

    Returns the average autocorrelation across the lag range as a
    single summary scalar. If you want the full lag profile for a
    plot, use volatility_clustering_profile() instead.
    """
    abs_returns = np.abs(log_returns)
    n = len(abs_returns)
    if n < max_lag + 5:
        return np.nan

    series = pd.Series(abs_returns)
    acorrs = [series.autocorr(lag=l) for l in range(1, max_lag + 1)]
    acorrs = [a for a in acorrs if a is not None and not np.isnan(a)]
    if not acorrs:
        return np.nan
    return float(np.mean(acorrs))


def volatility_clustering_profile(log_returns, max_lag=20):
    """Full per-lag autocorrelation profile of |returns|, useful for a plot."""
    abs_returns = np.abs(log_returns)
    series = pd.Series(abs_returns)
    return {l: series.autocorr(lag=l) for l in range(1, max_lag + 1)}


def volume_volatility_correlation(volume_series, log_returns):
    """
    Spearman correlation between per-step traded volume and per-step
    absolute return (a standard realized-volatility proxy at daily
    resolution). Spearman is used rather than Pearson to stay robust
    to the heavy tails already captured by fat_tails().

    volume_series must be aligned to the SAME steps as log_returns,
    i.e. len(volume_series) == len(log_returns) + 1 (prices) is trimmed
    to match returns internally.
    """
    volume = np.asarray(volume_series, dtype=float)
    abs_returns = np.abs(log_returns)

    # log_returns has one fewer element than price/volume (diff),
    # so align volume to the SECOND element of each return-pair.
    volume_aligned = volume[1:len(abs_returns) + 1]

    if len(volume_aligned) != len(abs_returns):
        n = min(len(volume_aligned), len(abs_returns))
        volume_aligned = volume_aligned[:n]
        abs_returns = abs_returns[:n]

    if len(abs_returns) < 4:
        return np.nan

    corr, _ = spearmanr(volume_aligned, abs_returns)
    return float(corr)


def compute_all_stylized_facts(csv_path, burn_in=50, max_lag=20, volume_col="total_volume"):
    """
    Main entry point. Returns:
        {
          "fat_tails": float,
          "volatility_clustering": float,
          "volume_volatility_correlation": float,
          "n_observations": int,
        }

    Requires MARKET_STATE_DATA.csv to have a 'price' column and,
    for the third metric, a volume column (see experiment_runner.py
    for how to add total_volume to your simulator output — it isn't
    currently logged and needs one small addition to simulator.py).
    """
    df = load_market_state(csv_path, burn_in=burn_in)
    log_returns = compute_log_returns(df["price"])

    result = {
        "fat_tails": fat_tails(log_returns),
        "volatility_clustering": volatility_clustering(log_returns, max_lag=max_lag),
        "n_observations": len(log_returns),
    }

    if volume_col in df.columns:
        result["volume_volatility_correlation"] = volume_volatility_correlation(
            df[volume_col], log_returns
        )
    else:
        result["volume_volatility_correlation"] = np.nan
        result["_warning"] = (
            f"Column '{volume_col}' not found in {csv_path} — "
            "volume-volatility correlation skipped. "
            "Add total_volume logging to simulator.py (see experiment_runner.py notes)."
        )

    return result


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python metrics.py <path_to_MARKET_STATE_DATA.csv>")
        sys.exit(1)
    facts = compute_all_stylized_facts(sys.argv[1])
    for k, v in facts.items():
        print(f"{k}: {v}")
