"""
experiment_runner.py
============================================================
Runs the full 36-configuration study (1 Baseline + 25 OFAT + 10
Archetype configs), computes stylized fact metrics on each, and
runs the Spearman sensitivity analysis on the OFAT sweeps.

REQUIRES: the simulator.py changes described in chat — a
run_market_simulation(agent_counts, seed, output_dir) signature,
PRICE_HISTORY.clear() at the top of each run, and total_volume
logging. Without those, this script can't run isolated per-config
simulations and volume-volatility correlation will be NaN.

Usage:
    python experiment_runner.py

Output:
    data/experiments/<config_id>/...            <- per-run raw CSVs
    data/experiments/manifest.csv                <- one row per run (with design metadata)
    data/experiments/summary_metrics.csv         <- manifest + stylized fact metrics
    data/experiments/sensitivity_analysis.csv    <- Spearman results (OFAT sweeps only)
    data/experiments/sensitivity_heatmap.png     <- visual summary
============================================================
"""

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .metrics import compute_all_stylized_facts

# ------------------------------------------------------------
# Experimental Design (36 Configurations)
# ------------------------------------------------------------

BASE_COUNTS = {
    "retail_count": 50,
    "contrarian_count": 15,
    "institutional_count": 5,
    "momentum_count": 25,
    "value_investor_count": 30,
}

TOTAL_POPULATION = sum(BASE_COUNTS.values())      # 125

# Experimental levels for the manipulated agent
LEVEL_PERCENTAGES = [0.00, 0.10, 0.25, 0.40, 0.60]

SEED = 42

PARAMETERS = [
    "retail_count",
    "contrarian_count",
    "institutional_count",
    "momentum_count",
    "value_investor_count",
]


# ------------------------------------------------------------
# Helper Functions
# ------------------------------------------------------------

def proportional_redistribution(vary_parameter, target_count):
    """
    Creates one OFAT configuration.

    The selected parameter is assigned 'target_count' agents.

    The remaining agents are redistributed among the other four
    agent classes while preserving their baseline proportions.

    Total population always remains constant.
    """

    counts = {}

    remaining_population = TOTAL_POPULATION - target_count

    other_parameters = [
        p for p in PARAMETERS if p != vary_parameter
    ]

    baseline_other_total = sum(
        BASE_COUNTS[p]
        for p in other_parameters
    )

    # Initial proportional allocation
    allocated = 0

    for parameter in other_parameters[:-1]:

        proportion = (
            BASE_COUNTS[parameter]
            / baseline_other_total
        )

        value = round(remaining_population * proportion)

        counts[parameter] = value
        allocated += value

    # Last parameter receives remainder to ensure exact total
    last_parameter = other_parameters[-1]
    counts[last_parameter] = remaining_population - allocated

    counts[vary_parameter] = target_count

    return counts


def validate_counts(counts):
    """
    Safety check.
    """

    assert sum(counts.values()) == TOTAL_POPULATION

    for value in counts.values():
        assert value >= 0


# ------------------------------------------------------------
# Configuration Generator
# ------------------------------------------------------------

def generate_configs():

    configs = []
    config_number = 0

    # --------------------------------------------------------
    # 1. Baseline
    # --------------------------------------------------------

    configs.append({
        "config_id": f"cfg_{config_number:03d}",
        "seed": SEED,
        "design": "Baseline",
        "counts": dict(BASE_COUNTS),
    })

    config_number += 1

    # --------------------------------------------------------
    # 2. OFAT Experiments
    # --------------------------------------------------------

    for parameter in PARAMETERS:

        for percentage in LEVEL_PERCENTAGES:

            target = round(TOTAL_POPULATION * percentage)

            counts = proportional_redistribution(
                parameter,
                target
            )

            validate_counts(counts)

            configs.append({
                "config_id": f"cfg_{config_number:03d}",
                "seed": SEED,
                "design": "OFAT",
                "varied_parameter": parameter,
                "target_percentage": percentage,
                "counts": counts,
            })

            config_number += 1

    # --------------------------------------------------------
    # 3. Archetype Configurations
    # --------------------------------------------------------

    archetypes = [

        ("Retail Dominated",
         {"retail_count": 75,
          "contrarian_count": 10,
          "institutional_count": 5,
          "momentum_count": 15,
          "value_investor_count": 20}),

        ("Institutional Dominated",
         {"retail_count": 20,
          "contrarian_count": 10,
          "institutional_count": 60,
          "momentum_count": 15,
          "value_investor_count": 20}),

        ("Momentum Heavy",
         {"retail_count": 20,
          "contrarian_count": 10,
          "institutional_count": 5,
          "momentum_count": 75,
          "value_investor_count": 15}),

        ("Fundamentalist Heavy",
         {"retail_count": 20,
          "contrarian_count": 10,
          "institutional_count": 5,
          "momentum_count": 15,
          "value_investor_count": 75}),

        ("Contrarian Heavy",
         {"retail_count": 20,
          "contrarian_count": 75,
          "institutional_count": 5,
          "momentum_count": 10,
          "value_investor_count": 15}),

        ("Retail + Momentum",
         {"retail_count": 45,
          "contrarian_count": 10,
          "institutional_count": 5,
          "momentum_count": 45,
          "value_investor_count": 20}),

        ("Institution + Value",
         {"retail_count": 15,
          "contrarian_count": 10,
          "institutional_count": 40,
          "momentum_count": 10,
          "value_investor_count": 50}),

        ("Balanced Active",
         {"retail_count": 30,
          "contrarian_count": 20,
          "institutional_count": 15,
          "momentum_count": 30,
          "value_investor_count": 30}),

        ("Retail + Contrarian",
         {"retail_count": 45,
          "contrarian_count": 35,
          "institutional_count": 5,
          "momentum_count": 15,
          "value_investor_count": 25}),

        ("Even Distribution",
         {"retail_count": 25,
          "contrarian_count": 25,
          "institutional_count": 25,
          "momentum_count": 25,
          "value_investor_count": 25}),
    ]

    for name, counts in archetypes:

        validate_counts(counts)

        configs.append({
            "config_id": f"cfg_{config_number:03d}",
            "seed": SEED,
            "design": "Archetype",
            "archetype": name,
            "counts": counts,
        })

        config_number += 1

    # assert len(configs) == 36

    # return configs
    assert len(configs) == 36

    return [configs[0]]

# ------------------------------------------------------------
# RUNNER
# ------------------------------------------------------------

def run_all_configs(configs, experiments_dir):
    """
    Calls your (patched) run_market_simulation for each config.
    Import is done lazily so this file can be dropped into your
    project root next to simulator.py.
    """
    from .simulator import run_market_simulation  # your patched version

    experiments_dir.mkdir(parents=True, exist_ok=True)
    manifest = []

    for cfg in configs:
        run_dir = experiments_dir / cfg["config_id"]
        run_dir.mkdir(parents=True, exist_ok=True)

        print(f"Running {cfg['config_id']}  [{cfg['design']}"
              f"{' - ' + cfg['varied_parameter'] if cfg.get('varied_parameter') else ''}"
              f"{' - ' + cfg['archetype'] if cfg.get('archetype') else ''}]...")

        try:
            run_market_simulation(
                agent_counts=cfg["counts"],
                seed=cfg["seed"],
                output_dir=run_dir,
            )
            status = "ok"
        except Exception as e:
            print(f"  FAILED: {e}")
            status = f"failed: {e}"

        manifest.append({
            **cfg["counts"],
            "config_id": cfg["config_id"],
            "seed": cfg["seed"],
            "design": cfg.get("design"),
            "varied_parameter": cfg.get("varied_parameter"),
            "target_percentage": cfg.get("target_percentage"),
            "archetype": cfg.get("archetype"),
            "status": status,
        })

    manifest_df = pd.DataFrame(manifest)
    manifest_df.to_csv(experiments_dir / "manifest.csv", index=False)
    return manifest_df


# ------------------------------------------------------------
# METRICS PASS
# ------------------------------------------------------------

def compute_metrics_for_all_runs(manifest_df, experiments_dir):
    rows = []
    for _, row in manifest_df.iterrows():
        if row["status"] != "ok":
            continue
        csv_path = experiments_dir / row["config_id"] / "MARKET_STATE_DATA.csv"
        if not csv_path.exists():
            print(f"  Missing output for {row['config_id']}, skipping.")
            continue

        facts = compute_all_stylized_facts(csv_path, burn_in=50)
        rows.append({**row.to_dict(), **facts})

    summary_df = pd.DataFrame(rows)
    summary_df.to_csv(experiments_dir / "summary_metrics.csv", index=False)
    return summary_df


# ------------------------------------------------------------
# SENSITIVITY ANALYSIS (Spearman, OFAT sweeps only)
# ------------------------------------------------------------

PARAM_COLS = PARAMETERS
METRIC_COLS = ["fat_tails", "volatility_clustering", "volume_volatility_correlation"]


def run_sensitivity_analysis(summary_df, experiments_dir):
    """
    Computes Spearman correlation between each parameter and each
    stylized fact metric, using ONLY that parameter's own OFAT sweep
    plus the shared Baseline as an anchor point (6 points per
    parameter: 5 OFAT levels + baseline).

    Archetype configs are deliberately excluded here — multiple
    parameters move simultaneously in those, so pooling them into a
    single-parameter correlation would conflate effects and violate
    the "isolate one factor" logic the OFAT design is built on.
    Archetypes remain in summary_metrics.csv for descriptive/
    qualitative comparison in the writeup.
    """
    results = []
    baseline_row = summary_df[summary_df["design"] == "Baseline"]

    for param in PARAM_COLS:
        ofat_rows = summary_df[
            (summary_df["design"] == "OFAT") & (summary_df["varied_parameter"] == param)
        ]
        subset = pd.concat([baseline_row, ofat_rows], ignore_index=True)

        if subset[param].nunique() < 2:
            continue

        for metric in METRIC_COLS:
            valid = subset[[param, metric]].dropna()
            if len(valid) < 4:
                continue
            rho, p_value = spearmanr(valid[param], valid[metric])
            results.append({
                "parameter": param,
                "metric": metric,
                "spearman_rho": rho,
                "p_value": p_value,
                "n": len(valid),
            })

    sens_df = pd.DataFrame(results)
    sens_df.to_csv(experiments_dir / "sensitivity_analysis.csv", index=False)
    return sens_df


def plot_sensitivity_heatmap(sens_df, experiments_dir):
    if sens_df.empty:
        print("No sensitivity results to plot (check that OFAT parameters vary across configs).")
        return

    pivot = sens_df.pivot(index="parameter", columns="metric", values="spearman_rho")

    fig, ax = plt.subplots(figsize=(8, 5))
    im = ax.imshow(pivot.values, cmap="RdBu_r", vmin=-1, vmax=1, aspect="auto")

    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns, rotation=30, ha="right")
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index)

    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            val = pivot.values[i, j]
            if not np.isnan(val):
                ax.text(j, i, f"{val:.2f}", ha="center", va="center", color="black")

    ax.set_title("Spearman sensitivity: agent ratio vs stylized fact intensity\n(OFAT sweeps + baseline, n=6 per parameter)")
    fig.colorbar(im, ax=ax, label="Spearman rho")
    fig.tight_layout()
    fig.savefig(experiments_dir / "sensitivity_heatmap.png", dpi=150)
    plt.close(fig)


# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------

if __name__ == "__main__":
    experiments_dir = Path("data/experiments")

    configs = generate_configs()
    print(f"Generated {len(configs)} configurations "
          f"(1 Baseline + 25 OFAT + 10 Archetype).")

    manifest_df = run_all_configs(configs, experiments_dir)
    print(f"\n{(manifest_df['status'] == 'ok').sum()} / {len(manifest_df)} runs succeeded.")

    summary_df = compute_metrics_for_all_runs(manifest_df, experiments_dir)
    print(f"Computed metrics for {len(summary_df)} runs.")

    sens_df = run_sensitivity_analysis(summary_df, experiments_dir)
    print("\nSensitivity results (OFAT sweeps only):")
    print(sens_df.to_string(index=False))

    plot_sensitivity_heatmap(sens_df, experiments_dir)
    print(f"\nDone. See {experiments_dir}/ for all outputs.")