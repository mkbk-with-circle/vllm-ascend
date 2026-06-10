#!/usr/bin/env python3
"""将同一 sweep 轴下各 case 的 timeline / timeline_focus 拼成一张总览图。"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

import matplotlib.image as mpimg
import matplotlib.pyplot as plt

_TOOLS_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _TOOLS_DIR.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from tools.dffc_profile.plot_sweep_bandwidth import AXIS_LABELS

SWEEP_AXIS_DIRS = ("by_hidden", "by_imhidden", "by_numtokens", "by_topk")


def _grid_shape(n: int, ncol_max: int = 3) -> tuple[int, int]:
    """子图行列数：尽量接近方阵，列数不超过 ncol_max。"""
    if n <= 0:
        return 0, 0
    ncol = min(ncol_max, max(1, math.ceil(math.sqrt(n))))
    nrow = math.ceil(n / ncol)
    return nrow, ncol


def _case_label(case: dict[str, Any], axis: str | None) -> str:
    """子图标题：优先 sweep 值，否则用 slug 缩写。"""
    sv = case.get("sweep_value")
    if sv is not None and axis:
        ax_label = AXIS_LABELS.get(axis, axis)
        return f"{ax_label}={sv}"
    slug = case.get("slug", "")
    return slug.replace("ep8_", "", 1) if slug else "case"


def collect_cases(sweep_dir: Path, *, all_dirs: bool) -> tuple[list[dict[str, Any]], str | None]:
    """收集 case 目录；默认 manifest 顺序，--all-dirs 时含目录内全部 timeline。"""
    manifest_path = sweep_dir / "manifest.json"
    axis: str | None = None
    manifest_slugs: dict[str, dict[str, Any]] = {}
    ordered: list[dict[str, Any]] = []

    if manifest_path.is_file():
        with open(manifest_path, encoding="utf-8") as f:
            manifest = json.load(f)
        axis = manifest.get("axis")
        for c in sorted(manifest.get("cases", []), key=lambda x: x.get("sweep_value", 0)):
            slug = c["slug"]
            case_dir = sweep_dir / slug
            if not case_dir.is_dir():
                case_dir = _REPO_ROOT / c.get("path", "")
            manifest_slugs[slug] = c
            ordered.append(
                {
                    "slug": slug,
                    "case_dir": case_dir,
                    "sweep_value": c.get("sweep_value"),
                    "case_name": c.get("case_name"),
                    "status": c.get("status", "ok"),
                }
            )

    if all_dirs:
        seen = {x["slug"] for x in ordered}
        extras = []
        for d in sorted(sweep_dir.iterdir()):
            if not d.is_dir() or d.name in seen:
                continue
            if (d / "timeline.png").is_file():
                extras.append(
                    {
                        "slug": d.name,
                        "case_dir": d,
                        "sweep_value": None,
                        "case_name": d.name,
                        "status": "extra",
                    }
                )
        ordered.extend(extras)

    return ordered, axis


def _compose_mosaic(
    cases: list[dict[str, Any]],
    image_name: str,
    *,
    axis: str | None,
    title: str,
    ncol_max: int,
    dpi: int,
) -> tuple[plt.Figure | None, list[str]]:
    """把多张 PNG 拼到同一 figure；返回 figure 与缺失列表。"""
    present: list[tuple[dict[str, Any], Any]] = []
    missing: list[str] = []
    for case in cases:
        img_path = case["case_dir"] / image_name
        if not img_path.is_file():
            missing.append(f"{case['slug']}: missing {image_name}")
            continue
        present.append((case, mpimg.imread(img_path)))

    if not present:
        return None, missing

    n = len(present)
    nrow, ncol = _grid_shape(n, ncol_max=ncol_max)
    # 单张图宽约 6in，纵向略矮
    fig_w = max(6.0, ncol * 6.2)
    fig_h = max(4.0, nrow * 3.6) + 0.8
    fig, axes = plt.subplots(nrow, ncol, figsize=(fig_w, fig_h), dpi=dpi)
    fig.suptitle(title, fontsize=13, y=0.995)

    if nrow == 1 and ncol == 1:
        ax_list = [axes]
    elif nrow == 1 or ncol == 1:
        ax_list = list(axes.flatten()) if hasattr(axes, "flatten") else list(axes)
    else:
        ax_list = axes.flatten().tolist()

    for ax in ax_list[n:]:
        ax.axis("off")

    for idx, (case, img) in enumerate(present):
        ax = ax_list[idx]
        ax.imshow(img)
        ax.set_axis_off()
        label = _case_label(case, axis)
        if case.get("status") not in (None, "ok"):
            label += f" [{case['status']}]"
        ax.set_title(label, fontsize=10, pad=6)

    fig.tight_layout(rect=[0, 0, 1, 0.98])
    return fig, missing


def plot_sweep_timelines(
    sweep_dir: Path,
    *,
    all_dirs: bool = False,
    ncol_max: int = 3,
    dpi: int = 120,
) -> list[Path]:
    """为一个 sweep 轴目录生成 summary_timeline*.png。"""
    sweep_dir = sweep_dir.resolve()
    cases, axis = collect_cases(sweep_dir, all_dirs=all_dirs)
    if not cases:
        print(f"[timeline-mosaic] skip (no cases): {sweep_dir}", file=sys.stderr)
        return []

    axis_tag = axis or sweep_dir.name.replace("by_", "")
    outs: list[Path] = []
    for image_name, out_name in (
        ("timeline.png", "summary_timeline.png"),
        ("timeline_focus.png", "summary_timeline_focus.png"),
    ):
        title = f"dispatch_ffn_combine timeline mosaic — by_{axis_tag} ({image_name})"
        fig, missing = _compose_mosaic(
            cases,
            image_name,
            axis=axis,
            title=title,
            ncol_max=ncol_max,
            dpi=dpi,
        )
        if fig is None:
            print(f"[timeline-mosaic] WARN no {image_name} under {sweep_dir}", file=sys.stderr)
            continue
        out_path = sweep_dir / out_name
        fig.savefig(out_path, dpi=dpi, bbox_inches="tight")
        plt.close(fig)
        outs.append(out_path)
        print(f"[timeline-mosaic] {out_path} ({len(cases) - len(missing)}/{len(cases)} panels)")
        for m in missing:
            print(f"[timeline-mosaic]   WARN {m}", file=sys.stderr)

    return outs


def plot_all_sweeps(
    sweeps_root: Path,
    *,
    all_dirs: bool = False,
    ncol_max: int = 3,
    dpi: int = 120,
) -> list[Path]:
    """遍历 sweeps_root 下各 by_* 轴目录。"""
    outs: list[Path] = []
    for name in SWEEP_AXIS_DIRS:
        sweep_dir = sweeps_root / name
        if sweep_dir.is_dir():
            outs.extend(
                plot_sweep_timelines(
                    sweep_dir,
                    all_dirs=all_dirs,
                    ncol_max=ncol_max,
                    dpi=dpi,
                )
            )
    return outs


def main() -> int:
    parser = argparse.ArgumentParser(description="拼接 sweep 轴下各 case 的 timeline 总览图")
    parser.add_argument(
        "--sweeps-root",
        type=Path,
        default=Path("results/sweeps"),
        help="sweep 根目录（含 by_hidden 等）",
    )
    parser.add_argument(
        "--sweep-dir",
        type=Path,
        default=None,
        help="仅处理单个轴目录，如 results/sweeps/by_hidden",
    )
    parser.add_argument(
        "--manifest-only",
        action="store_true",
        help="仅 manifest.json 中的 sweep case（默认含目录内全部 timeline 子目录）",
    )
    parser.add_argument("--ncol-max", type=int, default=3, help="每行最多子图列数")
    parser.add_argument("--dpi", type=int, default=120)
    args = parser.parse_args()

    if args.sweep_dir is not None:
        sweep_dir = args.sweep_dir if args.sweep_dir.is_absolute() else _REPO_ROOT / args.sweep_dir
        plot_sweep_timelines(
            sweep_dir,
            all_dirs=not args.manifest_only,
            ncol_max=args.ncol_max,
            dpi=args.dpi,
        )
    else:
        sweeps_root = args.sweeps_root if args.sweeps_root.is_absolute() else _REPO_ROOT / args.sweeps_root
        plot_all_sweeps(
            sweeps_root,
            all_dirs=not args.manifest_only,
            ncol_max=args.ncol_max,
            dpi=args.dpi,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
