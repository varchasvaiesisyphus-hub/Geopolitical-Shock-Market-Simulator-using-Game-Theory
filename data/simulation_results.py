"""
Export simulation results to Excel or CSV.
Run directly:  python data/simulation_results.py
"""
import pandas as pd


def export_results(data, filename="stock_simulation_results.xlsx"):
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False)
    print(f"Saved {len(df)} rows → '{filename}'")
    return df


if __name__ == "__main__":
    from simulation.simulator import data
    export_results(data)