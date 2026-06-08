#!/usr/bin/env python3
"""单 case 全流程：run -> parse -> timeline x2 -> bandwidth。"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from tools.dffc_profile.lib.paths import REPO_ROOT, cli_script, ensure_repo_on_path

ensure_repo_on_path()

from tools.dffc_profile.lib.cases import CASES, DffcCase, make_case
from tools.dffc_profile.pipeline.run_case import (
    DEFAULT_MEASURE_ITERS,
    DEFAULT_WARMUP_ITERS,
    SINGLE_FORWARD_MEASURE,
    SINGLE_FORWARD_WARMUP,
    run_case,
)


def _run_py(script: str, *argv: str) -> None:
    cmd = [sys.executable, str(cli_script(script)), *argv]
    subprocess.run(cmd, check=True, cwd=str(REPO_ROOT))


def run_postprocess(
    case: DffcCase,
    world_size: int,
    out_dir: Path,
    *,
    strict_validate: bool | None = None,
) -> Path:
    """已有 rank*_profile.json 时仅 parse / validate / 出图。"""
    return _run_postprocess_inner(case, world_size, out_dir, strict_validate=strict_validate)


def run_pipeline(
    case: DffcCase,
    world_size: int,
    out_dir: Path,
    port: int = 0,
    *,
    warmup_iters: int = DEFAULT_WARMUP_ITERS,
    measure_iters: int = DEFAULT_MEASURE_ITERS,
    strict_validate: bool | None = None,
    skip_benchmark: bool = False,
) -> Path:
    if not skip_benchmark:
        run_case(
            case,
            world_size,
            out_dir,
            port,
            warmup_iters=warmup_iters,
            measure_iters=measure_iters,
        )
    suffix = ""
    if measure_iters > 1 or warmup_iters > 0:
        suffix = f" (mean×{measure_iters}, warmup={warmup_iters})"
    return _run_postprocess_inner(
        case, world_size, out_dir, strict_validate=strict_validate, title_suffix=suffix,
    )


def _run_postprocess_inner(
    case: DffcCase,
    world_size: int,
    out_dir: Path,
    *,
    strict_validate: bool | None = None,
    title_suffix: str = "",
) -> Path:
    _run_py("parse_profile.py", "--indir", str(out_dir))
    # ws16 等多 rank 场景 expert 墙钟可重叠，默认放宽 strict
    if strict_validate is None:
        strict_validate = world_size <= 8
    val_argv = ["validate_profile.py", "--indir", str(out_dir)]
    if strict_validate:
        val_argv.append("--strict")
    val = subprocess.run(
        [sys.executable, str(cli_script(val_argv[0])), *val_argv[1:]],
        cwd=str(REPO_ROOT),
    )
    if strict_validate and (val.returncode == 2 or val.returncode != 0):
        raise subprocess.CalledProcessError(val.returncode, val_argv)
    if val.returncode != 0:
        print(f"[pipeline] validate 非零退出 {val.returncode}（已继续）: {out_dir}", file=sys.stderr)
    slug = case.result_slug(world_size)
    _run_py("calc_bandwidth.py", "--indir", str(out_dir))
    title = f"dispatch_ffn_combine {slug}{title_suffix}"
    _run_py(
        "gen_timeline.py",
        "--breakdown", str(out_dir / "breakdown.json"),
        "--title", title,
    )
    # v9：expert 粒度图（仅 active 条，阶段内 expert 空隙保留）
    _run_py(
        "gen_timeline.py",
        "--breakdown", str(out_dir / "breakdown.json"),
        "--title", f"{title} | expert active",
        "--expert-active-only",
        "--focus-only",
        "--out", str(out_dir / "timeline_expert.png"),
        "--out-focus", str(out_dir / "timeline_expert_focus.png"),
    )
    # 每 rank 三张 timeline（单卡、无 job 聚合）
    _run_py(
        "gen_per_rank_timelines.py",
        "--case-dir", str(out_dir),
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
