#!/usr/bin/env python3
"""按参数轴 sweep：每 case 自动 timeline + 带宽。"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from tools.dffc_profile.lib.paths import DFFC_ROOT, REPO_ROOT, ensure_repo_on_path, script_path

ensure_repo_on_path()

from tools.dffc_profile.lib.bandwidth import compute_bandwidth_from_dir, manifest_bandwidth_fields
from tools.dffc_profile.lib.profile_constants import DFFC_PROFILE_VERSION, DFFC_PROFILE_WORDS
from tools.dffc_profile.pipeline.run_one_case import run_pipeline
from tools.dffc_profile.lib.sweep_grids import (
    DEFAULT_EP,
    SWEEP_AXES,
    sweep_out_root,
    visible_devices_for_world_size,
)


def _needs_rerun(out_dir: Path, case, *, force: bool) -> bool:
    """v9 sweep：版本或 e 不一致时重跑。"""
    if force or not (out_dir / "bandwidth.json").is_file():
        return True
    case_json = out_dir / "case.json"
    if not case_json.is_file():
        return True
    data = json.loads(case_json.read_text(encoding="utf-8"))
    if int(data.get("e", 0)) != case.e:
        return True
    profiles = list(out_dir.glob("rank*_profile.json"))
    if not profiles:
        return True
    sample = json.loads(profiles[0].read_text(encoding="utf-8"))
    if sample.get("version") != DFFC_PROFILE_VERSION:
        return True
    if "expert_segments" not in sample:
        return True
    # v9 sidecar：raw 须为完整 304 words，旧 162-word 布局无 AIC per-expert
    raw = sample.get("raw") or []
    if len(raw) < DFFC_PROFILE_WORDS:
        return True
    return False


def run_axis(axis_name: str, world_size: int, repo_root: Path, *, force: bool) -> Path:
    if axis_name not in SWEEP_AXES:
        raise ValueError(f"未知轴: {axis_name}, 可选 {list(SWEEP_AXES)}")
    axis = SWEEP_AXES[axis_name]
    root = sweep_out_root(repo_root, axis_name, world_size=world_size)
    root.mkdir(parents=True, exist_ok=True)

    manifest_entries = []
    failures = []
    for case in axis.iter_cases(ep=world_size):
        out_dir = root / case.result_slug(world_size)
        print(f"[sweep:{axis_name}] {case.name} -> {out_dir.name}")
        try:
            if _needs_rerun(out_dir, case, force=force):
                run_pipeline(
                    case,
                    world_size,
                    out_dir,
                    strict_validate=(world_size <= 8),
                )
            bw = compute_bandwidth_from_dir(out_dir)
            job = bw["job"]
            entry = {
                "case_name": case.name,
                "slug": case.result_slug(world_size),
                "path": str(out_dir.relative_to(repo_root)),
                "params": case.to_dict(),
                "sweep_value": _sweep_value(axis_name, case),
                "bandwidth": manifest_bandwidth_fields(bw),
                "status": "ok",
            }
            manifest_entries.append(entry)
        except Exception as exc:
            print(f"[sweep:{axis_name}] FAILED {out_dir.name}: {exc}", file=sys.stderr)
            failures.append({"slug": case.result_slug(world_size), "error": str(exc)})

    manifest = {
        "axis": axis_name,
        "fixed": axis.fixed,
        "values": list(axis.values),
        "world_size": world_size,
        "expert_per_rank": axis.fixed.get("e", 8),
        "cases": manifest_entries,
        "failures": failures,
    }
    manifest_path = root / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"[sweep] manifest -> {manifest_path}")
    return root


def _sweep_value(axis_name: str, case) -> int:
    if axis_name == "numtokens":
        return case.m
    if axis_name == "hidden":
        return case.k
    if axis_name == "imhidden":
        return case.imhidden
    if axis_name == "topk":
        return case.topk
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--axis",
        choices=list(SWEEP_AXES.keys()),
        action="append",
        dest="axes",
    )
    parser.add_argument("--all", action="store_true", help="跑全部四轴")
    parser.add_argument("--world-size", type=int, action="append", dest="world_sizes")
    parser.add_argument("--force-rerun", action="store_true", help="忽略已有结果，全部重跑")
    args = parser.parse_args()

    axes = list(SWEEP_AXES.keys()) if args.all else (args.axes or [])
    if not axes:
        parser.error("需 --axis 或 --all")

    world_sizes = args.world_sizes or [DEFAULT_EP]

    for ws in world_sizes:
        os.environ["ASCEND_RT_VISIBLE_DEVICES"] = visible_devices_for_world_size(ws)
        print(f"[sweep] world_size={ws} ASCEND_RT_VISIBLE_DEVICES={os.environ['ASCEND_RT_VISIBLE_DEVICES']}")
        for ax in axes:
            run_axis(ax, ws, REPO_ROOT, force=args.force_rerun)

    # 每轴 sweep 结束后生成趋势图与 timeline 汇总
    from tools.dffc_profile.plot.plot_sweep_bandwidth import plot_axis
    from tools.dffc_profile.plot.plot_sweep_timelines import plot_sweep_timelines

    for ws in world_sizes:
        for ax in axes:
            axis_dir = sweep_out_root(REPO_ROOT, ax, world_size=ws)
            if axis_dir.is_dir():
                plot_axis(axis_dir)
                plot_sweep_timelines(axis_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
