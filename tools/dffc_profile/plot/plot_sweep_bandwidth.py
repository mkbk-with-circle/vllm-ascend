#!/usr/bin/env python3
"""sweep manifest → dispatch/combine 带宽趋势折线图。"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt

from tools.dffc_profile.lib.paths import DFFC_ROOT, REPO_ROOT, ensure_repo_on_path, script_path

ensure_repo_on_path()

from tools.dffc_profile.lib.bandwidth import manifest_bandwidth_fields
from tools.dffc_profile.lib.profile_constants import (
    HCCS_THEORETICAL_GBPS_PER_RANK,
    hccs_theoretical_gbps_job,
)

AXIS_LABELS = {
    "numtokens": "numtokens (M)",
    "hidden": "hidden_size (K)",
    "imhidden": "imhidden (N/2)",
    "topk": "topK",
}

# 本机 profile 环境标识（与 source_env.sh SOC_VERSION 一致）
HARDWARE_LABEL = "Ascend910 (ascend910_9391, 8×HCCS_SW)"


def _fmt_gbps(value: float) -> str:
    """带宽固定一位小数，禁用科学计数法。"""
    return f"{value:.1f}"


def _fmt_sweep_x(value: float) -> str:
    """sweep 横轴取值：整数直接显示，否则保留 2 位小数。"""
    if abs(value - round(value)) < 1e-6:
        return str(int(round(value)))
    return f"{value:.2f}"


def _peak_at(xs: list[float], ys: list[float]) -> tuple[float, float]:
    """返回 (峰值, 对应 sweep x)。"""
    idx = max(range(len(ys)), key=lambda i: ys[i])
    return ys[idx], xs[idx]


def _compute_peaks(
    xs: list[float],
    dispatch_y: list[float],
    combine_y: list[float],
    dispatch_pr: list[float] | None,
    combine_pr: list[float] | None,
) -> dict[str, Any]:
    dj, dx = _peak_at(xs, dispatch_y)
    cj, cx = _peak_at(xs, combine_y)
    peaks: dict[str, Any] = {
        "dispatch_gbps_job": dj,
        "dispatch_gbps_job_at": dx,
        "combine_gbps_job": cj,
        "combine_gbps_job_at": cx,
    }
    if dispatch_pr is not None and combine_pr is not None:
        dp, dpx = _peak_at(xs, dispatch_pr)
        cp, cpx = _peak_at(xs, combine_pr)
        peaks.update(
            {
                "dispatch_gbps_per_rank_median": dp,
                "dispatch_gbps_per_rank_median_at": dpx,
                "combine_gbps_per_rank_median": cp,
                "combine_gbps_per_rank_median_at": cpx,
            }
        )
    return peaks


def _peak_footer_lines(peaks: dict[str, Any], axis: str) -> list[str]:
    """图下方四行脚注：峰值分开展示，禁用科学计数法。"""
    ax_label = AXIS_LABELS.get(axis, axis)
    dj_at = _fmt_sweep_x(float(peaks["dispatch_gbps_job_at"]))
    dp_at = _fmt_sweep_x(float(peaks.get("dispatch_gbps_per_rank_median_at", 0)))
    cj_at = _fmt_sweep_x(float(peaks["combine_gbps_job_at"]))
    cp_at = _fmt_sweep_x(float(peaks.get("combine_gbps_per_rank_median_at", 0)))
    return [
        (
            f"Peak dispatch (job): {_fmt_gbps(peaks['dispatch_gbps_job'])} GB/s"
            f"  @ {ax_label} = {dj_at}"
        ),
        (
            f"Peak dispatch (per-rank median): "
            f"{_fmt_gbps(peaks.get('dispatch_gbps_per_rank_median', 0))} GB/s"
            f"  @ {ax_label} = {dp_at}"
        ),
        (
            f"Peak combine (job): {_fmt_gbps(peaks['combine_gbps_job'])} GB/s"
            f"  @ {ax_label} = {cj_at}"
        ),
        (
            f"Peak combine (per-rank median): "
            f"{_fmt_gbps(peaks.get('combine_gbps_per_rank_median', 0))} GB/s"
            f"  @ {ax_label} = {cp_at}"
        ),
    ]


def plot_axis(sweep_dir: Path) -> Path:
    manifest_path = sweep_dir / "manifest.json"
    with open(manifest_path, encoding="utf-8") as f:
        manifest = json.load(f)

    axis = manifest["axis"]
    ws = int(manifest.get("world_size", 8))
    cases = sorted(manifest["cases"], key=lambda c: c["sweep_value"])
    # manifest 可能缺 per-rank 字段：从 case/bandwidth.json 补齐
    for c in cases:
        bw_meta = c.get("bandwidth") or {}
        if bw_meta.get("dispatch_gbps_per_rank_median") is not None:
            continue
        slug = c.get("slug")
        if not slug:
            continue
        bw_path = sweep_dir / slug / "bandwidth.json"
        if not bw_path.is_file():
            continue
        with open(bw_path, encoding="utf-8") as bf:
            c["bandwidth"] = manifest_bandwidth_fields(json.load(bf))
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

    peaks = _compute_peaks(xs, dispatch_y, combine_y, dispatch_pr, combine_pr)
    footer_lines = _peak_footer_lines(peaks, axis)

    # 主图与脚注分区：抬高主图底边，xlabel 用 axes 坐标压在刻度下方
    fig = plt.figure(figsize=(12, 8.5), dpi=100)
    ax = fig.add_axes((0.08, 0.56, 0.90, 0.36))
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
    job_theo = hccs_theoretical_gbps_job(ws)
    # 仅画 per-rank 理论线；job 理论值 (EP×392) 远高于实测，放脚注避免压扁 Y 轴
    ax.axhline(
        HCCS_THEORETICAL_GBPS_PER_RANK,
        color="#4C78A8", linestyle=":", linewidth=1.0, alpha=0.55,
        label=(
            f"HCCS theory: per-rank {int(HCCS_THEORETICAL_GBPS_PER_RANK)} GB/s,"
            f" job {int(job_theo)} GB/s (ws={ws})"
        ),
    )
    notes = manifest.get("notes") or {}
    title = f"dispatch_ffn_combine bandwidth sweep — ws{ws} / by_{axis}"
    if notes.get("max_ok_k_m8192"):
        title += f"  (max K={notes['max_ok_k_m8192']})"
    ax.set_xlabel(AXIS_LABELS.get(axis, axis), labelpad=2)
    ax.xaxis.set_label_coords(0.5, -0.12)
    ax.set_ylabel("effective bandwidth (GB/s)")
    ax.set_title(title)
    ax.grid(True, linestyle=":", alpha=0.5)
    ax.legend(loc="upper left", fontsize=8, ncol=2)
    # 坐标轴禁用科学计数法与 offset 缩写（如 1e3）
    ax.ticklabel_format(style="plain", axis="both", useOffset=False)

    # 脚注 y 固定在 x 轴 label 下方
    footer_ys = [0.28, 0.20, 0.12, 0.04]
    for y, line in zip(footer_ys, footer_lines):
        fig.text(
            0.5,
            y,
            line,
            ha="center",
            va="center",
            fontsize=9.5,
            color="#333333",
        )

    out_png = sweep_dir / "summary_bandwidth.png"
    fig.savefig(out_png, dpi=200, bbox_inches="tight")
    plt.close(fig)

    summary = {
        "axis": axis,
        "world_size": ws,
        "expert_per_rank": int(manifest.get("expert_per_rank", manifest.get("ep", 8))),
        "hardware": f"{HARDWARE_LABEL}, ws={ws}",
        "theoretical_hccs_gbps_per_rank": HCCS_THEORETICAL_GBPS_PER_RANK,
        "theoretical_hccs_gbps_job": job_theo,
        "peaks": peaks,
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
        sweep_dir = REPO_ROOT / sweep_dir
    plot_axis(sweep_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
