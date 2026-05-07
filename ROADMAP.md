# Roadmap

Treat this like a backlog. Pull items as the journal data justifies them.

## Phase 1 — Live (now)
- [x] Distill jwill rules into STRATEGY.md
- [x] Pine v6 indicator: VP, HVN/LVN/Ledge, daily bias, A+/B+ grading,
      entry/SL/TP, alerts
- [x] Trade journal CSV + analyzer
- [x] **v2** — EMAs (9/21/50/200) + Session VWAP, per-confluence ✓/✗
      breakdown, structural stop/target picker (PDH/NY HoD/etc with
      reason text), multi-VP "All" overlay, developing POC, session H/L,
      exhaustion/absorption candle markers, profile pushed off candles
- [x] Python backtest scaffold (`backtest/backtest.py`)
- [ ] Gabe paper-trades or sim-trades 20+ setups, fills the journal
- [ ] First analyzer run → identify which confluences carry edge
- [ ] First Python backtest pass on 90 days of NQ + GC 1m data

## Phase 2 — Tighten
- [ ] Re-weight grading from journal lift (drop confluences with no edge,
      promote ones with clear edge). Most likely candidates to reweight
      after 30+ trades: VWAP align (7), EMA stack (6), volume regime (5).
- [ ] Multi-timeframe VP polishing — currently the "All" overlay is just
      POCs. Consider adding HVN/LVN clusters from each lookback when 2+
      lookbacks agree on a level.
- [ ] Better Ledge detection: require a sustained HVN cluster, not a
      single bin, before flagging.
- [ ] Session-aware bias (NY open vs Asia is different).
- [ ] Anchored VP from prior day high/low / weekly open.
- [ ] Tune session times for GC specifically (gold has its own COMEX-ish
      schedule that doesn't perfectly match the equity index sessions).

## Phase 3 — Backtest at scale
- [ ] Convert indicator to a `strategy(...)` script for TV's built-in
      backtester (lets you see the equity curve directly on the chart).
- [ ] Pull historical bars (CME via databento, or TV exports) and run
      `backtest/backtest.py` over 1–2y of NQ + GC.
- [ ] Walk-forward validation per quarter — does the rule set still
      produce edge in a fresh window after tuning on the prior one?
- [ ] Reconcile Pine-vs-Python results: any divergence > 5% in win rate
      means one of the ports has a bug.

## Phase 4 — Automation (only if Phase 1–3 show edge)
- [ ] TradingView webhook → small Flask/FastAPI server that
      logs setups + screenshots automatically into the journal.
- [ ] Optional: broker bridge (Tradovate / Topstep) for limit orders
      into A+ levels with bracket stops.
- [ ] Web dashboard (one screen) for live setup + journal stats.
- [ ] Footprint approximation from tick / depth data via databento or
      Polygon if we want order-flow without MotiveWave.

## Open questions for Gabe
- Account size / per-trade risk %? (drives position sizing in dashboard
  — currently not modeled).
- Do you want the indicator to size automatically from $ risk?
- What's a "good" R per setup for you — 1.5? 2? Depends on win rate, and
  win rate depends on journal data.
- Does the 1m chart bias check (close > EMA21 > EMA50) match what you
  *feel* the trend is? If you're getting BULL signals during obvious
  consolidation, we should add a slope or ADX gate.
- Do you want strict A+ only, or are A setups acceptable when the
  footprint confirms?
