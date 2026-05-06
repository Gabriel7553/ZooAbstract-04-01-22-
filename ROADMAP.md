# Roadmap

Treat this like a backlog. Pull items as the journal data justifies them.

## Phase 1 — Live (now)
- [x] Distill jwill rules into STRATEGY.md
- [x] Pine v6 indicator: VP, HVN/LVN/Ledge, daily bias, A+/B+ grading,
      entry/SL/TP, alerts
- [x] Trade journal CSV + analyzer
- [ ] Gabe paper-trades or sim-trades 20+ setups, fills the journal
- [ ] First analyzer run → identify which confluences carry edge

## Phase 2 — Tighten
- [ ] Re-weight grading from journal lift (drop confluences with no edge,
      promote ones with clear edge)
- [ ] Multi-timeframe VP (drive levels off the higher TF the way jwill
      does — 30D/90D/180D as primary, intraday as confirmation)
- [ ] Better Ledge detection: require a sustained HVN cluster, not a
      single bin, before flagging
- [ ] Session-aware bias (NY open vs Asia is different)
- [ ] Anchored VP from prior day high/low / weekly open

## Phase 3 — Backtest at scale
- [ ] Convert indicator to a `strategy(...)` script for TV's built-in
      backtester
- [ ] Or: pull historical bars (CME via databento, or TV exports) and
      backtest in Python with the same rules as the Pine
- [ ] Walk-forward validation per quarter

## Phase 4 — Automation (only if Phase 1–3 show edge)
- [ ] TradingView webhook → small Flask/FastAPI server that
      logs setups + screenshots automatically
- [ ] Optional: broker bridge (Tradovate / Topstep) for limit
      orders into A+ levels with bracket stops
- [ ] Web dashboard (one screen) for live setup + journal stats
- [ ] Footprint approximation from tick / depth data via databento or
      Polygon if we want order-flow without MotiveWave

## Open questions for Gabe
- Symbol(s) you trade most? (ES, NQ, MES, MNQ, others?)
- Typical session — RTH only, or globex?
- Account size / per-trade risk %? (drives position sizing in dashboard)
- Do you want the indicator to size automatically from $ risk?
