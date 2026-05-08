#!/usr/bin/env python3
"""
Jwill Volume Strategy — Python backtest scaffold.

Ports the Pine indicator's rules (EMAs, VP/LVN/Ledge detection, bias,
structural stop/target picker) to Python so we can backtest historical
CSVs without re-running every parameter change through paper trades.

Usage:
    python3 backtest/backtest.py data/NQ_1m_2024.csv
    python3 backtest/backtest.py data/GC_1m_2024.csv --primary-days 90 --min-rr 1.5

CSV format (TradingView export or generic):
    time,open,high,low,close,volume
    2024-01-02T09:30:00,16800.25,16812.5,16795.0,16808.75,12345
    ...
    `time` is parsed if present; otherwise rows are taken in order. Tz-naive
    is assumed to be exchange tz.

Caveats — the Python port is CLOSE but not byte-identical to Pine:
- Session H/L tracked from a fixed schedule (NY 09:30-16:00 ET, etc.) — if
  your CSV is in a different tz, pass --tz-shift hours.
- VWAP is anchored to NY session for NQ, daily reset for GC.
- We don't model slippage or commissions — add them later when refining.
- Entries are simulated as a market fill on the bar AFTER the signal bar
  (no look-ahead). Stops/targets fill on intrabar high/low touches.

Stdlib only — no pandas/numpy required.
"""
from __future__ import annotations

import argparse
import csv
import math
import sys
from collections import deque, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, time, timedelta, timezone
from statistics import mean


# ============================================================================
#  Bar + I/O
# ============================================================================
@dataclass
class Bar:
    t: datetime | None
    o: float
    h: float
    l: float
    c: float
    v: float


def load_csv(path: str) -> list[Bar]:
    bars: list[Bar] = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                t_raw = row.get("time") or row.get("Time") or row.get("date") or row.get("Date")
                t = None
                if t_raw:
                    # Unix epoch integer (TradingView "time" column)
                    try:
                        ts = int(float(t_raw))
                        t = datetime.fromtimestamp(ts)
                    except (ValueError, OSError):
                        t_clean = t_raw.replace("Z", "+00:00")
                        try:
                            t = datetime.fromisoformat(t_clean)
                        except ValueError:
                            try:
                                t = datetime.strptime(t_raw, "%Y-%m-%d %H:%M:%S")
                            except ValueError:
                                t = None
                # TradingView exports volume as last column, sometimes capitalized
                vol_raw = (row.get("Volume") or row.get("volume") or "0").strip()
                bars.append(Bar(
                    t=t,
                    o=float(row["open"]),
                    h=float(row["high"]),
                    l=float(row["low"]),
                    c=float(row["close"]),
                    v=float(vol_raw) if vol_raw else 0.0,
                ))
            except (KeyError, ValueError):
                continue
    return bars


# ============================================================================
#  Indicators (rolling — stdlib only)
# ============================================================================
class EMA:
    def __init__(self, length: int):
        self.length = length
        self.alpha = 2 / (length + 1)
        self.value: float | None = None

    def push(self, x: float) -> float | None:
        if self.value is None:
            self.value = x
        else:
            self.value = self.alpha * x + (1 - self.alpha) * self.value
        return self.value


class ATR:
    """Wilder ATR over `length`."""
    def __init__(self, length: int):
        self.length = length
        self.prev_close: float | None = None
        self.value: float | None = None
        self.count = 0

    def push(self, h: float, l: float, c: float) -> float | None:
        if self.prev_close is None:
            tr = h - l
        else:
            tr = max(h - l, abs(h - self.prev_close), abs(l - self.prev_close))
        self.prev_close = c
        if self.value is None:
            self.value = tr
        else:
            self.value = (self.value * (self.length - 1) + tr) / self.length
        self.count += 1
        return self.value if self.count >= self.length else None


class RollingMean:
    def __init__(self, length: int):
        self.length = length
        self.buf: deque[float] = deque(maxlen=length)
        self.s = 0.0

    def push(self, x: float) -> float | None:
        if len(self.buf) == self.length:
            self.s -= self.buf[0]
        self.buf.append(x)
        self.s += x
        return self.s / len(self.buf) if len(self.buf) == self.length else None


# ============================================================================
#  Volume Profile builder
# ============================================================================
def build_profile(bars: list[Bar], end_idx: int, lookback_bars: int,
                  nbins: int) -> dict:
    """Build VP over bars[end_idx - lookback_bars + 1 : end_idx + 1]."""
    start = max(0, end_idx - lookback_bars + 1)
    window = bars[start:end_idx + 1]
    if not window:
        return {"poc": None, "lvns": [], "hvns": [], "ledges": [], "top": None, "bot": None, "bins": []}
    hi = max(b.h for b in window)
    lo = min(b.l for b in window)
    if hi <= lo:
        return {"poc": None, "lvns": [], "hvns": [], "ledges": [], "top": hi, "bot": lo, "bins": []}
    bs = (hi - lo) / nbins
    bins = [0.0] * nbins
    bin_price = [lo + (i + 0.5) * bs for i in range(nbins)]
    for b in window:
        if b.v <= 0 or b.h < b.l:
            continue
        sB = max(0, min(nbins - 1, math.floor((b.l - lo) / bs)))
        eB = max(0, min(nbins - 1, math.floor((b.h - lo) / bs)))
        spread = eB - sB + 1
        per = b.v / spread
        for j in range(sB, eB + 1):
            bins[j] += per
    poc_vol = max(bins)
    poc_idx = bins.index(poc_vol)
    poc_price = bin_price[poc_idx]
    return {
        "poc": poc_price,
        "poc_vol": poc_vol,
        "bins": bins,
        "bin_price": bin_price,
        "top": hi,
        "bot": lo,
        "lvns": [bin_price[i] for i, v in enumerate(bins) if poc_vol > 0 and 0.02 < v / poc_vol <= 0.20],
        "hvns": [bin_price[i] for i, v in enumerate(bins) if poc_vol > 0 and v / poc_vol >= 0.80],
        "ledges": [bin_price[i] for i in range(1, nbins - 1)
                   if poc_vol > 0 and bins[i] / poc_vol >= 0.80
                   and (bins[i + 1] / poc_vol <= 0.20 or bins[i - 1] / poc_vol <= 0.20)],
    }


# ============================================================================
#  Session H/L tracker (uses local time of bar.t — assumes exchange tz)
# ============================================================================
NY_OPEN = time(9, 30)
NY_CLOSE = time(16, 0)
ASIA_OPEN = time(17, 0)
ASIA_CLOSE = time(3, 0)
LON_OPEN = time(3, 0)
LON_CLOSE = time(8, 0)


def in_session(t: time, open_t: time, close_t: time) -> bool:
    if open_t < close_t:
        return open_t <= t < close_t
    return t >= open_t or t < close_t


@dataclass
class SessionLevels:
    asia_h: float | None = None
    asia_l: float | None = None
    lon_h: float | None = None
    lon_l: float | None = None
    ny_h: float | None = None
    ny_l: float | None = None
    pdh: float | None = None
    pdl: float | None = None
    cur_day: int = -1
    today_h: float = -math.inf
    today_l: float = math.inf
    last_bar_in_ny: bool = False

    def update(self, bar: Bar):
        if bar.t is None:
            return False
        # day rollover
        doy = bar.t.toordinal()
        if self.cur_day != doy:
            if self.cur_day != -1:
                self.pdh = self.today_h if self.today_h > -math.inf else self.pdh
                self.pdl = self.today_l if self.today_l < math.inf else self.pdl
            self.cur_day = doy
            self.today_h = bar.h
            self.today_l = bar.l
            self.asia_h = self.asia_l = None
            self.lon_h = self.lon_l = None
            self.ny_h = self.ny_l = None
        else:
            self.today_h = max(self.today_h, bar.h)
            self.today_l = min(self.today_l, bar.l)
        tod = bar.t.time()
        if in_session(tod, ASIA_OPEN, ASIA_CLOSE):
            self.asia_h = bar.h if self.asia_h is None else max(self.asia_h, bar.h)
            self.asia_l = bar.l if self.asia_l is None else min(self.asia_l, bar.l)
        if in_session(tod, LON_OPEN, LON_CLOSE):
            self.lon_h = bar.h if self.lon_h is None else max(self.lon_h, bar.h)
            self.lon_l = bar.l if self.lon_l is None else min(self.lon_l, bar.l)
        in_ny_now = in_session(tod, NY_OPEN, NY_CLOSE)
        if in_ny_now:
            self.ny_h = bar.h if self.ny_h is None else max(self.ny_h, bar.h)
            self.ny_l = bar.l if self.ny_l is None else min(self.ny_l, bar.l)
        anchor = in_ny_now and not self.last_bar_in_ny
        self.last_bar_in_ny = in_ny_now
        return anchor


# ============================================================================
#  Anchored Session VWAP (resets on anchor)
# ============================================================================
class SessionVWAP:
    def __init__(self):
        self.pv = 0.0
        self.v = 0.0
        self.value: float | None = None

    def reset(self):
        self.pv = 0.0
        self.v = 0.0
        self.value = None

    def push(self, h: float, l: float, c: float, v: float, anchor: bool):
        if anchor:
            self.reset()
        typ = (h + l + c) / 3
        self.pv += typ * v
        self.v += v
        self.value = self.pv / self.v if self.v > 0 else None
        return self.value


# ============================================================================
#  Backtester
# ============================================================================
@dataclass
class Trade:
    direction: str   # "LONG" / "SHORT"
    grade: str
    score: int
    entry_idx: int
    entry: float
    stop: float
    target: float
    target_reason: str
    exit_idx: int = -1
    exit: float = 0.0
    result: str = ""  # WIN / LOSS / BE
    rr_planned: float = 0.0
    rr_realized: float = 0.0


def run(bars: list[Bar], cfg) -> list[Trade]:
    ema1, ema2, ema3, ema4 = EMA(9), EMA(21), EMA(50), EMA(200)
    atr = ATR(cfg.atr_len)
    vol_avg = RollingMean(cfg.vol_avg_len)
    sessions = SessionLevels()
    vwap = SessionVWAP()
    trades: list[Trade] = []
    open_trade: Trade | None = None

    is_nq = cfg.symbol_hint.upper().startswith("NQ") or "NQ" in cfg.symbol_hint.upper()

    bars_per_day = cfg.bars_per_day
    primary_lb = min(5000, cfg.primary_days * bars_per_day)

    for i, b in enumerate(bars):
        anchor = sessions.update(b)
        if not is_nq and b.t and b.t.toordinal() != sessions.cur_day:
            # daily anchor for non-NQ symbols
            anchor = True

        e1 = ema1.push(b.c)
        e2 = ema2.push(b.c)
        e3 = ema3.push(b.c)
        e4 = ema4.push(b.c)
        a = atr.push(b.h, b.l, b.c)
        va = vol_avg.push(b.v)
        vw = vwap.push(b.h, b.l, b.c, b.v, anchor)

        # close-out check (intrabar fills)
        if open_trade is not None:
            if open_trade.direction == "LONG":
                if b.l <= open_trade.stop:
                    open_trade.exit_idx = i
                    open_trade.exit = open_trade.stop
                    open_trade.result = "LOSS"
                elif b.h >= open_trade.target:
                    open_trade.exit_idx = i
                    open_trade.exit = open_trade.target
                    open_trade.result = "WIN"
            else:
                if b.h >= open_trade.stop:
                    open_trade.exit_idx = i
                    open_trade.exit = open_trade.stop
                    open_trade.result = "LOSS"
                elif b.l <= open_trade.target:
                    open_trade.exit_idx = i
                    open_trade.exit = open_trade.target
                    open_trade.result = "WIN"
            if open_trade.result:
                risk = abs(open_trade.entry - open_trade.stop)
                reward = abs(open_trade.exit - open_trade.entry)
                open_trade.rr_realized = reward / risk if risk > 0 else 0
                if open_trade.result == "LOSS":
                    open_trade.rr_realized = -open_trade.rr_realized
                trades.append(open_trade)
                open_trade = None

        if open_trade is not None:
            continue
        if None in (e1, e2, e3, e4) or a is None or va is None or vw is None:
            continue
        if i < primary_lb:
            continue
        # Rebuild profile on a cadence (every `profile_every` bars) to keep
        # things fast — Pine rebuilds only on last bar; we approximate.
        if i % cfg.profile_every != 0:
            continue
        prof = build_profile(bars, i, primary_lb, cfg.nbins)
        if not prof["lvns"] and not prof["ledges"]:
            continue

        stacked_up = e1 > e2 > e3 > e4
        stacked_dn = e1 < e2 < e3 < e4
        trend_up = b.c > e2 > e3
        trend_dn = b.c < e2 < e3
        vol_spike = b.v > va * cfg.vol_spike_mul
        # exhaustion is a 3-bar pattern; simplistic check
        exh_top = vol_spike and b.c > b.o
        exh_bot = vol_spike and b.c < b.o
        bias = 1 if trend_up and not exh_top else -1 if trend_dn and not exh_bot else 0

        # nearest level
        candidates = list(prof["lvns"]) + list(prof["ledges"])
        if not candidates:
            continue
        nearest = min(candidates, key=lambda p: abs(b.c - p))
        prox = a * cfg.prox_mul
        at_level = abs(b.c - nearest) <= prox

        # in-HVN check
        bs_inner = (prof["top"] - prof["bot"]) / cfg.nbins
        if bs_inner > 0 and prof["poc_vol"] > 0:
            idx_now = max(0, min(cfg.nbins - 1, math.floor((b.c - prof["bot"]) / bs_inner)))
            in_hvn = prof["bins"][idx_now] / prof["poc_vol"] >= 0.80
        else:
            in_hvn = False

        long_setup = bias == 1 and at_level and not in_hvn and nearest <= b.c
        short_setup = bias == -1 and at_level and not in_hvn and nearest >= b.c

        c1 = bias != 0
        c2 = at_level
        c3 = long_setup or short_setup
        c4 = not in_hvn
        price_slope = b.c - bars[max(0, i - 10)].c if i >= 10 else 0.0
        healthy_up = price_slope > 0
        healthy_dn = price_slope < 0
        c5 = (bias == 1 and (healthy_up or exh_bot)) or (bias == -1 and (healthy_dn or exh_top))
        c6 = (bias == 1 and stacked_up) or (bias == -1 and stacked_dn)
        c7 = (bias == 1 and b.c > vw) or (bias == -1 and b.c < vw)
        score = sum([c1, c2, c3, c4, c5, c6, c7])
        total = 7
        grade = "A+" if score >= total else "A" if score == total - 1 else "B+" if score == total - 2 else "B" if score >= 2 else "C"

        if grade not in cfg.allowed_grades:
            continue
        if not (long_setup or short_setup):
            continue

        # next bar fill
        if i + 1 >= len(bars):
            break
        fill = bars[i + 1].o
        if long_setup:
            stop = nearest - a * cfg.sl_buf_mul
            target, reason = pick_target(fill, abs(fill - stop), True, sessions, prof,
                                          cfg.min_rr)
            if target is None:
                target = fill + a * cfg.fallback_tp
                reason = "ATR fallback"
            direction = "LONG"
        else:
            stop = nearest + a * cfg.sl_buf_mul
            target, reason = pick_target(fill, abs(fill - stop), False, sessions, prof,
                                          cfg.min_rr)
            if target is None:
                target = fill - a * cfg.fallback_tp
                reason = "ATR fallback"
            direction = "SHORT"
        risk = abs(fill - stop)
        rr = abs(target - fill) / risk if risk > 0 else 0
        open_trade = Trade(direction=direction, grade=grade, score=score,
                           entry_idx=i + 1, entry=fill, stop=stop,
                           target=target, target_reason=reason, rr_planned=rr)
    return trades


def pick_target(entry: float, risk: float, is_long: bool,
                sess: SessionLevels, prof: dict, min_rr: float):
    cands: list[tuple[float, str]] = []
    if is_long:
        for v, n in [(sess.ny_h, "NY HoD"), (sess.lon_h, "Lon HoD"),
                     (sess.asia_h, "Asia HoD"), (sess.pdh, "PDH")]:
            if v is not None and v > entry:
                cands.append((v, n))
        for p in prof["lvns"]:
            if p > entry:
                cands.append((p, "LVN above"))
    else:
        for v, n in [(sess.ny_l, "NY LoD"), (sess.lon_l, "Lon LoD"),
                     (sess.asia_l, "Asia LoD"), (sess.pdl, "PDL")]:
            if v is not None and v < entry:
                cands.append((v, n))
        for p in prof["lvns"]:
            if p < entry:
                cands.append((p, "LVN below"))
    best = None
    best_d = math.inf
    for p, n in cands:
        rr = abs(p - entry) / risk if risk > 0 else 0
        if rr >= min_rr:
            d = abs(p - entry)
            if d < best_d:
                best_d = d
                best = (p, n)
    if best is None:
        return None, ""
    return best


# ============================================================================
#  Reporting
# ============================================================================
def report(trades: list[Trade]):
    if not trades:
        print("No trades.")
        return
    n = len(trades)
    wins = sum(1 for t in trades if t.result == "WIN")
    losses = sum(1 for t in trades if t.result == "LOSS")
    open_t = sum(1 for t in trades if not t.result)
    closed = n - open_t
    wr = wins / closed if closed else 0
    avg_r = mean(t.rr_realized for t in trades if t.result) if closed else 0
    expectancy = mean(t.rr_realized for t in trades if t.result) if closed else 0
    print("=" * 64)
    print(f"Total signals : {n}")
    print(f"Closed        : {closed}  (open at end-of-data: {open_t})")
    print(f"Wins / Losses : {wins} / {losses}")
    print(f"Win rate      : {wr*100:.1f}%")
    print(f"Avg R         : {avg_r:.2f}")
    print(f"Expectancy    : {expectancy:.2f} R / trade")
    print()
    by_grade: dict[str, list[Trade]] = defaultdict(list)
    for t in trades:
        by_grade[t.grade].append(t)
    print(f"{'grade':<6} {'n':>4} {'WR':>6} {'avgR':>6}")
    for g in ("A+", "A", "B+", "B", "C"):
        rs = [t for t in by_grade.get(g, []) if t.result]
        if not rs:
            continue
        w = sum(1 for t in rs if t.result == "WIN") / len(rs)
        a = mean(t.rr_realized for t in rs)
        print(f"{g:<6} {len(rs):>4} {w*100:>5.1f}% {a:>6.2f}")
    print()
    print(f"{'dir':<6} {'n':>4} {'WR':>6} {'avgR':>6}")
    for d in ("LONG", "SHORT"):
        rs = [t for t in trades if t.direction == d and t.result]
        if not rs:
            continue
        w = sum(1 for t in rs if t.result == "WIN") / len(rs)
        a = mean(t.rr_realized for t in rs)
        print(f"{d:<6} {len(rs):>4} {w*100:>5.1f}% {a:>6.2f}")
    print()
    by_reason: dict[str, list[Trade]] = defaultdict(list)
    for t in trades:
        if t.result:
            by_reason[t.target_reason].append(t)
    print("Target-reason breakdown")
    for r, rs in sorted(by_reason.items(), key=lambda x: -len(x[1])):
        if not rs:
            continue
        w = sum(1 for t in rs if t.result == "WIN") / len(rs)
        a = mean(t.rr_realized for t in rs)
        print(f"  {r:<18} n={len(rs):>4}  WR={w*100:>5.1f}%  avgR={a:>5.2f}")


# ============================================================================
#  CLI
# ============================================================================
@dataclass
class Cfg:
    primary_days: int = 90
    bars_per_day: int = 1440      # 1m default; auto-detect would be nicer
    nbins: int = 60
    atr_len: int = 14
    vol_avg_len: int = 20
    vol_spike_mul: float = 1.8
    prox_mul: float = 0.30
    sl_buf_mul: float = 0.25
    min_rr: float = 1.5
    fallback_tp: float = 2.5
    profile_every: int = 5
    allowed_grades: tuple = ("A+", "A")
    symbol_hint: str = "NQ"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("--primary-days", type=int, default=90)
    ap.add_argument("--bars-per-day", type=int, default=1440)
    ap.add_argument("--min-rr", type=float, default=1.5)
    ap.add_argument("--prox-mul", type=float, default=0.30)
    ap.add_argument("--sl-buf-mul", type=float, default=0.25)
    ap.add_argument("--symbol", default="NQ")
    ap.add_argument("--grades", default="A+,A",
                    help="comma-separated grades to take (default: A+,A)")
    ap.add_argument("--profile-every", type=int, default=5,
                    help="rebuild profile every N bars (perf trade-off)")
    args = ap.parse_args()
    cfg = Cfg(primary_days=args.primary_days, bars_per_day=args.bars_per_day,
              min_rr=args.min_rr, prox_mul=args.prox_mul,
              sl_buf_mul=args.sl_buf_mul, symbol_hint=args.symbol,
              allowed_grades=tuple(g.strip() for g in args.grades.split(",")),
              profile_every=args.profile_every)
    bars = load_csv(args.csv)
    if len(bars) < cfg.primary_days * cfg.bars_per_day:
        print(f"WARNING: only {len(bars)} bars but lookback wants "
              f"{cfg.primary_days * cfg.bars_per_day}. Stats will be thin.",
              file=sys.stderr)
    trades = run(bars, cfg)
    report(trades)


if __name__ == "__main__":
    main()
