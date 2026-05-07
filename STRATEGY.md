# Strategy — Distilled from jwill (v2)

Source: jwill's notes on Ledges, LVNs, HVNs, Time-Based Volume, and Discord
Q&A with Gabe (4/16/26 and 4/21/26). Footprint triggers, level rules, and
HTF-bias gates are encoded as rules below so the indicator and journal
share the same model. v2 adds EMAs + VWAP, session/HTF level structure,
and structural stop/target logic.

## Tools jwill uses

- **MotiveWave** for everything (volume profile + footprint).
- **Volume Profiles**: 3-day, 7-day, 30-day, 90-day, 180-day. v2 supports
  selecting one OR overlaying POCs from all five.
- **Footprint**: 1-minute only — looking for **absorption** and **exhaustion**.
- **Time-based volume** on the daily for HTF bias.
- **EMAs + VWAP** instead of plain SMAs (v2). Default stack: 9 / 21 / 50 / 200
  with Session VWAP (anchored to NY/RTH for NQ, daily for GC).
- *Not used*: FVGs, "vu's" indicators (Gabe's note: "vu" / "vus" is a
  person — ignore those references).

## Markets we trade

- **NQ / MNQ** (Nasdaq-100 futures)
- **GC / MGC** (Gold futures)

The indicator auto-detects the symbol root and picks the right session anchor
(NY/RTH for NQ; daily reset for GC since gold trades through Asia/London).

## Core market model

Markets auction. Liquidity forms where buyers and sellers agree → that's
an **HVN**. Where they don't agree → low volume → **LVN** /
**Ledge**. Price seeks HVNs to transact, moves through LVNs quickly when
trend is strong, and rejects from LVNs / Ledges when momentum is on
that side or when a trend is exhausting.

## Level definitions

### HVN — High Volume Node
- Peak on the volume profile.
- **Avoid trading inside HVNs — usually just chop.**
- Use as a destination / mean-reversion magnet.

### LVN — Low Volume Node
- Valley between two HVNs. Aggressive movement printed it.
- **Reject when** aligned with HTF trend, OR at trend exhaustion.
- **Runs through when** traded against trend — low volume = no orders to defend.

### Ledge
- Flat shelf at the **edge** of an HVN where volume drops to a low-volume zone.
- Same support/resistance logic as LVNs.
- **Same trend-alignment rule** — bearish ledge in a bullish HTF gets run through.

### Liquidity / structural levels (new in v2)
The indicator also marks and uses these for stop/target placement:
- **PDH / PDL** — prior day high / low.
- **Asia / London / NY H/L** — today's per-session extremes.
- **PWH / PWL** — prior week high / low.
- **PMH / PML** — prior month (optional).
- **ATH(v) / ATL(v)** — visible-range all-time high / low.
- **Developing POC (dPOC)** — POC of just today's session. Solves the
  "POC is 1000 points away on a 1m chart" problem. Use this as a near-term
  magnet alongside the HTF POC.

> "Make sure with LVNs and ledges to make sure they align with the trend
> or the overall market structure. If the momentum is not on your side
> they can be ran through very easily since they are areas of low
> volume." — jwill

## Daily bias (HTF) — v2 rules

Built from EMAs + Session VWAP + time-based volume regime.

- **EMA stack** drives trend: bullish stack = 9 > 21 > 50 > 200; bearish = inverse.
- **Trend gate** (lighter): close > 21 > 50 (bull) or close < 21 < 50 (bear).
- **VWAP confluence**: longs require price above VWAP; shorts below.
- **Volume spike** = peak panic / peak fomo → temporary top/bottom.
  - Spike on a green-bar rally → bearish reversal watch (exhaustion top).
  - Spike on a red-bar drop → bullish reversal watch (exhaustion bottom).
- **Decreasing volume + steady trend** = healthy trend → continuation bias.

## Setup process (jwill's flow, refined)

1. Set HTF bias from EMAs + VWAP + TBV (BULL / BEAR / NEUTRAL).
2. Mark levels from VP: Ledges and LVNs aligned with the bias.
3. Watch session/HTF levels (PDH, PDL, NY HoD, etc.) — these are where
   stops cluster. Targets, not entries.
4. **Wait at the level**:
   - If footprint triggers (absorption / exhaustion) are already
     printing into the level → **limit in**.
   - Otherwise → **wait for trigger at the level**, then enter.
5. Avoid HVNs entirely.

## Grading — 7 confluences (v2)

Score 0–7 → grade.

| # | Confluence | Pass condition |
|---|---|---|
| 1 | HTF bias defined | BULL or BEAR (not NEUTRAL) |
| 2 | At a level | Within ATR×proximity of an LVN or Ledge |
| 3 | Level aligned with bias | Long: level ≤ price in bull. Short: level ≥ price in bear |
| 4 | Not in HVN | Current price's bin < HVN threshold |
| 5 | Volume regime favorable | healthy-trend slope OR exhaustion reversal OR absorption-proxy |
| 6 | EMA stack aligned | Bull: 9>21>50>200. Bear: inverse |
| 7 | VWAP aligned | Long: above VWAP. Short: below VWAP |

- **A+** = 7/7 → take it (still confirm footprint trigger).
- **A**  = 6/7 → take it if footprint is clean.
- **B+** = 5/7 → consider, smaller size.
- **B**  = 2–4/7 → skip unless footprint is very strong.
- **C**  = 0–1/7 → skip.

The dashboard now shows each confluence as ✓/✗ with the actual value, so
you can see exactly *why* a setup graded what it did. If VWAP confluence
is disabled in inputs, scoring reverts to 6 confluences (totals adjust
automatically).

The footprint trigger (absorption / exhaustion on the 1m) is still the
**final gate** and is **not** computed by Pine — TradingView retail tier
doesn't have order-flow data. The on-chart "AB" (absorption-proxy) and
"EX" (exhaustion) markers are *hints* based on candle shape + volume —
useful but not a substitute for actual footprint reads.

## Risk — Structural stops & targets (v2)

This is the big change. Stops and targets are no longer arbitrary
ATR multiples. They snap to structure, with a reason printed in the
dashboard.

### Stop placement
- **At a level** (LVN/Ledge): just beyond the level by `slBuffer × ATR`
  (default 0.25). Reason in dashboard: "LVN structural" / "Ledge structural".
- **Not at a level** (still in-bias): ATR fallback. Reason: "ATR fallback".

### Target placement (priority ladder)
For LONG, scan upward; for SHORT, scan downward:

1. **NY HoD/LoD** — today's RTH extreme
2. **London HoD/LoD**
3. **Asia HoD/LoD**
4. **PDH/PDL**
5. **PWH/PWL**
6. **PMH/PML** (if enabled)
7. **ATH/ATL (visible range)**
8. **Next LVN beyond entry**

Pick the **closest** candidate that yields ≥ `minRR` (default 1.5R). The
dashboard shows that price + a label like `(NY HoD)` so you know exactly
why the target is where it is.

If no structural target gives ≥ minRR, fall back to `fallbackTP × ATR`
(default 2.5).

### Why this matters
You said it best: "we don't put stop and take profit in random places."
A target at "NY HoD" or "PDH" is a *thesis*: price is rotating into the
liquidity above. A stop just beyond an LVN is a *thesis*: if the LVN
breaks, the level was wrong, get out. ATR-only stops/targets can't tell
you those things.

## Marking on-chart

- **EX** triangle (red above bar / green below bar) → exhaustion top/bottom.
  Background also tints lightly so you can see it at a glance.
- **AB** circle (cyan below / magenta above) → absorption-proxy candle
  *at an LVN/Ledge only* (we don't want noise everywhere).
- Profile boxes are pushed to the right of the last bar by `profileOffset`
  bars so they don't overlap candles.
- VP lines (LVN red dotted / Ledge orange / HVN cyan dashed) are drawn
  with text labels on the right edge. Multi-VP "All" mode adds 5 colored
  POC lines (white/yellow/orange/red/fuchsia for 3D/7D/30D/90D/180D).

## What we are explicitly NOT doing

- No FVGs.
- No counter-trend Ledge/LVN trades.
- No HVN entries.
- No trades without a defined HTF bias.
- No trades without a footprint trigger (or a clean limit fill into the
  level when triggers were already printing).
- No "random" stops or targets — every level we use must have a name.
