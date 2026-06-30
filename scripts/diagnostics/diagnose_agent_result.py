#!/usr/bin/env python
"""Diagnose whether a real-data run supports the intended relapse/PFS claim.

NOT part of the scientific record (read-only diagnostic; writes no artifact).

Usage:
  python scripts/diagnostics/diagnose_agent_result.py \
    --leaderboard outputs/real_run/leaderboard.csv \
    --manifest outputs/real_run/run_manifest.json \
    --endpoint open_gdc_os
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import pandas as pd


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--leaderboard", required=True)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--endpoint", default="unknown")
    ap.add_argument("--min-test-events", type=int, default=50)
    args = ap.parse_args()

    lb = pd.read_csv(args.leaderboard)
    manifest = json.loads(Path(args.manifest).read_text())
    events = int(manifest.get("events_test", 0))
    best = lb.sort_values("test_cindex", ascending=False).iloc[0]

    print("Endpoint:", args.endpoint)
    print("Best model:", best["model"], "test C-index=", round(float(best["test_cindex"]), 3))
    print("Test events:", events)

    if args.endpoint.lower() in {"open_gdc_os", "os", "overall_survival"}:
        print("DIAGNOSIS: This run supports OS-only conclusions, not relapse/PFS conclusions.")
    if events < args.min_test_events:
        print("DIAGNOSIS: Underpowered model comparison; use event-stratified CV or a larger endpoint cohort.")

    clinical = lb[lb["model"].astype(str).str.contains("clinical", case=False, na=False)]
    if not clinical.empty:
        clinical_best = clinical["test_cindex"].max()
        if float(best["test_cindex"]) <= float(clinical_best) + 0.005:
            print("DIAGNOSIS: Integrated model did not beat clinical-only by a meaningful margin in this run.")

    opsd = lb[lb["model"].astype(str).str.startswith("opsd", na=False)]
    base = lb[~lb["model"].astype(str).str.startswith("opsd", na=False)]
    if not opsd.empty and not base.empty and opsd["test_cindex"].max() + 0.02 < base["test_cindex"].max():
        print("DIAGNOSIS: OPSD is hurting; use warm-up/ramp or disable OPSD for this endpoint.")


if __name__ == "__main__":
    main()
