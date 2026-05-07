# Backtest

Python port of the Pine indicator's rules so you can test parameter changes
on historical CSVs without paper-trading them.

## Run it

```bash
python3 backtest/backtest.py data/NQ_1m.csv
python3 backtest/backtest.py data/GC_1m.csv --symbol GC --primary-days 30
python3 backtest/backtest.py data/NQ_1m.csv --grades A+ --min-rr 2.0
```

## CSV format

```
time,open,high,low,close,volume
2024-01-02T09:30:00,16800.25,16812.5,16795.0,16808.75,12345
...
```

TradingView's "Export chart data" button gives you this directly. Times
are assumed to be in the exchange timezone — if your CSV is UTC, shift
it before feeding in.

## Output

```
Total signals : 142
Closed        : 138  (open at end-of-data: 4)
Wins / Losses : 76 / 62
Win rate      : 55.1%
Avg R         : 0.41
Expectancy    : 0.41 R / trade

grade  n   WR    avgR
A+    24  62.5%  0.78
A     59  54.2%  0.42
B+    55  50.9%  0.18

Target-reason breakdown
  NY HoD          n=  41  WR= 58.5%  avgR= 0.61
  PDH             n=  28  WR= 53.6%  avgR= 0.42
  LVN above       n=  35  WR= 51.4%  avgR= 0.31
  ATR fallback    n=  34  WR= 47.1%  avgR= 0.18
```

The "Target-reason breakdown" is the most useful read — if `ATR fallback`
trades have lower expectancy than `NY HoD` / `PDH` trades, that's
evidence the structural-target picker is doing real work. If they're
similar, structural targets aren't adding edge yet.

## Caveats

This Python port is *close* to the Pine indicator but not byte-identical.
Differences:

1. **Profile rebuild cadence** — Pine rebuilds the VP only on the last bar
   for visualization; the Python backtest rebuilds every N bars
   (`--profile-every`, default 5) to be tractable. Lower N = more
   accurate but slower.
2. **Volume regime** — Pine has `healthy_up`/`healthy_dn` from linreg slopes;
   the Python port simplifies this (`c5` is permissive). This means the
   Python backtest will likely be slightly more permissive than Pine.
3. **Footprint trigger** — both Pine and Python skip this. Real trades on
   the indicator require manual confirmation; the backtest assumes any
   A/A+ at-level setup is taken.
4. **Fills** — entries fill at next-bar open; stops/targets fill on
   intrabar high/low touches. No slippage or commissions modeled.
5. **Session times** — hardcoded to NYSE-style schedule. If you're
   backtesting outside US-equity-index hours, edit the `*_OPEN`/`*_CLOSE`
   constants in `backtest.py`.

Use this as a sanity check, not a P&L oracle. The journal + analyzer is
still the source of truth for live performance.

## Getting historical data

- **TradingView**: chart → ⋮ menu → "Export chart data". 1m intraday is
  limited to ~5000 bars on retail; for longer periods use a higher TF or
  a real data feed.
- **Databento / Polygon / CME DataMine** for proper CME futures tick + minute
  data.
- **Tradovate / Topstep API** if you have an account — they expose
  historical 1m bars going back far enough to be useful.
