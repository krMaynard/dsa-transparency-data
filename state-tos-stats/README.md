# Merged US state terms-of-service statistics

`state_tos_stats.csv` is a jurisdiction-aware union of the normalized
California AB 587 and New York Stop Hiding Hate Act statistics. It connects the
two laws through their five shared statutory content categories while retaining
each filer's original metric, label, geographic scope, source file, and page.

The file is deliberately a union, not a sum. A California count must not be
used to fill a missing New York value, and different company metrics must not be
added together. Filter to one jurisdiction, company, metric, unit, grain, and
geographic scope before comparing periods.

Rebuild from the two committed normalized inputs:

```bash
python3 build.py
```

California extraction coverage and limitations are documented in
[`../ca-ab587/QUANTITATIVE.md`](../ca-ab587/QUANTITATIVE.md); New York's mapping
methodology is in [`../ny-tos-reports/NORMALIZATION.md`](../ny-tos-reports/NORMALIZATION.md).
