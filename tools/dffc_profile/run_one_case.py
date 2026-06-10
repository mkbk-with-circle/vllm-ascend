#!/usr/bin/env python3
"""单 case 全流程：run -> parse -> timeline x2 -> bandwidth。"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

_TOOLS_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _TOOLS_DIR.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from tools.dffc_profile.cases import CASES, DffcCase, make_case
from tools.dffc_profile.run_case import (
    DEFAULT_MEASURE_ITERS,
    DEFAULT_WARMUP_ITERS,
    SINGLE_FORWARD_MEASURE,
    SINGLE_FORWARD_WARMUP,
    run_case,
)


def _run_py(script: str, *argv: str) -> None:
    cmd = [sys.executable, str(_TOOLS_DIR / script), *argv]
    subprocess.run(cmd, check=True, cwd=str(_REPO_ROOT))


def run_pipeline(
    case: DffcCase,
    world_size: int,
    out_dir: Path,
    port: int = 0,
    *,
    warmup_iters: int = DEFAULT_WARMUP_ITERS,
    measure_iters: int = DEFAULT_MEASURE_ITERS,
) -> Path:
    run_case(
        case,
        world_size,
        out_dir,
        port,
        warmup_iters=warmup_iters,
        measure_iters=measure_iters,
    )
    _run_py("parse_profile.py", "--indir", str(out_dir))
    _run_py("validate_profile.py", "--indir", str(out_dir), "--strict")
    slug = case.result_slug(world_size)
    _run_py("calc_bandwidth.py", "--indir", str(out_dir))
    title = f"dispatch_ffn_combine {slug}"
    if measure_iters > 1 or warmup_iters > 0:
        title += f" (mean×{measure_iters}, warmup={warmup_iters})"
    _run_py(
        "gen_timeline.py",
        "--breakdown", str(out_dir / "breakdown.json"),
        "--title", title,
    )
    return out_dir


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", default=None, choices=list(CASES.keys()))
    parser.add_argument("--name", default=None)
    parser.add_argument("--m", type=int, default=None)
    parser.add_argument("--k", type=int, default=None)
    parser.add_argument("--n", type=int, default=None)
    parser.add_argument("--e", type=int, default=2)
    parser.add_argument("--topk", type=int, default=8)
    parser.add_argument("--max-output-size", type=int, default=None)
    parser.add_argument("--world-size", type=int, default=8)
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--warmup", type=int, default=DEFAULT_WARMUP_ITERS)
    parser.add_argument("--measure-iters", type=int, default=DEFAULT_MEASURE_ITERS)
    parser.add_argument("--single-forward", action="store_true", help="单次 forward baseline")
    args = parser.parse_args()

    if args.single_forward:
        args.warmup = SINGLE_FORWARD_WARMUP
        args.measure_iters = SINGLE_FORWARD_MEASURE

    if args.m is not None:
        if args.k is None:
            parser.error("--m 需配合 --k")
        case = make_case(
            name=args.name or "custom",
            m=args.m,
            k=args.k,
            n=args.n,
            e=args.e,
            topk=args.topk,
            max_output_size=args.max_output_size,
        )
    elif args.case:
        case = CASES[args.case]
    else:
        parser.error("需指定 --case 或 --m/--k")

    run_pipeline(
        case,
        args.world_size,
        args.out_dir,
        args.port,
        warmup_iters=args.warmup,
        measure_iters=args.measure_iters,
    )
    print(f"[run_one_case] done -> {args.out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
