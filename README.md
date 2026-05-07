# Jwill Volume Strategy — Trading System

A trading system built around jwill's volume-profile + footprint-trigger
strategy. Goal: stop guessing, take only graded setups, track every trade,
iterate the rules from real data.

## What's in this repo

```
STRATEGY.md                          Distilled rules from jwill (read first)
pinescript/jwill_volume_strategy.pine   TradingView indicator (v6)
journal/trade_log_template.csv       Empty trade journal — copy and fill
journal/analyzer.py                  Win-rate / confluence breakdown
ROADMAP.md                           What's next
```

## How you use it

1. **TradingView** — paste `pinescript/jwill_volume_strategy.pine` into
   Pine Editor, save, add to your futures chart. The dashboard (top-right)
   tells you:
   - Daily bias (BULL / BEAR / NEUTRAL)
   - Side (LONG / SHORT / —)
   - Grade (A+ / A / B+ / B / C) with confluence score
   - Entry, Stop, Target, Points, R:R
   - Whether price is at a Ledge / LVN / HVN(avoid) / none
2. **Set alerts** on "A+ Long" and "A+ Short" — those are the trades
   where every confluence is green.
3. **Footprint trigger is manual** — TradingView free tier has no order
   flow. The indicator gets you to the level with bias confirmed; you
   confirm absorption / exhaustion on the 1m footprint in MotiveWave
   before pulling the trigger (or limit into the level if triggers were
   already printing into it, like jwill said).
4. **Log every trade** in `journal/trade_log_template.csv`. Columns
   capture each confluence so we can see which ones actually predict
   wins.
5. **Run the analyzer** weekly: `python3 journal/analyzer.py
   journal/trade_log_template.csv` — it prints win rate by grade and
   per-confluence lift. That's how we tune the rules.

## Why not a custom web app?

- The strategy needs your eyes on a chart anyway (footprint trigger).
- TradingView already gives you alerts, mobile push, and 5y of data.
- Building a web app first means babysitting infra instead of trading.

We can revisit if/when the journal shows clear edges and you want
auto-execution or webhook-based stat tracking.

## Branch / workflow

Working branch: `claude/project-strategy-setup-amflX`. Push commits there;
review before merging to `main`.
