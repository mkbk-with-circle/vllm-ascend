#!/usr/bin/env python3
"""按参数轴 sweep：每 case 自动 timeline + 带宽。"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_TOOLS_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _TOOLS_DIR.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from tools.dffc_profile.bandwidth import compute_bandwidth_from_dir
from tools.dffc_profile.run_one_case import run_pipeline
from tools.dffc_profile.sweep_grids import DEFAULT_EP, SWEEP_AXES, sweep_out_root


def run_axis(axis_name: str, world_size: int, repo_root: Path) -> Path:
    if axis_name not in SWEEP_AXES:
        raise ValueError(f"未知轴: {axis_name}, 可选 {list(SWEEP_AXES)}")
    axis = SWEEP_AXES[axis_name]
    root = sweep_out_root(repo_root, axis_name)
    root.mkdir(parents=True, exist_ok=True)

    manifest_entries = []
    failures = []
    for case in axis.iter_cases(ep=world_size):
        out_dir = root / case.result_slug(world_size)
        print(f"[sweep:{axis_name}] {case.name} -> {out_dir.name}")
        try:
            if not (out_dir / "bandwidth.json").exists():
                run_pipeline(case, world_size, out_dir)
            bw = compute_bandwidth_from_dir(out_dir)
            entry = {
                "case_name": case.name,
                "slug": case.result_slug(world_size),
                "path": str(out_dir.relative_to(repo_root)),
                "params": case.to_dict(),
                "sweep_value": _sweep_value(axis_name, case),
                "bandwidth": {
                    "dispatch_gbps_job": bw["job"]["bw_dispatch_gbps"],
                    "combine_gbps_job": bw["job"]["bw_combine_gbps"],
                },
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
        "ep": world_size,
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
    parser.add_argument("--world-size", type=int, default=DEFAULT_EP)
    args = parser.parse_args()

    axes = list(SWEEP_AXES.keys()) if args.all else (args.axes or [])
    if not axes:
        parser.error("需 --axis 或 --all")

    for ax in axes:
        run_axis(ax, args.world_size, _REPO_ROOT)

    # 每轴 sweep 结束后生成趋势图
    from tools.dffc_profile.plot_sweep_bandwidth import plot_axis

    for ax in axes:
        plot_axis(sweep_out_root(_REPO_ROOT, ax))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
