#!/usr/bin/env python3
"""为 sweep 轴下各 manifest case 生成 timeline_expert_focus.png 及 summary 拼图。"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from tools.dffc_profile.lib.paths import REPO_ROOT, cli_script, ensure_repo_on_path

ensure_repo_on_path()

from tools.dffc_profile.plot.plot_sweep_timelines import plot_sweep_timelines
from tools.dffc_profile.lib.sweep_grids import iter_sweep_axis_dirs


def _run_py(script: str, *argv: str) -> None:
    subprocess.run(
        [sys.executable, str(cli_script(script)), *argv],
        check=True,
        cwd=str(REPO_ROOT),
    )


def gen_axis(sweep_dir: Path, *, reparse: bool) -> None:
    manifest_path = sweep_dir / "manifest.json"
    if not manifest_path.is_file():
        raise FileNotFoundError(f"无 manifest: {manifest_path}")
    cases = json.loads(manifest_path.read_text(encoding="utf-8")).get("cases", [])
    if not cases:
        raise ValueError(f"manifest 无 case: {sweep_dir}")

    for c in cases:
        case_dir = sweep_dir / c["slug"]
        if not case_dir.is_dir():
            alt = REPO_ROOT / c.get("path", "")
            if alt.is_dir():
                case_dir = alt
            else:
                print(f"[expert-timeline] SKIP 无目录: {c['slug']}", file=sys.stderr)
                continue
        if reparse or not (case_dir / "breakdown.json").is_file():
            _run_py("parse_profile.py", "--indir", str(case_dir), "--timeline-aggregation", "relative_median")
        slug = c["slug"]
        title = f"dispatch_ffn_combine {slug} | expert active (relative_median)"
        _run_py(
            "gen_timeline.py",
            "--breakdown",
            str(case_dir / "breakdown.json"),
            "--title",
            title,
            "--expert-active-only",
            "--focus-only",
            "--out",
            str(case_dir / "timeline_expert.png"),
            "--out-focus",
            str(case_dir / "timeline_expert_focus.png"),
        )

    outs = plot_sweep_timelines(sweep_dir)
    summary = sweep_dir / "summary_timeline_expert_focus.png"
    if summary not in outs and not summary.is_file():
        print(f"[expert-timeline] WARN 未生成 summary: {summary}", file=sys.stderr)
    else:
        print(f"[expert-timeline] axis done -> {summary}")


def main() -> int:
    parser = argparse.ArgumentParser(description="批量生成 expert focus timeline + summary 拼图")
    parser.add_argument(
        "--sweep-dir",
        type=Path,
        action="append",
        default=[],
        help="单个轴目录，可重复；默认处理四个标准轴",
    )
    parser.add_argument("--reparse", action="store_true", help="强制重新 parse breakdown.json")
    args = parser.parse_args()

    if args.sweep_dir:
        dirs = [
            d if d.is_absolute() else REPO_ROOT / d
            for d in args.sweep_dir
        ]
    else:
        root = REPO_ROOT / "results" / "sweeps"
        dirs = list(iter_sweep_axis_dirs(root))

    for sweep_dir in dirs:
        if not sweep_dir.is_dir():
            print(f"[expert-timeline] SKIP 不存在: {sweep_dir}", file=sys.stderr)
            continue
        print(f"[expert-timeline] === {sweep_dir.name} ===")
        gen_axis(sweep_dir, reparse=args.reparse)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
