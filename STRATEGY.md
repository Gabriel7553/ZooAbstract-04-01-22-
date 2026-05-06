# Strategy — Distilled from jwill

Source: jwill's notes on Ledges, LVNs, HVNs, Time-Based Volume, and Discord
Q&A with Gabe (4/16/26 and 4/21/26). Footprint triggers, level rules, and
HTF-bias gates are stated as rules below so the indicator and the journal
encode the same thing.

## Tools jwill actually uses

- **MotiveWave** for everything (volume profile + footprint).
- **Volume Profiles**: 3-day, 7-day, 30-day, 90-day, 180-day.
- **Footprint**: 1-minute only, looking for **absorption** and
  **exhaustion**.
- **Time-based volume** on the daily for HTF bias.
- **Moving averages** with volume.
- *Not used*: FVGs, "vu's" indicators (Gabe's note: "vu" / "vus" is a
  person — ignore those references).

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
- Use only as a destination / mean-reversion magnet.

### LVN — Low Volume Node
- Valley between two HVNs. Aggressive movement printed it.
- **Reject when**: aligned with HTF trend (long at LVN below in uptrend,
  short at LVN above in downtrend), OR at trend exhaustion (volume
  spike + exhaustion candles → reversal).
- **Runs through when**: traded against sentiment / trend. Low volume
  means no orders to defend → fast continuation.

### Ledge
- Flat shelf at the **edge** of an HVN where volume sharply drops to a
  low-volume zone.
- Same support/resistance logic as LVNs: traders were unwilling to
  transact past it; on return that behavior tends to repeat.
- **Same trend-alignment rule** — bearish ledge in a bullish HTF gets
  run through.

> "Make sure with LVNs and ledges to make sure they align with the trend
> or the overall market structure. If the momentum is not on your side
> they can be ran through very easily since they are areas of low
> volume." — jwill

## Daily bias (HTF)

Built from time-based (regular) volume on the daily chart.

- **Volume spike** = peak panic / peak fomo → temporary top/bottom.
  - Spike on a green-bar rally → bearish reversal watch.
  - Spike on a red-bar drop → bullish reversal watch.
- **Decreasing volume + steady trend** = healthy trend (takes few
  buyers/sellers to keep moving). Trend continuation bias.
- Pair with moving averages.

## Setup process (jwill's flow)

1. Set HTF bias from daily TBV + MAs (BULL / BEAR / NEUTRAL).
2. Mark levels from VP: Ledges and LVNs aligned with the bias.
3. **Wait at the level**:
   - If footprint triggers (absorption / exhaustion) are already
     printing into the level → **limit in**.
   - Otherwise → **wait for trigger at the level**, then enter.
4. Avoid HVNs entirely.

## Grading (rules the indicator uses)

Six confluences. Score 0–6 → grade.

| # | Confluence | Pass condition |
|---|---|---|
| 1 | HTF bias defined | Daily bias is BULL or BEAR (not NEUTRAL) |
| 2 | At a level | Within ATR×proximity of an LVN or Ledge |
| 3 | Level aligned with bias | Long: level ≤ price in bull bias. Short: level ≥ price in bear bias |
| 4 | Not in HVN | Current price's bin < HVN threshold |
| 5 | Volume regime favorable | Healthy-trend volume slope OR exhaustion reversal pattern |
| 6 | MA alignment | Fast MA on bias side of slow MA |

- **A+** = 6/6 → take it (still confirm footprint trigger).
- **A**  = 5/6 → take it if footprint trigger is clean.
- **B+** = 4/6 → consider, smaller size.
- **B**  = 2–3/6 → skip unless footprint is very strong.
- **C**  = 0–1/6 → skip.

The footprint trigger (absorption / exhaustion on the 1m) is the **final
gate** and is **not** computed by the Pine indicator — TradingView
doesn't have order-flow data on retail tier. Mark the trigger pass/fail
in the journal so we can measure its lift.

## Risk

- Stop = ATR × `slMult` (default 1.0) on the far side of the level.
- Target = ATR × `tpMult` (default 2.5) → minimum 2.5R.
- Points and R:R are computed in the dashboard.
- If the level itself is closer than the ATR stop, the structural stop
  beyond the level wins — adjust manually.

## What we are explicitly NOT doing

- No FVGs.
- No counter-trend Ledge/LVN trades.
- No HVN entries.
- No trades without a defined HTF bias.
- No trades without a footprint trigger (or a clean limit fill into the
  level when triggers were already printing).
