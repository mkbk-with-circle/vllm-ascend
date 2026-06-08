#!/usr/bin/env python3
"""多 rank profile JSON → 阶段聚合表（mean/median/max）。"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path
from typing import Any

from tools.dffc_profile.lib.paths import DFFC_ROOT, REPO_ROOT, ensure_repo_on_path, script_path

ensure_repo_on_path()

from tools.dffc_profile.lib.profile_constants import (
    PHASE_NAMES,
    SWIGLU_WAVE_NAMES,
    TIMELINE_EXTRA_PHASES,
    UNPERMUTE_PHASE_NAME,
)
from tools.dffc_profile.lib.profile_constants import TIMELINE_AGG_CHOICES, TIMELINE_AGG_DEFAULT
from tools.dffc_profile.lib.profile_utils import (
    aggregate_expert_segments,
    aggregate_expert_segments_relative_median,
    aggregate_timeline_relative_median,
    aggregate_timeline_single_rank,
    aggregate_timeline_trimmed_by_duration,
    normalize_rank_profile,
    pick_rank_profile,
    repair_aggregate_phases_tracked,
    repair_profiles_batch,
)
from tools.dffc_profile.lib.timeline_backup import (
    DEFAULT_BACKUP_TAG,
    backup_timeline_artifacts,
    read_aggregation_marker,
    restore_timeline_artifacts,
    write_aggregation_marker,
)


def _is_run_case_payload(raw: dict[str, Any]) -> bool:
    """run_case 已写入 duration_us + prep 对齐后的 phases，勿再按 raw 槽位解析。"""
    phases = raw.get("phases", {})
    prep = phases.get("prep", {})
    return "duration_us" in prep and prep.get("begin_us", -1) == 0


def _load_case_params(indir: Path) -> dict[str, Any] | None:
    fp = indir / "case.json"
    if not fp.is_file():
        return None
    with open(fp, encoding="utf-8") as f:
        return json.load(f)


def load_rank_profiles(indir: Path) -> list[dict[str, Any]]:
    case_params = _load_case_params(indir)
    files = sorted(indir.glob("rank*_profile.json"))
    if not files:
        raise FileNotFoundError(f"未找到 profile JSON: {indir}")
    out = []
    for fp in files:
        with open(fp, encoding="utf-8") as f:
            raw = json.load(f)
        if case_params and "case_params" not in raw:
            raw["case_params"] = case_params
        if _is_run_case_payload(raw):
            norm = {
                "magic": raw.get("magic"),
                "version": raw.get("version"),
                "phases": raw["phases"],
                "rank": raw.get("rank"),
                "case": raw.get("case"),
                "ep": raw.get("ep"),
                "raw": raw.get("raw"),
                "case_params": raw.get("case_params"),
                "expert_token_nums": raw.get("expert_token_nums"),
                "expert_segments": raw.get("expert_segments"),
            }
        else:
            norm = normalize_rank_profile(raw)
        if norm is not None:
            norm["source"] = str(fp.name)
            out.append(norm)
    if not out:
        raise ValueError(f"无有效 profile（magic 校验失败）: {indir}")
    repair_profiles_batch(out)
    return out


def _aggregate_phase_row(
    name: str,
    profiles: list[dict[str, Any]],
    *,
    relative_tl: dict[str, dict[str, Any]] | None,
    single: dict[str, dict[str, float | int]] | None,
) -> dict[str, Any]:
    begins = [p["phases"][name]["begin_us"] for p in profiles if name in p["phases"]]
    ends = [p["phases"][name]["end_us"] for p in profiles if name in p["phases"]]
    durs = [p["phases"][name]["duration_us"] for p in profiles if name in p["phases"]]
    if relative_tl is not None and name in relative_tl:
        tl = relative_tl[name]
        timeline_start = float(tl["timeline_start_us"])
        timeline_dur = float(tl["timeline_duration_us"])
        timeline_n = int(tl["timeline_n_ranks"])
    elif single is not None and name in single:
        tl = single[name]
        timeline_start = float(tl["timeline_start_us"])
        timeline_dur = float(tl["timeline_duration_us"])
        timeline_n = int(tl["timeline_n_ranks"])
    else:
        timeline_start, timeline_dur, timeline_n = aggregate_timeline_trimmed_by_duration(
            begins, ends, durs
        )
    valid_durs = [d for d in durs if d >= 1]
    row: dict[str, Any] = {
        "begin_us_mean": statistics.mean(begins) if begins else 0.0,
        "begin_us_median": statistics.median(begins) if begins else 0.0,
        "begin_us_max": max(begins) if begins else 0.0,
        "begin_us_min": min(begins) if begins else 0.0,
        "end_us_max": max(ends) if ends else 0.0,
        "duration_us_mean": statistics.mean(durs) if durs else 0.0,
        "duration_us_median": statistics.median(durs) if durs else 0.0,
        "duration_us_max": max(durs) if durs else 0.0,
        "duration_us_min_nonzero": min(valid_durs) if valid_durs else 0,
        "timeline_start_us": timeline_start,
        "timeline_duration_us": timeline_dur,
        "timeline_end_us": timeline_start + timeline_dur,
        "timeline_n_ranks": timeline_n,
    }
    if relative_tl is not None and name in relative_tl:
        tl = relative_tl[name]
        for key in (
            "offset_min_us",
            "offset_max_us",
            "end_min_us",
            "end_max_us",
            "insufficient_ranks",
        ):
            if key in tl:
                row[key] = tl[key]
    return row



def aggregate(
    profiles: list[dict[str, Any]],
    *,
    case_params: dict[str, Any] | None = None,
    timeline_aggregation: str = TIMELINE_AGG_DEFAULT,
    timeline_rank: int = 0,
) -> dict[str, Any]:
    if case_params is None:
        case_params = profiles[0].get("case_params") if profiles else None

    rows: dict[str, dict[str, Any]] = {}
    anomalies: list[str] = []
    extra_meta: dict[str, Any] = {}

    relative_tl: dict[str, dict[str, Any]] | None = None
    if timeline_aggregation == "relative_median":
        relative_tl, rel_meta = aggregate_timeline_relative_median(profiles)
        extra_meta.update(rel_meta)

    single = (
        aggregate_timeline_single_rank(profiles, rank=timeline_rank)
        if timeline_aggregation == "rank0"
        else None
    )

    for name in PHASE_NAMES:
        begins = [p["phases"][name]["begin_us"] for p in profiles]
        ends = [p["phases"][name]["end_us"] for p in profiles]
        durs = [p["phases"][name]["duration_us"] for p in profiles]

        if relative_tl is not None:
            tl = relative_tl[name]
            timeline_start = float(tl["timeline_start_us"])
            timeline_dur = float(tl["timeline_duration_us"])
            timeline_n = int(tl["timeline_n_ranks"])
        elif single is not None:
            tl = single[name]
            timeline_start = float(tl["timeline_start_us"])
            timeline_dur = float(tl["timeline_duration_us"])
            timeline_n = int(tl["timeline_n_ranks"])
        else:
            timeline_start, timeline_dur, timeline_n = aggregate_timeline_trimmed_by_duration(
                begins, ends, durs
            )

        valid_durs = [d for d in durs if d >= 1]
        row: dict[str, Any] = {
            "begin_us_mean": statistics.mean(begins),
            "begin_us_median": statistics.median(begins),
            "begin_us_max": max(begins),
            "begin_us_min": min(begins),
            "end_us_max": max(ends),
            "duration_us_mean": statistics.mean(durs),
            "duration_us_median": statistics.median(durs),
            "duration_us_max": max(durs),
            "duration_us_min_nonzero": min(valid_durs) if valid_durs else 0,
            "timeline_start_us": timeline_start,
            "timeline_duration_us": timeline_dur,
            "timeline_end_us": timeline_start + timeline_dur,
            "timeline_n_ranks": timeline_n,
        }
        if relative_tl is not None:
            for key in (
                "offset_min_us",
                "offset_max_us",
                "end_min_us",
                "end_max_us",
                "insufficient_ranks",
            ):
                if key in tl:
                    row[key] = tl[key]
        rows[name] = row
        if timeline_dur < 1 or any(d < 1 for d in durs):
            anomalies.append(name)

    for wname in TIMELINE_EXTRA_PHASES:
        if not any(wname in p.get("phases", {}) for p in profiles):
            continue
        row = _aggregate_phase_row(
            wname, profiles, relative_tl=relative_tl, single=single
        )
        rows[wname] = row

    timeline_repaired = repair_aggregate_phases_tracked(rows, case_params=case_params)

    meta: dict[str, Any] = {
        "timeline_aggregation": timeline_aggregation,
        "timeline_repaired": timeline_repaired,
    }
    if timeline_aggregation == "rank0":
        meta["timeline_rank"] = timeline_rank
        meta["timeline_source"] = pick_rank_profile(profiles, timeline_rank).get("source")
    meta.update(extra_meta)

    if timeline_aggregation == "relative_median":
        expert_segments = aggregate_expert_segments_relative_median(profiles)
    else:
        expert_segments = aggregate_expert_segments(profiles, timeline_rank=timeline_rank)
    out: dict[str, Any] = {
        "t0_us": 0,
        "phases": rows,
        "anomalies": anomalies,
        "num_ranks": len(profiles),
        "valid_ranks": [p.get("rank") for p in profiles],
        "profile_version": profiles[0].get("version") if profiles else None,
        "case_params": case_params,
        **meta,
    }
    if expert_segments:
        out["expert_segments"] = expert_segments
    return out


def write_breakdown_md(agg: dict[str, Any], out_path: Path) -> None:
    lines = [
        "# dispatch_ffn_combine BREAKDOWN",
        "",
        f"- valid ranks: {agg['num_ranks']} {agg.get('valid_ranks', [])}",
        f"- profile version: {agg.get('profile_version')}",
        f"- timeline 聚合: {agg.get('timeline_aggregation', TIMELINE_AGG_DEFAULT)}"
        + (f" (rank {agg['timeline_rank']})" if agg.get("timeline_rank") is not None else ""),
    ]
    if agg.get("prep_skew_us"):
        ps = agg["prep_skew_us"]
        lines.append(
            f"- prep skew (µs): median={ps['median']:.0f} [{ps['min']:.0f}, {ps['max']:.0f}]"
        )
    if agg.get("timeline_repaired"):
        lines.append(f"- timeline repaired: {agg['timeline_repaired']}")
    agg_mode = agg.get("timeline_aggregation", TIMELINE_AGG_DEFAULT)
    lines.extend(
        [
            "",
            "| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |",
            "|-------|--------------|------------|---------|----------------|-------|---------------------------|",
        ]
    )
    table_phases = list(PHASE_NAMES)
    wave_insert = table_phases.index("swiglu") + 1
    for wname in SWIGLU_WAVE_NAMES:
        if wname in agg["phases"]:
            table_phases.insert(wave_insert, wname)
            wave_insert += 1
    if UNPERMUTE_PHASE_NAME in agg["phases"]:
        table_phases.insert(table_phases.index("combine") + 1, UNPERMUTE_PHASE_NAME)
    for name in table_phases:
        r = agg["phases"].get(name)
        if r is None:
            continue
        whisk = ""
        if "offset_min_us" in r and "offset_max_us" in r:
            whisk = f"[{r['offset_min_us']:.0f}, {r['offset_max_us']:.0f}]"
        flag = " (data?)" if r.get("insufficient_ranks") else ""
        min_nz = r.get("duration_us_min_nonzero", 0)
        min_nz_s = f"{min_nz:.1f}" if min_nz >= 1 else "—"
        lines.append(
            f"| {name}{flag} | {min_nz_s} | {r['duration_us_median']:.1f} | {r['duration_us_max']:.1f} | "
            f"{r['timeline_start_us']:.1f} | {r['timeline_duration_us']:.1f} | {whisk} |"
        )
    if agg_mode == "relative_median":
        lines.extend(
            [
                "",
                "## 列说明",
                "",
                "- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。",
                "- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。",
                "- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值；"
                " 即 `prep_median + min/max(phase.begin − dispatch.begin)`。"
                " 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。",
                "- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。",
            ]
        )
    if agg["anomalies"]:
        lines.extend(["", "## 异常阶段", ""])
        for a in agg["anomalies"]:
            lines.append(f"- `{a}`: duration < 1µs")
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--indir", type=Path, required=True)
    parser.add_argument("--out-json", type=Path, default=None)
    parser.add_argument("--out-md", type=Path, default=None)
    parser.add_argument("--strict", action="store_true", help="有 anomaly 时返回非 0")
    parser.add_argument(
        "--timeline-aggregation",
        choices=TIMELINE_AGG_CHOICES,
        default=None,
        help=f"timeline 聚合方式（默认 {TIMELINE_AGG_DEFAULT}）",
    )
    parser.add_argument("--timeline-rank", type=int, default=0, help="rank0 模式使用的 rank")
    parser.add_argument(
        "--save-backup",
        nargs="?",
        const=DEFAULT_BACKUP_TAG,
        default=None,
        metavar="TAG",
        help=f"写入前备份现有产物为 *.<TAG>.*（默认 {DEFAULT_BACKUP_TAG}）",
    )
    parser.add_argument(
        "--restore-backup",
        nargs="?",
        const=DEFAULT_BACKUP_TAG,
        default=None,
        metavar="TAG",
        help=f"从 *.<TAG>.* 恢复 breakdown/timeline，不重新 parse",
    )
    args = parser.parse_args()

    if args.restore_backup is not None:
        restored = restore_timeline_artifacts(args.indir, args.restore_backup)
        if not restored:
            print(f"[parse] 无备份可恢复: tag={args.restore_backup}", file=sys.stderr)
            return 1
        write_aggregation_marker(
            args.indir,
            {
                "timeline_aggregation": DEFAULT_BACKUP_TAG,
                "restored_from": args.restore_backup,
            },
        )
        print(f"[parse] restored {len(restored)} files from tag={args.restore_backup}")
        for p in restored:
            print(f"  - {p}")
        return 0

    timeline_agg = args.timeline_aggregation
    if timeline_agg is None:
        marker = read_aggregation_marker(args.indir)
        timeline_agg = (marker or {}).get("timeline_aggregation", TIMELINE_AGG_DEFAULT)

    if args.save_backup is not None:
        saved = backup_timeline_artifacts(args.indir, args.save_backup)
        if saved:
            print(f"[parse] backup tag={args.save_backup}: {len(saved)} files")

    profiles = load_rank_profiles(args.indir)
    case_params = _load_case_params(args.indir)
    agg = aggregate(
        profiles,
        case_params=case_params,
        timeline_aggregation=timeline_agg,
        timeline_rank=args.timeline_rank,
    )

    out_json = args.out_json or (args.indir / "breakdown.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(agg, f, indent=2)

    out_md = args.out_md or (args.indir / "BREAKDOWN.md")
    write_breakdown_md(agg, out_md)
    write_aggregation_marker(
        args.indir,
        {
            "timeline_aggregation": timeline_agg,
            "timeline_rank": args.timeline_rank if timeline_agg == "rank0" else None,
            "backup_tag": args.save_backup,
        },
    )
    print(f"[parse] {out_json} (timeline_aggregation={timeline_agg})")
    print(f"[parse] {out_md}")
    if agg["anomalies"]:
        print(f"[parse] WARN anomalies: {agg['anomalies']}", file=sys.stderr)
        if args.strict:
            return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
