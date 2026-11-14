#!/usr/bin/env python3
"""Polymarket FAA-attribution forecast: random-walk with slight mean reversion.

For each market with checkpoint price x: median path pulls x toward the
median of its recent history (weight 0.1 over the 240-minute horizon);
quantile spread sigma=0.001 per sqrt(minute), normal quantiles at the
five levels, clamped to [0,1], rounded to 6 decimals. Deterministic."""
import json, math, os, glob, statistics

Z = (-1.644854, -0.674490, 0.0, 0.674490, 1.644854)
SIGMA = 0.001
MR = 0.1
MRWIN = 2880
H = 240

def clamp(x):
    return 0.0 if x < 0 else (1.0 if x > 1 else x)

def forecast(m):
    p = m["prices"]
    x = p[-1]
    win = p[-MRWIN:]
    med = statistics.median(win) if len(win) > 10 else x
    rows = []
    for h in range(1, H + 1):
        mu = x - MR * (x - med) * (h / H)
        s = SIGMA * math.sqrt(h)
        rows.append([round(clamp(mu + z * s), 6) for z in Z])
    return rows

def main():
    ind = os.environ.get("MAKEFUN_INPUT_DIR", "/input")
    outd = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outd, exist_ok=True)
    for path in sorted(glob.glob(os.path.join(ind, "*.in"))):
        case = json.load(open(path))
        cid = case["case"]
        rows_by_id = {m["id"]: forecast(m) for m in case["markets"]}
        out = {"forecasts": [{"id": k, "q": rows_by_id[k]} for k in rows_by_id]}
        with open(os.path.join(outd, cid + ".out"), "w") as f:
            json.dump(out, f, separators=(",", ":"))

main()
