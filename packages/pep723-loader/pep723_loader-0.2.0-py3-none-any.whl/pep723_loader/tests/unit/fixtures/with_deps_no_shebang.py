# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "numpy>=1.24.0",
#   "pandas>=2.0.0",
# ]
# ///
"""Test script with PEP 723 dependencies but no shebang."""

import numpy as np
import pandas as pd


def analyze_data(data: list[float]) -> dict[str, float]:
    """Analyze numeric data using numpy and pandas.

    Args:
        data: List of numeric values

    Returns:
        Dictionary with statistical metrics
    """
    arr = np.array(data)
    df = pd.DataFrame({"values": data})

    return {"mean": float(arr.mean()), "std": float(arr.std()), "median": float(df["values"].median())}


if __name__ == "__main__":
    result = analyze_data([1.0, 2.0, 3.0, 4.0, 5.0])
    print(result)
