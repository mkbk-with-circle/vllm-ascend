#!/usr/bin/env python3
"""校验 profile breakdown 因果序与 v5 槽位完整性。"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from tools.dffc_profile.lib.paths import DFFC_ROOT, REPO_ROOT, ensure_repo_on_path, script_path

ensure_repo_on_path()

from tools.dffc_profile.analysis.parse_profile import load_rank_profiles, aggregate
from tools.dffc_profile.lib.profile_constants import (
    TIMELINE_AGG_DEFAULT,
    COMBINE_V1_M_TOPK_THRESHOLD,
    DFFC_PROFILE_SLOT_GMM1_BEGIN,
    DFFC_PROFILE_SLOT_GMM1_END,
    DFFC_PROFILE_SLOT_GMM2_BEGIN,
    DFFC_PROFILE_SLOT_GMM2_END,
    PHASE_NAMES,
    UNPERMUTE_PHASE_NAME,
)
from tools.dffc_profile.lib.profile_utils import u32
from tools.dffc_profile.lib.timeline_backup import read_aggregation_marker


def _is_combine_v1(case_params: dict | None) -> bool:
    if not case_params:
        return True
    return int(case_params.get("m", 0)) * int(case_params.get("topk", 8)) > COMBINE_V1_M_TOPK_THRESHOLD


def validate_indir(
    indir: Path,
    *,
    timeline_aggregation: str | None = None,
    timeline_rank: int = 0,
) -> tuple[list[str], list[str], dict]:
    profiles = load_rank_profiles(indir)
    case_params = None
    cp = indir / "case.json"
    if cp.is_file():
        case_params = json.loads(cp.read_text(encoding="utf-8"))
    if timeline_aggregation is None:
        marker = read_aggregation_marker(indir)
        timeline_aggregation = (marker or {}).get("timeline_aggregation", TIMELINE_AGG_DEFAULT)
        if marker and marker.get("timeline_rank") is not None:
            timeline_rank = int(marker["timeline_rank"])
    agg = aggregate(
        profiles,
        case_params=case_params,
        timeline_aggregation=timeline_aggregation,
        timeline_rank=timeline_rank,
    )
    issues: list[str] = []
    warnings: list[str] = []

    phases = agg["phases"]
    for name in PHASE_NAMES:
        row = phases[name]
        if row.get("insufficient_ranks"):
            warnings.append(
                f"job: {name} insufficient_ranks (n={row.get('timeline_n_ranks', 0)})"
            )
    g1 = phases["gmm1"]
    g2 = phases["gmm2"]
    comb = phases["combine"]

    if g1["timeline_duration_us"] < 1 and any(
        p["phases"]["gmm1"]["duration_us"] >= 1 for p in profiles
    ):
        issues.append("job: gmm1 timeline_duration=0")
    if g2["timeline_duration_us"] < 1 and any(
        p["phases"]["gmm2"]["duration_us"] >= 1 for p in profiles
    ):
        issues.append("job: gmm2 timeline_duration=0")

    sw = phases["swiglu"]
    profile_ver = int(profiles[0].get("version", 0)) if profiles else 0
    g1s, g1e = g1["timeline_start_us"], g1["timeline_start_us"] + g1["timeline_duration_us"]
    g2s, g2e = g2["timeline_start_us"], g2["timeline_start_us"] + g2["timeline_duration_us"]
    cs, ce = comb["timeline_start_us"], comb["timeline_start_us"] + comb["timeline_duration_us"]

    if g2["timeline_duration_us"] >= 1 and sw["timeline_duration_us"] >= 1 and g2s < sw["timeline_start_us"] - 1:
        msg = f"job: gmm2.start ({g2s:.0f}) < swiglu.start ({sw['timeline_start_us']:.0f})"
        if profile_ver >= 8:
            warnings.append(msg)
        else:
            issues.append(msg)
    sw_end = sw.get("timeline_start_us", 0) + sw.get("timeline_duration_us", 0)
    if g1.get("timeline_duration_us", 0) >= 1 and sw.get("timeline_duration_us", 0) >= 1:
        if sw_end < g1e - 50:
            issues.append(
                f"job: swiglu.end ({sw_end:.0f}) < gmm1.end ({g1e:.0f}) [wall clock]"
            )

    if g2["timeline_duration_us"] >= 1 and g2s < g1s - 1:
        issues.append(f"job: gmm2.start ({g2s:.0f}) < gmm1.start ({g1s:.0f})")

    # v8：combine 可与 gmm2 交叠，记录 overlap 供审查
    if (
        profile_ver >= 8
        and comb["timeline_duration_us"] >= 1
        and g2["timeline_duration_us"] >= 1
        and cs < g2e - 50
        and ce > g2s + 50
    ):
        overlap_us = min(ce, g2e) - max(cs, g2s)
        if overlap_us > 50:
            warnings.append(
                f"job: combine∥gmm2 overlap {overlap_us:.0f}µs "
                f"(combine [{cs:.0f},{ce:.0f}), gmm2 [{g2s:.0f},{g2e:.0f}))"
            )

    # v10：unpermute 须在 combine 结束之后
    if profile_ver >= 10:
        up = phases.get(UNPERMUTE_PHASE_NAME, {})
        if up.get("timeline_duration_us", 0) >= 1 and comb["timeline_duration_us"] >= 1:
            us = float(up["timeline_start_us"])
            if us < ce - 50:
                issues.append(
                    f"job: {UNPERMUTE_PHASE_NAME}.start ({us:.0f}) < combine.end ({ce:.0f})"
                )

    for p in profiles:
        rank = p.get("rank")
        ver = int(p.get("version", 0))
        ph = p["phases"]
        if ph["gmm1"]["duration_us"] >= 1 and ph["gmm2"]["duration_us"] >= 1:
            if ph["gmm2"]["begin_us"] < ph["gmm1"]["begin_us"]:
                # v8：首 expert GMM2 可与 GMM1 交叠，仅 warning
                msg = f"rank{rank}: gmm2.begin < gmm1.begin"
                if ver >= 8:
                    warnings.append(msg)
                else:
                    issues.append(msg)
        if ver >= 7 and ph["swiglu"]["duration_us"] >= 1 and ph["gmm1"]["duration_us"] >= 1:
            sw_e = ph["swiglu"]["begin_us"] + ph["swiglu"]["duration_us"]
            g1_e = ph["gmm1"]["begin_us"] + ph["gmm1"]["duration_us"]
            if sw_e < g1_e - 50:
                issues.append(f"rank{rank}: swiglu.end < gmm1.end (wall clock)")
            w2 = ph.get("swiglu_w2", {})
            if w2.get("duration_us", 0) >= 1 and w2.get("begin_us", 0) < g1_e - 50:
                # EP>8 时 GMM1 expert 墙钟可交叠，第二波 SwiGLU 可与末 expert 并行
                msg = f"rank{rank}: swiglu_w2.begin < gmm1.end (wait GMM1)"
                ep = int(p.get("ep") or (case_params or {}).get("ep") or len(profiles))
                if ep > 8:
                    warnings.append(msg)
                else:
                    issues.append(msg)
        if ph["swiglu"]["duration_us"] >= 1 and ph["gmm2"]["duration_us"] >= 1:
            if ph["gmm2"]["begin_us"] < ph["swiglu"]["begin_us"]:
                msg = f"rank{rank}: gmm2.begin < swiglu.begin"
                if ver >= 8:
                    warnings.append(msg)
                else:
                    issues.append(msg)
            if ver < 8:
                sw_end = ph["swiglu"]["begin_us"] + ph["swiglu"]["duration_us"]
                if ph["gmm2"]["begin_us"] < sw_end - 50:
                    issues.append(f"rank{rank}: gmm2.begin < swiglu.end (first-wave wait)")
        raw = p.get("raw") or []
        if ver >= 5 and ph["gmm1"]["duration_us"] >= 1 and ph["gmm1"]["begin_us"] < 1:
            if ph["gmm1"]["end_us"] != ph["gmm1"]["begin_us"] + ph["gmm1"]["duration_us"]:
                issues.append(f"rank{rank}: gmm1 begin=0 inconsistent with end/dur")
        if ver >= 5 and ph["gmm2"]["duration_us"] >= 1 and ph["gmm2"]["begin_us"] < 1:
            if ph["gmm2"]["end_us"] != ph["gmm2"]["begin_us"] + ph["gmm2"]["duration_us"]:
                issues.append(f"rank{rank}: gmm2 begin=0 inconsistent with end/dur")

        for name in PHASE_NAMES:
            row = ph[name]
            if row["duration_us"] >= 1:
                expect_end = row["begin_us"] + row["duration_us"]
                if abs(row.get("end_us", expect_end) - expect_end) > 2:
                    issues.append(f"rank{rank}: {name} end != begin+dur")

        # v9：per-expert 墙钟单调、active 不超过墙钟窗口
        if ver >= 9:
            segs = p.get("expert_segments") or {}
            for phase in ("dispatch", "combine", "gmm1", "gmm2"):
                rows = segs.get(phase) or []
                phase_wall = ph.get(phase, {}).get("duration_us", 0)
                sum_active = 0
                prev_end = -1
                for seg in rows:
                    wb = int(seg.get("wall_begin_us", 0))
                    we = int(seg.get("wall_end_us", 0))
                    act = int(seg.get("active_us", 0))
                    if wb > 0 and we > 0 and we < wb:
                        warnings.append(f"rank{rank}: {phase} e{seg.get('expert')} wall_end < wall_begin")
                    if prev_end >= 0 and wb > 0 and wb < prev_end - 1:
                        warnings.append(
                            f"rank{rank}: {phase} e{seg.get('expert')} wall_begin < prev wall_end"
                        )
                    if act > 0 and we > wb and act > we - wb + 50:
                        warnings.append(
                            f"rank{rank}: {phase} e{seg.get('expert')} active_us > wall span"
                        )
                    sum_active += act
                    if we > prev_end:
                        prev_end = we
                if phase_wall >= 1 and sum_active > phase_wall + 200:
                    warnings.append(
                        f"rank{rank}: {phase} sum(active_us)={sum_active} > phase dur {phase_wall}"
                    )

    return issues, warnings, agg


def write_validation_md(indir: Path, issues: list[str], warnings: list[str], agg: dict) -> Path:
    out = indir / "VALIDATION.md"
    lines = ["# Profile validation", ""]
    if issues:
        lines.append("## FAIL")
        for i in issues:
            lines.append(f"- {i}")
    else:
        lines.append("## PASS")
        lines.append("- 因果序检查通过")
    if warnings:
        lines.extend(["", "## WARN"])
        for w in warnings:
            lines.append(f"- {w}")
    lines.extend(["", "## Job timeline (µs)"])
    for name in PHASE_NAMES:
        r = agg["phases"][name]
        lines.append(
            f"- {name}: [{r['timeline_start_us']:.0f}, "
            f"{r['timeline_start_us'] + r['timeline_duration_us']:.0f}) "
            f"dur={r['timeline_duration_us']:.0f}"
        )
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--indir", type=Path, required=True)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    issues, warnings, agg = validate_indir(args.indir)
    md = write_validation_md(args.indir, issues, warnings, agg)
    print(f"[validate] {md}")
    for w in warnings:
        print(f"[validate] WARN: {w}", file=sys.stderr)
    if issues:
        for i in issues:
            print(f"[validate] FAIL: {i}", file=sys.stderr)
        return 2 if args.strict else 1
    print("[validate] PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
