#!/usr/bin/env python3
"""按指定 timeline 聚合方式重跑某 sweep 轴下全部 case 的 parse + timeline + summary。"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

_TOOLS_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _TOOLS_DIR.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from tools.dffc_profile.plot_sweep_timelines import collect_cases
from tools.dffc_profile.profile_constants import TIMELINE_AGG_CHOICES, TIMELINE_AGG_DEFAULT
from tools.dffc_profile.timeline_backup import (
    backup_sweep_summaries,
    backup_tag_from_marker,
    backup_timeline_artifacts,
    read_aggregation_marker,
    restore_sweep_summaries,
    restore_timeline_artifacts,
    write_aggregation_marker,
)


def _run(script: str, *argv: str) -> None:
    subprocess.run(
        [sys.executable, str(_TOOLS_DIR / script), *argv],
        check=True,
        cwd=str(_REPO_ROOT),
    )


def regen_axis(
    sweep_dir: Path,
    *,
    timeline_aggregation: str,
    timeline_rank: int = 0,
    save_backup: bool = True,
    manifest_only: bool = False,
) -> list[str]:
    cases, _ = collect_cases(sweep_dir, all_dirs=not manifest_only)
    if not cases:
        raise SystemExit(f"no cases under {sweep_dir}")

    backup_tags: set[str] = set()
    if save_backup:
        for case in cases:
            tag = backup_tag_from_marker(case["case_dir"])
            backup_tags.add(tag)
            backup_timeline_artifacts(case["case_dir"], tag)
        axis_marker = read_aggregation_marker(sweep_dir)
        summary_tag = (
            str(axis_marker["timeline_aggregation"])
            if axis_marker and axis_marker.get("timeline_aggregation")
            else next(iter(backup_tags), TIMELINE_AGG_DEFAULT)
        )
        backup_sweep_summaries(sweep_dir, summary_tag)
        backup_tags.add(summary_tag)

    for case in cases:
        d = case["case_dir"]
        argv = [
            "--indir",
            str(d),
            "--timeline-aggregation",
            timeline_aggregation,
        ]
        if timeline_aggregation == "rank0":
            argv.extend(["--timeline-rank", str(timeline_rank)])
        _run("parse_profile.py", *argv)
        slug = case.get("slug", d.name)
        title = f"dispatch_ffn_combine {slug}"
        if timeline_aggregation == "rank0":
            title += f" (rank{timeline_rank})"
        elif timeline_aggregation == "relative_median":
            title += " (relative_median)"
        _run(
            "gen_timeline.py",
            "--breakdown",
            str(d / "breakdown.json"),
            "--title",
            title,
        )

    _run(
        "plot_sweep_timelines.py",
        "--sweep-dir",
        str(sweep_dir),
        *(["--manifest-only"] if manifest_only else []),
    )

    write_aggregation_marker(
        sweep_dir,
        {
            "timeline_aggregation": timeline_aggregation,
            "timeline_rank": timeline_rank if timeline_aggregation == "rank0" else None,
            "backup_tags": sorted(backup_tags),
        },
    )
    return sorted(backup_tags)


def restore_axis(
    sweep_dir: Path,
    tag: str,
    *,
    manifest_only: bool = False,
) -> None:
    cases, _ = collect_cases(sweep_dir, all_dirs=not manifest_only)
    for case in cases:
        restore_timeline_artifacts(case["case_dir"], tag)
    restore_sweep_summaries(sweep_dir, tag)
    _run("plot_sweep_timelines.py", "--sweep-dir", str(sweep_dir))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sweep-dir", type=Path, required=True)
    parser.add_argument(
        "--timeline-aggregation",
        choices=TIMELINE_AGG_CHOICES,
        default=TIMELINE_AGG_DEFAULT,
    )
    parser.add_argument("--timeline-rank", type=int, default=0)
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="切换前不备份现有 breakdown/timeline",
    )
    parser.add_argument("--manifest-only", action="store_true")
    parser.add_argument(
        "--restore",
        metavar="TAG",
        default=None,
        help="从指定 tag 备份恢复（如 rank0 / trimmed_mean_duration）",
    )
    args = parser.parse_args()

    sweep_dir = args.sweep_dir if args.sweep_dir.is_absolute() else _REPO_ROOT / args.sweep_dir

    if args.restore is not None:
        restore_axis(sweep_dir, args.restore, manifest_only=args.manifest_only)
        print(f"[regen] restored axis from tag={args.restore}")
        return 0

    tags = regen_axis(
        sweep_dir,
        timeline_aggregation=args.timeline_aggregation,
        timeline_rank=args.timeline_rank,
        save_backup=not args.no_backup,
        manifest_only=args.manifest_only,
    )
    print(f"[regen] {sweep_dir} timeline_aggregation={args.timeline_aggregation}")
    if tags:
        print(f"[regen] backup tags={tags}（回退: --restore <tag>）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
