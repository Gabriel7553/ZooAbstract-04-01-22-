# Jwill Volume Strategy — Trading System (v2)

A trading system built around jwill's volume-profile + footprint-trigger
strategy, tuned for the markets you actually trade (NQ and GC futures).
Goal: stop guessing, take only graded setups, place stops and targets at
real structure, track every trade, iterate the rules from real data.

## What's in this repo

```
STRATEGY.md                          Distilled rules (read first)
pinescript/jwill_volume_strategy.pine   TradingView indicator (Pine v6)
backtest/backtest.py                 Python backtest scaffold (TV CSV → stats)
journal/trade_log_template.csv       Empty trade journal — copy and fill
journal/analyzer.py                  Win-rate / confluence breakdown
journal/SCHEMA.md                    Journal column reference
ROADMAP.md                           What's next
```

## How you use it

1. **TradingView** — paste `pinescript/jwill_volume_strategy.pine` into
   Pine Editor, save, add to your futures chart. The dashboard (top-right)
   is 8 rows for instant scan:
   - **Big signal cell**: GO LONG / GO SHORT / WAIT / SKIP
   - Grade (A+ / A / B+ / B / C) with score X/7
   - Confluence pattern (one row of 7 ✓/✗ — see at a glance which boxes
     are checked)
   - Entry
   - **Structural** Stop with reason (e.g. `28705 · LVN structural`)
   - **Structural** Target with reason (e.g. `28780 · NY HoD`)
   - R:R (color-coded: lime ≥ 2R, yellow ≥ 1.5R, red below)
   - Note: lookback + symbol
2. **Volume Profile lookback** — pick a single horizon from the dropdown
   (3D/7D/30D/90D/180D/Custom) or pick **`All`** to overlay POCs from
   every lookback at once (color-coded).
3. **Set alerts** on "A+ Long" and "A+ Short". A/A+ alerts and exhaustion /
   absorption-proxy alerts are also wired.
4. **Footprint trigger is manual** — TradingView free tier has no order
   flow. The indicator gets you to the level with bias confirmed; you
   confirm absorption / exhaustion on the 1m footprint in MotiveWave
   before pulling the trigger (or limit into the level if triggers were
   already printing into it). The on-chart "AB" / "EX" markers are
   candle-shape hints, not a substitute for real footprint reads.
5. **Log every trade** in `journal/trade_log_template.csv`. Columns
   capture each confluence so we can see which ones actually predict
   wins.
6. **Run the analyzer** weekly:
   `python3 journal/analyzer.py journal/trade_log_template.csv` —
   prints win rate by grade and per-confluence lift.
7. **Backtest** historical CSVs:
   `python3 backtest/backtest.py path/to/NQ_1m.csv` — applies a Python
   port of the same rules and reports overall win rate, R:R, and per-grade
   stats. Useful for sanity-checking parameter changes without re-running
   them through paper trades.

## What's new in v2 (vs v1)

- **EMAs (9/21/50/200) replace SMAs**, plus Session VWAP as a 7th confluence.
- **8-row scannable dashboard** — big GO/WAIT/SKIP signal cell on top,
  confluence pattern as one row of ✓/✗, structural stop/target with
  reason text, color-coded R:R. Designed so you can decide in 1 second.
- **Solid-white VP gradient** — opacity scales with volume, flush to the
  price axis. Brightest bar = POC. No more 4-color rainbow.
- **Structural stops & targets** — every TP has a reason
  (PDH / NY HoD / Asia HoD / LVN above / ATH-visible / etc.), every stop
  is anchored to the level being defended.
- **Multi-VP overlay** — "All" mode draws POCs of 3D/7D/30D/90D/180D as
  thin colored lines.
- **Developing POC** — POC of just today's session, drawn as a yellow
  dashed line. Solves the "POC is 1000 points away" problem on intraday.
- **Session H/L lines** — Asia, London, NY H/L tracked live, plus
  prior-day, prior-week, optional prior-month, and visible-range ATH/ATL.
  Text labels only appear when level is within ~5 × ATR of price (no more
  spaghetti on the right edge).
- **EX exhaustion markers on candles** — triangles + faint background
  tint for volume-spike exhaustion tops/bottoms.
- **Per-symbol presets** — auto-detects NQ vs GC for VWAP / dPOC
  anchoring (RTH for NQ, daily for GC).
- **Always-populated trade plan** — Entry/Stop/Target now show even on
  long-bias / short-bias states, not only on A/A+ at-level setups.

## Backtesting

`backtest/backtest.py` ports the indicator's rules to Python. Feed it
TradingView CSV exports (or any OHLCV CSV with `time,open,high,low,close,volume`
columns):

```
python3 backtest/backtest.py data/NQ_1m_2024.csv
```

Output: total trades, win rate, average R, expectancy, breakdown by grade.
**Caveats** in `backtest/README.md` — the Python port is *close* to the
Pine logic but not byte-identical. Use it as a sanity check before
committing parameter changes to live trading.

## Why not a custom web app?

- The strategy needs your eyes on a chart anyway (footprint trigger).
- TradingView already gives you alerts, mobile push, and 5y of data.
- Building a web app first means babysitting infra instead of trading.

We can revisit if/when the journal shows a clear edge and you want
auto-execution or webhook-based stat tracking.

## Branch / workflow

Working branch: `claude/review-trading-strategy-XR7Hw`. Push commits there;
review before merging to `main`.
