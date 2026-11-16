# faa-forecast

Deterministic five-quantile price-path forecaster for FAA attribution cases. Built by an AI agent for a make.fun forecasting bounty.

## How it works

Each `*.in` case file holds markets with one-minute prices. For every market the forecaster:

1. Starts at the latest price.
2. Blends 10% toward the median of the trailing 2,880 prices over a 240-minute horizon (mean reversion).
3. Adds a Gaussian random-walk spread at the 5%, 25%, 50%, 75%, and 95% quantiles.
4. Clamps every forecast to [0, 1] and rounds to six decimals.

Output is one 240-row forecast table per market, written as compact JSON.

## Run

```sh
MAKEFUN_INPUT_DIR=/input MAKEFUN_OUTPUT_DIR=/output python3 main.py
```

Input and output directories default to `/input` and `/output`. Requires Python 3 (standard library only, no dependencies).

## Files

- `main.py` — the forecaster
- `LICENSE` — MIT

## License

MIT — see [LICENSE](LICENSE).
