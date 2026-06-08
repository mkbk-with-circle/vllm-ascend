#!/usr/bin/env python3
"""重跑指定目录下 case（读 case.json，warmup+多次测量均值，原地覆盖 profile/timeline）。"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from tools.dffc_profile.lib.paths import REPO_ROOT, cli_script, ensure_repo_on_path

ensure_repo_on_path()

from tools.dffc_profile.lib.cases import DffcCase
from tools.dffc_profile.lib.profile_constants import DFFC_PROFILE_VERSION, DFFC_PROFILE_WORDS
from tools.dffc_profile.pipeline.run_case import (
    DEFAULT_MEASURE_ITERS,
    DEFAULT_WARMUP_ITERS,
    SINGLE_FORWARD_MEASURE,
    SINGLE_FORWARD_WARMUP,
)

from tools.dffc_profile.lib.sweep_grids import iter_sweep_axis_dirs
# 16 chip 机器：两组 EP=8，各用 8 个 logic chip 并行跑不同 case
DEVICE_GROUPS = (
    "0,1,2,3,4,5,6,7",
    "8,9,10,11,12,13,14,15",
)


def _needs_rerun(
    case_dir: Path,
    *,
    warmup_iters: int,
    measure_iters: int,
) -> bool:
    profiles = list(case_dir.glob("rank*_profile.json"))
    if not profiles:
        return True
    for fp in profiles:
        r = json.loads(fp.read_text(encoding="utf-8"))
        if r.get("version") != DFFC_PROFILE_VERSION:
            return True
        if "raw" not in r:
            return True
        if len(r.get("raw") or []) < DFFC_PROFILE_WORDS:
            return True
        if r.get("version", 0) >= 7 and "swiglu_w1" not in r.get("phases", {}):
            return True
        iters = r.get("profile_iters") or r.get("benchmark") or {}
        if iters.get("warmup") != warmup_iters or iters.get("measure") != measure_iters:
            return True
        g1 = r["phases"]["gmm1"]
        g2 = r["phases"]["gmm2"]
        if g1["duration_us"] < 1 or g2.get("duration_us", 0) < 1:
            return True
    return False


def collect_case_dirs(roots: list[Path], *, include_variants: bool) -> list[Path]:
    out: list[Path] = []
    for root in roots:
        for case_json in sorted(root.rglob("case.json")):
            d = case_json.parent
            if not include_variants and any(d.name.endswith(s) for s in ("_v2", "_v3", "_v4")):
                continue
            out.append(d)
    return out


def _run_one_case_job(
    *,
    case_dir: Path,
    case: DffcCase,
    case_data: dict,
    device_group: str,
    args: argparse.Namespace,
    index: int,
    total: int,
) -> tuple[Path, bool, str]:
    """在指定 chip 组上跑单个 case，返回 (case_dir, ok, msg)。"""
    print(
        f"[{index}/{total}] {case_dir} ({case.name}) devices={device_group}",
        flush=True,
    )
    cmd = [
        sys.executable,
        str(cli_script("run_one_case.py")),
        "--m", str(case.m),
        "--k", str(case.k),
        "--n", str(case_data.get("n", case.k)),
        "--e", str(case.e),
        "--topk", str(case.topk),
        "--max-output-size", str(case.max_output_size),
        "--name", case.name,
        "--world-size", str(args.world_size),
        "--out-dir", str(case_dir),
        "--warmup", str(args.warmup),
        "--measure-iters", str(args.measure_iters),
    ]
    if args.single_forward:
        cmd.append("--single-forward")
    env = os.environ.copy()
    env["ASCEND_RT_VISIBLE_DEVICES"] = device_group
    try:
        subprocess.run(
            cmd,
            check=True,
            cwd=str(REPO_ROOT),
            timeout=args.timeout_sec,
            env=env,
        )
        return case_dir, True, ""
    except subprocess.TimeoutExpired:
        return case_dir, False, f"TIMEOUT>{args.timeout_sec}s"
    except subprocess.CalledProcessError as exc:
        return case_dir, False, str(exc)


def _refresh_manifest_bandwidth(axis_dir: Path) -> None:
    """从各 case bandwidth.json 回写 manifest，供 summary 带宽图使用。"""
    manifest_path = axis_dir / "manifest.json"
    if not manifest_path.is_file():
        return
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for entry in manifest.get("cases", []):
        slug = entry.get("slug")
        if not slug:
            continue
        bw_path = axis_dir / slug / "bandwidth.json"
        if not bw_path.is_file():
            continue
        from tools.dffc_profile.lib.bandwidth import manifest_bandwidth_fields

        bw = json.loads(bw_path.read_text(encoding="utf-8"))
        entry["bandwidth"] = manifest_bandwidth_fields(bw)
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)


def _regen_axis_summaries(sweeps_root: Path) -> None:
    for axis_dir in iter_sweep_axis_dirs(sweeps_root):
        subprocess.run(
            [
                sys.executable,
                str(cli_script("plot_sweep_timelines.py")),
                "--sweep-dir",
                str(axis_dir),
            ],
            check=False,
            cwd=str(REPO_ROOT),
        )
        _refresh_manifest_bandwidth(axis_dir)
        subprocess.run(
            [
                sys.executable,
                str(cli_script("plot_sweep_bandwidth.py")),
                "--sweep-dir",
                str(axis_dir),
            ],
            check=False,
            cwd=str(REPO_ROOT),
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", action="append", default=[])
    parser.add_argument("--all", action="store_true", help="不筛选，全部重跑")
    parser.add_argument("--include-variants", action="store_true", help="含 *_v2/_v3/_v4 等目录")
    parser.add_argument("--world-size", type=int, default=8)
    parser.add_argument("--warmup", type=int, default=DEFAULT_WARMUP_ITERS)
    parser.add_argument("--measure-iters", type=int, default=DEFAULT_MEASURE_ITERS)
    parser.add_argument("--single-forward", action="store_true", help="单次 forward baseline")
    parser.add_argument(
        "--timeout-sec",
        type=int,
        default=int(os.environ.get("DFFC_CASE_TIMEOUT", "900")),
        help="单 case 超时秒数（默认 900，防 HCCL/spawn 卡死）",
    )
    parser.add_argument(
        "--parallel-jobs",
        type=int,
        default=int(os.environ.get("DFFC_PARALLEL_JOBS", "1")),
        help="并行 case 数（默认 1；16 chip 可设 2，两组 EP=8 各跑一 case）",
    )
    parser.add_argument("--skip-summaries", action="store_true")
    args = parser.parse_args()

    if args.parallel_jobs < 1:
        parser.error("--parallel-jobs 须 >= 1")
    if args.parallel_jobs > len(DEVICE_GROUPS):
        parser.error(f"--parallel-jobs 最大 {len(DEVICE_GROUPS)}（当前 {len(DEVICE_GROUPS)} 组 device）")

    if args.single_forward:
        args.warmup = SINGLE_FORWARD_WARMUP
        args.measure_iters = SINGLE_FORWARD_MEASURE

    roots = [Path(p) for p in args.root] if args.root else [
        REPO_ROOT / "results/sweeps",
        REPO_ROOT / "results/try_data",
    ]
    include_variants = args.include_variants or args.all
    case_dirs = collect_case_dirs(roots, include_variants=include_variants)
    if not args.all:
        case_dirs = [
            d for d in case_dirs
            if _needs_rerun(d, warmup_iters=args.warmup, measure_iters=args.measure_iters)
        ]

    print(
        f"[rerun] {len(case_dirs)} cases warmup={args.warmup} measure={args.measure_iters} "
        f"parallel_jobs={args.parallel_jobs}",
        flush=True,
    )
    ok, fail = 0, 0
    total = len(case_dirs)
    if args.parallel_jobs == 1:
        for i, case_dir in enumerate(case_dirs, 1):
            data = json.loads((case_dir / "case.json").read_text(encoding="utf-8"))
            case = DffcCase.from_dict(data)
            _, success, msg = _run_one_case_job(
                case_dir=case_dir,
                case=case,
                case_data=data,
                device_group=DEVICE_GROUPS[0],
                args=args,
                index=i,
                total=total,
            )
            if success:
                ok += 1
            else:
                fail += 1
                print(f"[FAIL] {case_dir}: {msg}", flush=True)
    else:
        with ThreadPoolExecutor(max_workers=args.parallel_jobs) as pool:
            futures = []
            for i, case_dir in enumerate(case_dirs, 1):
                data = json.loads((case_dir / "case.json").read_text(encoding="utf-8"))
                case = DffcCase.from_dict(data)
                group = DEVICE_GROUPS[(i - 1) % args.parallel_jobs]
                futures.append(
                    pool.submit(
                        _run_one_case_job,
                        case_dir=case_dir,
                        case=case,
                        case_data=data,
                        device_group=group,
                        args=args,
                        index=i,
                        total=total,
                    )
                )
            for fut in as_completed(futures):
                case_dir, success, msg = fut.result()
                if success:
                    ok += 1
                else:
                    fail += 1
                    print(f"[FAIL] {case_dir}: {msg}", flush=True)

    if not args.skip_summaries:
        sweeps_root = REPO_ROOT / "results/sweeps"
        if sweeps_root.is_dir() and any(
            sweeps_root.resolve() in r.resolve().parents or r.resolve() == sweeps_root.resolve()
            for r in roots
        ):
            _regen_axis_summaries(sweeps_root)

    print(f"[rerun] done ok={ok} fail={fail}", flush=True)
    return 1 if fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
