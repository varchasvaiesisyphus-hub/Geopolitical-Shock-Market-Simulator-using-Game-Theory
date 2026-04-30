"""
Export simulation results to Excel.

FIX — ARCHITECTURAL ISSUE:
The original file did this at MODULE LEVEL (outside any function):
    from simulation.simulator import data   ← this RUNS the entire simulation
    df = pd.DataFrame(data)
    df.to_excel(...)

This means importing this module as a library would trigger the whole
simulation as a side effect — a classic Python anti-pattern.

The fix: wrap everything in a main() function and guard with
`if __name__ == "__main__"`. Now you can safely import this module
elsewhere without accidentally running a 100-step simulation.
"""

import pandas as pd


def export_results(data, filename="stock_simulation_results.xlsx"):
    """Save simulation data list to an Excel file."""
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False)
    print(f"Saved {len(df)} rows to '{filename}'")
    return df


if __name__ == "__main__":
    # Only runs when you execute this file directly:
    #   python data/simulation_results.py
    # NOT when you import it from somewhere else.
    from simulation.simulator import data
    export_results(data)