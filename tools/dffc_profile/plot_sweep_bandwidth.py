#!/usr/bin/env python3
"""sweep manifest → dispatch/combine 带宽趋势折线图。"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt

_TOOLS_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _TOOLS_DIR.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

AXIS_LABELS = {
    "numtokens": "numtokens (M)",
    "hidden": "hidden_size (K)",
    "imhidden": "imhidden (N/2)",
    "topk": "topK",
}


def plot_axis(sweep_dir: Path) -> Path:
    manifest_path = sweep_dir / "manifest.json"
    with open(manifest_path, encoding="utf-8") as f:
        manifest = json.load(f)

    axis = manifest["axis"]
    cases = sorted(manifest["cases"], key=lambda c: c["sweep_value"])
    xs = [c["sweep_value"] for c in cases]
    dispatch_y = [c["bandwidth"]["dispatch_gbps_job"] for c in cases]
    combine_y = [c["bandwidth"]["combine_gbps_job"] for c in cases]
    # per-rank 中位数（与单卡 HCCS 对比更有意义）
    has_per_rank = all(
        "dispatch_gbps_per_rank_median" in c["bandwidth"]
        for c in cases
    )
    dispatch_pr = (
        [c["bandwidth"]["dispatch_gbps_per_rank_median"] for c in cases]
        if has_per_rank
        else None
    )
    combine_pr = (
        [c["bandwidth"]["combine_gbps_per_rank_median"] for c in cases]
        if has_per_rank
        else None
    )

    fig, ax = plt.subplots(figsize=(11, 5.5))
    ax.plot(xs, dispatch_y, "o-", label="dispatch (job)", color="#F58518", linewidth=2)
    ax.plot(xs, combine_y, "s-", label="combine (job)", color="#E45756", linewidth=2)
    if dispatch_pr is not None and combine_pr is not None:
        ax.plot(
            xs, dispatch_pr, "o--", label="dispatch (per-rank median)",
            color="#F58518", linewidth=1.2, alpha=0.65,
        )
        ax.plot(
            xs, combine_pr, "s--", label="combine (per-rank median)",
            color="#E45756", linewidth=1.2, alpha=0.65,
        )
    notes = manifest.get("notes") or {}
    title = f"dispatch_ffn_combine bandwidth sweep — by_{axis}"
    if notes.get("max_ok_k_m8192"):
        title += f"  (max K={notes['max_ok_k_m8192']})"
    ax.set_xlabel(AXIS_LABELS.get(axis, axis))
    ax.set_ylabel("effective bandwidth (GB/s)")
    ax.set_title(title)
    ax.grid(True, linestyle=":", alpha=0.5)
    ax.legend(loc="best", fontsize=9)
    fig.tight_layout()

    out_png = sweep_dir / "summary_bandwidth.png"
    fig.savefig(out_png, dpi=150)
    plt.close(fig)

    summary = {
        "axis": axis,
        "points": [
            {
                "x": c["sweep_value"],
                "slug": c["slug"],
                "dispatch_gbps_job": c["bandwidth"]["dispatch_gbps_job"],
                "combine_gbps_job": c["bandwidth"]["combine_gbps_job"],
                **(
                    {
                        "dispatch_gbps_per_rank_median": c["bandwidth"][
                            "dispatch_gbps_per_rank_median"
                        ],
                        "combine_gbps_per_rank_median": c["bandwidth"][
                            "combine_gbps_per_rank_median"
                        ],
                    }
                    if has_per_rank
                    else {}
                ),
            }
            for c in cases
        ],
        "failures": manifest.get("failures", []),
        "notes": manifest.get("notes", {}),
    }
    out_json = sweep_dir / "summary_bandwidth.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"[plot] {out_png}")
    return out_png


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sweep-dir", type=Path, required=True, help="e.g. results/dffc/sweeps/by_hidden")
    args = parser.parse_args()
    sweep_dir = args.sweep_dir
    if not sweep_dir.is_absolute():
        sweep_dir = _REPO_ROOT / sweep_dir
    plot_axis(sweep_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
