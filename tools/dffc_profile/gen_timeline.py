#!/usr/bin/env python3
"""根据 breakdown.json 生成 AIV/AIC 双轨 timeline PNG。"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

_TOOLS_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _TOOLS_DIR.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from tools.dffc_profile.profile_constants import AIC_PHASES, AIV_PHASES, PHASE_NAMES

# comet 风格配色
PHASE_COLORS = {
    "prep": "#4C78A8",
    "dispatch": "#F58518",
    "swiglu": "#54A24B",
    "combine": "#E45756",
    "gmm1": "#B279A2",
    "gmm2": "#72B7B2",
}


def _draw_track(ax, y: float, phases: frozenset[str], agg: dict, label: str) -> None:
    ax.text(-0.02, y, label, transform=ax.get_yaxis_transform(), ha="right", va="center", fontsize=11)
    xmax = 0.0
    for name in PHASE_NAMES:
        if name not in phases:
            continue
        row = agg["phases"][name]
        x = row["timeline_start_us"]
        w = max(row["timeline_duration_us"], 1.0)
        xmax = max(xmax, x + w)
        rect = FancyBboxPatch(
            (x, y - 0.32),
            w,
            0.64,
            boxstyle="round,pad=0.02,rounding_size=4",
            linewidth=0.8,
            edgecolor="#333333",
            facecolor=PHASE_COLORS.get(name, "#999999"),
            alpha=0.92,
        )
        ax.add_patch(rect)
        ax.text(
            x + w / 2,
            y,
            f"{name}\n{w:.0f}µs",
            ha="center",
            va="center",
            fontsize=8,
            color="white",
            fontweight="bold",
        )
    return xmax


def gen_png(breakdown: dict, out_path: Path, title: str) -> None:
    fig, ax = plt.subplots(figsize=(14, 3.2))
    ymax = _draw_track(ax, 1.0, AIV_PHASES, breakdown, "AIV")
    xmax = _draw_track(ax, 0.0, AIC_PHASES, breakdown, "AIC")
    xmax = max(ymax, xmax) * 1.05

    ax.set_xlim(0, xmax)
    ax.set_ylim(-0.6, 1.6)
    ax.set_xlabel("相对时间 (µs)，起点 = median(prep_begin) - t0")
    ax.set_yticks([])
    ax.set_title(title)
    ax.grid(axis="x", linestyle=":", alpha=0.4)
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"[timeline] {out_path}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--breakdown", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--title", default="dispatch_ffn_combine timeline")
    args = parser.parse_args()

    with open(args.breakdown, encoding="utf-8") as f:
        breakdown = json.load(f)

    out = args.out or (args.breakdown.parent / "timeline.png")
    gen_png(breakdown, out, args.title)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
