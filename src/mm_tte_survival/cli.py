from __future__ import annotations

import argparse
from pathlib import Path
import json

from .audit import audit_inputs, write_markdown_audit
from .config import load_config
from .demo import make_demo_data
from .experiments import run_experiments


def main(argv=None):
    parser = argparse.ArgumentParser(description="MM cytogenetic subtype TTE modeling")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_demo = sub.add_parser("make-demo-data")
    p_demo.add_argument("--out", default="data/demo")
    p_demo.add_argument("--n", type=int, default=260)
    p_demo.add_argument("--p", type=int, default=120)
    p_demo.add_argument("--seed", type=int, default=42)

    p_audit = sub.add_parser("audit-data")
    p_audit.add_argument("--clinical", required=True)
    p_audit.add_argument("--cytogenetics")
    p_audit.add_argument("--omics")
    p_audit.add_argument("--out", default="outputs/audit_report.json")
    p_audit.add_argument("--id-col", default="patient_id")
    p_audit.add_argument("--time-col", default="time_months")
    p_audit.add_argument("--event-col", default="event")

    p_run = sub.add_parser("run-experiments")
    p_run.add_argument("--config", default="configs/default.yaml")

    p_res = sub.add_parser(
        "residual-report",
        help="Residual-risk decomposition + matched ablation + claim/usefulness reports",
    )
    p_res.add_argument("--config", default="configs/real_training.yaml")

    p_main = sub.add_parser("run", help="Run the full pipeline via main.run_pipeline")
    p_main.add_argument("--config", default="configs/experiments/experiment0_open_gdc_os.yaml")

    p_ext = sub.add_parser("external-validate",
                           help="Train on one cohort, evaluate the frozen model on an external cohort")
    p_ext.add_argument("--train-config", required=True)
    p_ext.add_argument("--external-config", required=True)

    p_bench = sub.add_parser("benchmark-mmsygnal",
                             help="Score the cohort with the external mmSYGNAL models (research benchmark)")
    p_bench.add_argument("--config", default="configs/experiments/experiment0_open_gdc_os.yaml")
    p_bench.add_argument("--benchmark-config", default="configs/benchmarks/mmsygnal.yaml")

    args = parser.parse_args(argv)
    if args.cmd == "make-demo-data":
        make_demo_data(args.out, args.n, args.p, args.seed)
        print(f"Wrote demo data to {args.out}")
    elif args.cmd == "audit-data":
        report = audit_inputs(args.clinical, args.cytogenetics, args.omics, args.out, args.id_col, args.time_col, args.event_col)
        md = Path(args.out).with_suffix(".md")
        write_markdown_audit(report, md)
        print(json.dumps(report["usable_for"], indent=2))
        print(f"Wrote {args.out} and {md}")
    elif args.cmd == "run-experiments":
        cfg = load_config(args.config)
        res = run_experiments(cfg)
        print(res["leaderboard"].to_string(index=False))
        print(f"Outputs: {res['outdir']}")
    elif args.cmd == "residual-report":
        from .residual import run_residual_report
        cfg = load_config(args.config)
        res = run_residual_report(cfg)
        print(f"\nOutputs: {res['outdir']}")
    elif args.cmd == "run":
        from .main import run_pipeline
        run_pipeline(args.config)
    elif args.cmd == "external-validate":
        from .evaluation.external import run_external_validation
        run_external_validation(args.train_config, args.external_config)
    elif args.cmd == "benchmark-mmsygnal":
        from .benchmarks.mmsygnal import run_mmsygnal_benchmark
        cfg = load_config(args.config)
        bench_cfg = load_config(args.benchmark_config)
        run_mmsygnal_benchmark(cfg, bench_cfg)


if __name__ == "__main__":
    main()
