# Trade Journal Schema

One row per trade. Yes/No fields take `Y` / `N`. Numeric fields blank if
not applicable. Keep the example row as a reference, delete it before
running the analyzer if you want clean stats (analyzer also accepts it).

| Column | Type | Notes |
|---|---|---|
| `date` | YYYY-MM-DD | Date of the trade |
| `symbol` | str | e.g. ES, NQ, MES |
| `session` | str | RTH / ETH / Asia / London |
| `side` | LONG/SHORT | |
| `grade` | A+/A/B+/B/C | What the indicator showed at entry |
| `score` | 0..6 | Raw confluence score |
| `entry` | float | Fill price |
| `stop` | float | Stop price (initial) |
| `target` | float | Target price (initial) |
| `exit` | float | Actual exit price |
| `points` | float | Points captured (signed: positive = green) |
| `rr_planned` | float | Planned R:R at entry |
| `rr_realized` | float | Actual R:R at exit |
| `result` | WIN/LOSS/BE | |
| `bias` | BULL/BEAR/NEUTRAL | HTF bias at entry |
| `bias_source` | str | What confirmed it (e.g. "daily TBV + MAs") |
| `level_type` | Ledge/LVN/HVN/none | Level the trade was at |
| `level_price` | float | |
| `level_aligned` | Y/N | Did the level agree with HTF bias? |
| `in_hvn` | Y/N | Was price inside an HVN? (should be N) |
| `vol_regime` | str | healthy_up / healthy_dn / exh_top / exh_bot / normal / spike |
| `ma_aligned` | Y/N | Fast MA on bias side of slow MA |
| `footprint_trigger` | Y/N | Was there a clean trigger on the 1m? |
| `trigger_type` | absorption/exhaustion/none | |
| `htf_check` | Y/N | Did you actively check HTF before entry? |
| `limit_or_trigger` | limit/trigger | Limit fill into level or waited for trigger |
| `notes` | free text | Anything contextual |
