#!/usr/bin/env python3
"""单 rank profile → 每 rank 三张 timeline（full / focus / expert_focus），无 job 聚合。"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from tools.dffc_profile.lib.paths import DFFC_ROOT, REPO_ROOT, ensure_repo_on_path, script_path

ensure_repo_on_path()

from tools.dffc_profile.plot.gen_timeline import (
    build_focus_breakdown,
    gen_png,
    load_bandwidth,
)
from tools.dffc_profile.analysis.parse_profile import load_rank_profiles
from tools.dffc_profile.lib.profile_constants import PHASE_NAMES, TIMELINE_EXTRA_PHASES


def breakdown_from_single_profile(profile: dict[str, Any]) -> dict[str, Any]:
    """把单 rank phases 直接映射为 gen_timeline 所需的 breakdown 结构。"""
    phases_out: dict[str, dict[str, Any]] = {}
    for name in (*PHASE_NAMES, *TIMELINE_EXTRA_PHASES):
        row = profile.get("phases", {}).get(name)
        if not row or int(row.get("duration_us", 0)) < 1:
            continue
        b = float(row["begin_us"])
        d = float(row["duration_us"])
        phases_out[name] = {
            "begin_us_mean": b,
            "begin_us_median": b,
            "begin_us_max": b,
            "begin_us_min": b,
            "end_us_max": b + d,
            "duration_us_mean": d,
            "duration_us_median": d,
            "duration_us_max": d,
            "duration_us_min_nonzero": d,
            "timeline_start_us": b,
            "timeline_duration_us": d,
            "timeline_end_us": b + d,
            "timeline_n_ranks": 1,
        }

    rank = profile.get("rank")
    return {
        "t0_us": 0,
        "phases": phases_out,
        "anomalies": [],
        "num_ranks": 1,
        "valid_ranks": [rank],
        "profile_version": profile.get("version"),
        "timeline_aggregation": "single_rank",
        "timeline_rank": rank,
        "case_params": profile.get("case_params"),
        "expert_segments": profile.get("expert_segments"),
    }


def gen_rank_triplet(
    profile: dict[str, Any],
    out_dir: Path,
    *,
    title_base: str,
    bandwidth: dict[str, Any] | None,
    pack_aic_intra_phase: bool = False,
    pack_aic_walls: bool = False,
) -> None:
    """为单个 rank 生成 timeline / timeline_focus / timeline_expert_focus。"""
    out_dir.mkdir(parents=True, exist_ok=True)
    bd = breakdown_from_single_profile(profile)
    rank = profile.get("rank", "?")
    title = f"{title_base} | rank{rank}"

    gen_png(
        bd,
        out_dir / "timeline.png",
        title,
        xlabel="relative time (µs), prep = 0",
        label_bars=False,
        bandwidth=bandwidth,
        expert_active_only=False,
    )

    focus = build_focus_breakdown(bd)
    gen_png(
        focus,
        out_dir / "timeline_focus.png",
        f"{title} (focus)",
        skip_phases=frozenset({"prep"}),
        xlabel="relative time (µs), dispatch = 0 (prep omitted)",
        label_bars=True,
        bandwidth=bandwidth,
        expert_active_only=False,
    )

    gen_png(
        focus,
        out_dir / "timeline_expert_focus.png",
        f"{title} | expert active (focus)",
        skip_phases=frozenset({"prep"}),
        xlabel="relative time (µs), dispatch = 0 (prep omitted)",
        label_bars=True,
        bandwidth=bandwidth,
        expert_active_only=True,
        # False=阶段内墙钟（可交叠）；True=阶段内串行摆条（旧逻辑）
        pack_aic_intra_phase=pack_aic_intra_phase,
        pack_aic_walls=pack_aic_walls,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="每 rank 生成三张单卡 timeline")
    parser.add_argument("--case-dir", type=Path, required=True)
    parser.add_argument(
        "--out-subdir",
        default="per_rank_timeline",
        help="输出子目录名，各 rank 写入 rank{N}/",
    )
    parser.add_argument("--title", default=None, help="图标题前缀，默认用 case 目录名")
    parser.add_argument(
        "--pack-aic-intra-phase",
        action="store_true",
        help="expert_focus 阶段内串行摆条（旧逻辑）；默认阶段内用墙钟起点",
    )
    parser.add_argument(
        "--no-pack-aic-walls",
        action="store_true",
        help="expert_focus 不对 gmm 墙钟串行摆条（与 barrier 对比实验一致）",
    )
    args = parser.parse_args()

    case_dir = args.case_dir.resolve()
    profiles = load_rank_profiles(case_dir)
    bw = load_bandwidth(case_dir)
    title_base = args.title or case_dir.name

    pack_aic = not args.no_pack_aic_walls
    root = case_dir / args.out_subdir
    for p in profiles:
        rank = int(p.get("rank", 0))
        gen_rank_triplet(
            p,
            root / f"rank{rank}",
            title_base=title_base,
            bandwidth=bw,
            pack_aic_intra_phase=args.pack_aic_intra_phase,
            pack_aic_walls=pack_aic,
        )
        print(f"[per-rank-timeline] rank{rank} -> {root / f'rank{rank}'}")

    print(f"[per-rank-timeline] done {len(profiles)} ranks x 3 PNGs under {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
