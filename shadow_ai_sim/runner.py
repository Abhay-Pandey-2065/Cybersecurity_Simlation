import argparse
import json
import statistics as st
import sys
from pathlib import Path
from typing import Dict, List, Sequence

from .config import DEFAULT_SEEDS, SimConfig
from .detectors import METHODS
from .metrics import evaluate
from .traffic import generate_events

LABELS = {"M1": "M1 static blocklist", "M2": "M2 + catalogue", "M3": "M3 + heuristics"}


def run_seed(cfg: SimConfig, seed: int) -> Dict:
    return evaluate(generate_events(cfg, seed), cfg)


def _mean_sd(results: List[Dict], getter):
    vals = [getter(r) for r in results]
    return st.mean(vals), st.pstdev(vals)


def summarise(results: List[Dict]) -> str:
    """Human-readable summary (mean ± sd across seeds)."""
    ms = lambda f: _mean_sd(results, f)
    lines = []
    ev, sh, se, su = (ms(lambda r: r["events"]), ms(lambda r: r["shadow"]),
                      ms(lambda r: r["sens_shadow"]), ms(lambda r: r["shadow_users"]))
    lines.append(f"Runs: {len(results)} seeds")
    lines.append(f"Events per run        : {ev[0]:,.0f} (sd {ev[1]:,.0f})")
    lines.append(f"Shadow AI events      : {sh[0]:,.0f} (sd {sh[1]:,.0f})")
    lines.append(f"Sensitive shadow evts : {se[0]:,.0f} (sd {se[1]:,.0f})")
    lines.append(f"Shadow AI users       : {su[0]:,.0f} (sd {su[1]:,.1f})")
    lines.append("")
    header = f"{'Configuration':<22}{'Precision':>10}{'Recall':>9}{'F1':>8}{'Users':>7}{'Sens→DLP':>10}{'FP':>8}{'FN':>8}"
    lines.append(header)
    lines.append("-" * len(header))
    for m in METHODS:
        g = lambda k, m=m: ms(lambda r: r[m][k])[0]
        lines.append(f"{LABELS[m]:<22}{g('prec'):>10.3f}{g('rec'):>9.3f}{g('f1'):>8.3f}"
                     f"{g('users'):>7.0f}{g('sens_det'):>10.0f}{g('fp'):>8.0f}{g('fn'):>8.0f}")
    ceil = ms(lambda r: r["dlp_ceiling"])[0]
    lines.append("")
    lines.append(f"DLP ceiling (perfect discovery): {ceil:,.0f} of {se[0]:,.0f} "
                 f"sensitive prompts ({ceil / se[0]:.1%})")
    lines.append(f"DLP false positives on benign shadow prompts: "
                 f"{ms(lambda r: r['dlp_total_fp'])[0]:,.0f}")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="shadow_ai_sim",
                                description="Simulate shadow AI traffic and compare detection layers.")
    p.add_argument("--seeds", type=int, nargs="+", default=list(DEFAULT_SEEDS),
                   help="random seeds, one run each (default: %(default)s)")
    p.add_argument("--employees", type=int, default=SimConfig.employees)
    p.add_argument("--days", type=int, default=SimConfig.days)
    p.add_argument("--output-dir", type=Path, default=Path("results"),
                   help="directory for results.json (default: %(default)s)")
    p.add_argument("--quiet", action="store_true", help="do not print the summary table")
    return p


def main(argv: Sequence[str] = None) -> int:
    args = build_parser().parse_args(argv)
    cfg = SimConfig(employees=args.employees, days=args.days)
    results = []
    for seed in args.seeds:
        if not args.quiet:
            print(f"[seed {seed}] simulating {cfg.employees} employees x {cfg.days} days ...",
                  file=sys.stderr)
        results.append(run_seed(cfg, seed))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    out_file = args.output_dir / "results.json"
    out_file.write_text(json.dumps(results, indent=1))
    if not args.quiet:
        print()
        print(summarise(results))
        print(f"\nRaw per-seed results written to {out_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
