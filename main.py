#!/usr/bin/env python3
"""Generate deterministic five-quantile price paths for FAA attribution cases.

Each ``*.in`` file contains one case and markets with one-minute prices.  The
forecaster starts at the latest price, blends 10% toward the median of the
trailing 2,880 prices over 240 minutes, and adds a Gaussian random-walk
spread.  Every forecast is clamped to [0, 1] and rounded to six decimals.
"""

from __future__ import annotations

import json
import math
import os
import statistics
from pathlib import Path


INPUT_DIRECTORY = Path(os.environ.get("MAKEFUN_INPUT_DIR", "/input"))
OUTPUT_DIRECTORY = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
INPUT_GLOB = "*.in"
HORIZON_MINUTES = 240
HISTORY_MINUTES = 2880
# Standard-normal quantiles for the 5%, 25%, 50%, 75%, and 95% levels.
QUANTILES = (-1.644854, -0.674490, 0.0, 0.674490, 1.644854)
SCALE = 0.001
MEAN_REVERSION = 0.1


def bounded(value: float) -> float:
    """Constrain a forecast price to the valid binary-market range."""
    return min(max(value, 0.0), 1.0)


def forecast_market(market: dict[str, object]) -> list[list[float]]:
    """Produce one 240-row forecast table for a single market."""
    prices = market["prices"]
    current_price = prices[-1]
    history = prices[-HISTORY_MINUTES:]
    median_price = statistics.median(history)
    forecast_rows: list[list[float]] = []

    for minutes in range(1, HORIZON_MINUTES + 1):
        mean_reversion = MEAN_REVERSION * (current_price - median_price) * (
            minutes / HORIZON_MINUTES
        )
        mean = current_price - mean_reversion
        spread = SCALE * math.sqrt(minutes)
        forecast_rows.append(
            [round(bounded(mean + quantile * spread), 6) for quantile in QUANTILES]
        )

    return forecast_rows


def forecast_case(case: dict[str, object]) -> dict[str, object]:
    """Map market IDs to their forecast tables in input order."""
    forecasts = [
        {"id": market["id"], "q": forecast_market(market)}
        for market in case["markets"]
    ]
    return {"forecasts": forecasts}


def write_output(path: Path, document: dict[str, object]) -> None:
    """Write compact UTF-8 JSON, preserving input-derived ordering."""
    path.write_text(
        json.dumps(document, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )


def main() -> None:
    """Create the output directory and process input cases in name order."""
    OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)
    for input_path in sorted(INPUT_DIRECTORY.glob(INPUT_GLOB)):
        case = json.loads(input_path.read_text(encoding="utf-8"))
        output_path = OUTPUT_DIRECTORY / f"{case['case']}.out"
        write_output(output_path, forecast_case(case))


if __name__ == "__main__":
    main()
