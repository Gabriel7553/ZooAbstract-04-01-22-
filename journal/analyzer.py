#!/usr/bin/env python3
"""
Trade journal analyzer.

Usage:
    python3 journal/analyzer.py journal/trade_log_template.csv

Reports:
- Overall win rate, avg R, expectancy
- Win rate by grade (A+ / A / B+ / B / C)
- Confluence lift: win-rate of trades where each Y/N flag was Y vs N
- Win rate by level type, by side, by session
- Footprint-trigger lift (the gate Pine can't compute)

Stdlib only — no pandas dependency.
"""
import csv
import sys
from collections import defaultdict
from statistics import mean


def is_yes(v):
    return str(v).strip().upper() in {"Y", "YES", "TRUE", "1"}


def to_float(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def load(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def winrate(rows):
    if not rows:
        return 0.0, 0
    wins = sum(1 for r in rows if str(r.get("result", "")).strip().upper() == "WIN")
    return wins / len(rows), len(rows)


def avg_rr(rows):
    rr = [to_float(r.get("rr_realized")) for r in rows]
    rr = [x for x in rr if x is not None]
    return mean(rr) if rr else 0.0


def expectancy(rows):
    """Average R per trade — positive means profitable."""
    out = []
    for r in rows:
        rr = to_float(r.get("rr_realized"))
        result = str(r.get("result", "")).strip().upper()
        if rr is None:
            continue
        sign = 1 if result == "WIN" else -1 if result == "LOSS" else 0
        out.append(sign * abs(rr))
    return mean(out) if out else 0.0


def group_by(rows, key):
    g = defaultdict(list)
    for r in rows:
        g[str(r.get(key, "")).strip()].append(r)
    return g


def fmt_pct(p):
    return f"{p*100:5.1f}%"


def section(title):
    print(f"\n{'=' * 64}\n{title}\n{'=' * 64}")


def report_breakdown(label, groups):
    print(f"\n{label}")
    print(f"  {'bucket':<18} {'n':>4}  {'WR':>6}  {'avgR':>6}  {'exp':>6}")
    for k, rs in sorted(groups.items(), key=lambda x: -len(x[1])):
        if not k:
            continue
        wr, n = winrate(rs)
        print(f"  {k:<18} {n:>4}  {fmt_pct(wr):>6}  {avg_rr(rs):>6.2f}  {expectancy(rs):>6.2f}")


def confluence_lift(rows):
    flags = [
        ("level_aligned",     "Level aligned w/ bias"),
        ("ma_aligned",        "MA aligned"),
        ("footprint_trigger", "Footprint trigger"),
        ("htf_check",         "HTF actively checked"),
        ("in_hvn",            "In HVN (should be N)"),
    ]
    print("\nConfluence lift (WR when flag=Y vs N)")
    print(f"  {'flag':<28} {'Y n':>4} {'Y WR':>6}  {'N n':>4} {'N WR':>6}  {'lift':>6}")
    for col, label in flags:
        y = [r for r in rows if is_yes(r.get(col))]
        n = [r for r in rows if not is_yes(r.get(col)) and str(r.get(col, "")).strip()]
        ywr, yn = winrate(y)
        nwr, nn = winrate(n)
        lift = ywr - nwr
        print(f"  {label:<28} {yn:>4} {fmt_pct(ywr):>6}  {nn:>4} {fmt_pct(nwr):>6}  {lift*100:>+5.1f}%")


def main():
    if len(sys.argv) < 2:
        print("usage: analyzer.py <trade_log.csv>", file=sys.stderr)
        sys.exit(2)
    rows = load(sys.argv[1])
    rows = [r for r in rows if str(r.get("result", "")).strip().upper() in {"WIN", "LOSS", "BE"}]
    if not rows:
        print("No closed trades found (need result=WIN/LOSS/BE).")
        sys.exit(0)

    section(f"Overall  ({len(rows)} trades)")
    wr, n = winrate(rows)
    print(f"  Win rate    : {fmt_pct(wr)}  ({n} trades)")
    print(f"  Avg R       : {avg_rr(rows):.2f}")
    print(f"  Expectancy  : {expectancy(rows):.2f} R per trade")

    section("By grade")
    report_breakdown("grade", group_by(rows, "grade"))

    section("By dimension")
    report_breakdown("side",        group_by(rows, "side"))
    report_breakdown("level_type",  group_by(rows, "level_type"))
    report_breakdown("session",     group_by(rows, "session"))
    report_breakdown("vol_regime",  group_by(rows, "vol_regime"))
    report_breakdown("trigger_type", group_by(rows, "trigger_type"))
    report_breakdown("limit_or_trigger", group_by(rows, "limit_or_trigger"))

    section("Confluence lift")
    confluence_lift(rows)


if __name__ == "__main__":
    main()
