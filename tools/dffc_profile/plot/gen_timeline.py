#!/usr/bin/env python3
"""根据 breakdown.json 生成 AIV/AIC 双轨 timeline PNG（完整版 + 聚焦版）。"""
from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Patch

from tools.dffc_profile.lib.paths import DFFC_ROOT, REPO_ROOT, ensure_repo_on_path, script_path

ensure_repo_on_path()

from tools.dffc_profile.lib.profile_constants import (
    AIC_PHASES,
    AIV_PHASES,
    HCCS_THEORETICAL_GBPS_PER_RANK as HCCS_BASELINE_GBPS,
    PHASE_NAMES,
    SWIGLU_WAVE_NAMES,
    TIMELINE_EXTRA_PHASES,
    UNPERMUTE_PHASE_NAME,
)

# comet 风格配色
PHASE_COLORS = {
    "prep": "#4C78A8",
    "dispatch": "#F58518",
    "swiglu": "#54A24B",
    "swiglu_w1": "#7CB342",
    "swiglu_w2": "#33691E",
    "swiglu_wait": "#A5D6A7",
    "expert_wait": "#E8ECF0",
    "combine": "#E45756",
    "combine_barrier": "#9B59B6",
    "unpermute": "#8E24AA",
    "gmm1": "#B279A2",
    "gmm2": "#72B7B2",
}

# 8 expert 独立色（与阶段色解耦，便于区分 e0–e7）
EXPERT_COLORS = (
    "#4E79A7",
    "#F28E2B",
    "#E15759",
    "#76B7B2",
    "#59A14F",
    "#EDC948",
    "#B07AA1",
    "#FF9DA7",
)

_EXPERT_PHASE_TRACKS = frozenset({"dispatch", "combine", "gmm1", "gmm2"})
# AIC 上 gmm 多核 min/max 墙钟可交叠，需串行摆放 active 避免假重叠
_AIC_PACK_PHASES = frozenset({"gmm1", "gmm2"})


def _expert_wall_nonmonotonic(segments: list[dict[str, Any]]) -> bool:
    """按 expert 序 wall_begin 是否倒退（多 AIC 核并行打点）。"""
    ordered = sorted(segments, key=lambda s: int(s.get("expert", 0)))
    prev_we: float | None = None
    for seg in ordered:
        wb = float(seg.get("wall_begin_us", 0))
        we = float(seg.get("wall_end_us", 0))
        if prev_we is not None and wb > 0 and wb < prev_we - 1:
            return True
        if we > 0:
            prev_we = we
    return False

def build_focus_breakdown(breakdown: dict) -> dict:
    """聚焦视图：不画 prep，时间轴以 dispatch 为 0；须字段同步平移。"""
    out = copy.deepcopy(breakdown)
    phases = out["phases"]
    dispatch_start = float(phases["dispatch"]["timeline_start_us"])

    # 含 unpermute，须与 expert_segments 同一 dispatch=0 坐标系
    for name in list(PHASE_NAMES) + list(TIMELINE_EXTRA_PHASES):
        if name == "prep" or name not in phases:
            continue
        row = phases[name]
        row["timeline_start_us"] = max(0.0, float(row["timeline_start_us"]) - dispatch_start)
        row["timeline_end_us"] = float(row["timeline_start_us"]) + float(row.get("timeline_duration_us", 0))
        for key in ("offset_min_us", "offset_max_us", "end_min_us", "end_max_us"):
            if key in row:
                row[key] = float(row[key]) - dispatch_start

    # v9 expert 段与阶段时间轴同步平移
    segs = out.get("expert_segments")
    if isinstance(segs, dict):
        shifted: dict[str, list[dict[str, Any]]] = {}
        for phase_name, rows in segs.items():
            shifted[phase_name] = []
            for seg in rows:
                s = dict(seg)
                for key in ("wall_begin_us", "wall_end_us"):
                    if key in s and s[key]:
                        s[key] = max(0.0, float(s[key]) - dispatch_start)
                shifted[phase_name].append(s)
        out["expert_segments"] = shifted
    return out


def _agg_subtitle(breakdown: dict) -> str:
    ver = breakdown.get("profile_version")
    base = f"profile v{ver}" if ver else "profile v5"
    if ver is not None and int(ver) >= 9:
        base += " | v9 per-expert active; hatch=expert wait"
    if breakdown.get("timeline_draw_mode") == "expert_active_only":
        base += " | bars=active only (no phase wall block)"
    elif ver is not None and int(ver) >= 8:
        base += " | gmm2/combine wall clock (may overlap)"
    agg = breakdown.get("timeline_aggregation")
    if agg == "relative_median":
        return f"{base} | agg=relative_median (median offset, whisker=[min,max])"
    if agg == "rank0":
        rk = breakdown.get("timeline_rank", 0)
        return f"{base} | data: rank{rk} profile only (no job agg)"
    if agg:
        return f"{base} | agg={agg}"
    return base


def _expert_color(expert: int, phase_name: str) -> str:
    """expert 条颜色：优先按 expert 索引，回退阶段色。"""
    if 0 <= expert < len(EXPERT_COLORS):
        return EXPERT_COLORS[expert]
    return PHASE_COLORS.get(phase_name, "#999999")


def _draw_hatch_gap(
    ax,
    x: float,
    w: float,
    y: float,
    bar_h: float,
    *,
    zorder: int = 4,
    label: str | None = None,
) -> None:
    """expert 间等待区：浅色底 + 细斜线。"""
    if w < 0.5:
        return
    gap_rect = FancyBboxPatch(
        (x, y - bar_h / 2),
        w,
        bar_h,
        boxstyle="round,pad=0.01,rounding_size=2",
        linewidth=0.5,
        edgecolor="#c5cad0",
        facecolor=PHASE_COLORS["expert_wait"],
        alpha=0.65,
        linestyle="-",
    )
    gap_rect.set_hatch("....")
    gap_rect.set_zorder(zorder)
    ax.add_patch(gap_rect)
    if label and w >= 120:
        ax.text(
            x + w / 2,
            y,
            label,
            ha="center",
            va="center",
            fontsize=6,
            color="#888888",
            style="italic",
            zorder=zorder + 1,
        )


def _draw_expert_active_only(
    ax,
    y: float,
    phase_name: str,
    segments: list[dict[str, Any]],
    phase_row: dict[str, Any],
    *,
    bar_h: float = 0.64,
    label_bars: bool = False,
    pack_aic_walls: bool = True,
    pack_aic_intra_phase: bool = True,
    packed_floor: float | None = None,
) -> tuple[float, float | None]:
    """仅画各 expert active 条；expert 间空隙保留，不画阶段墙钟大框。

    packed_floor：上一 AIC 阶段（如 gmm1）串行摆条后的尾部，保证 gmm2 不与 gmm1 e7 重叠。
    pack_aic_intra_phase=False 时阶段内始终用墙钟起点，仅跨阶段（gmm2 首 expert）接续 packed_floor。
    返回 (xmax, packed_tail)。
    """
    if not segments:
        return 0.0, packed_floor
    ordered = sorted(segments, key=lambda s: int(s.get("expert", 0)))
    xmax = 0.0
    prev_end: float | None = packed_floor
    packed_visual_tail = packed_floor if packed_floor is not None else 0.0
    if packed_floor is not None and pack_aic_walls:
        # 跨阶段：gmm2 从 gmm1 尾部接续，中间可画 wait
        first_wb = float(ordered[0].get("wall_begin_us", 0))
        if first_wb > packed_floor + 1:
            _draw_hatch_gap(ax, packed_floor, first_wb - packed_floor, y, bar_h, label="wait")

    for seg in ordered:
        wb = float(seg.get("wall_begin_us", 0))
        we = float(seg.get("wall_end_us", 0))
        active = float(seg.get("active_us", 0))
        expert = int(seg.get("expert", 0))
        if we < wb and active > 0:
            we = wb + active

        # v11：combine 每 expert 前 barrier（CrossCoreWait + SyncAll）
        has_barrier = False
        bb_f = be_f = 0.0
        if phase_name == "combine":
            bb_raw = seg.get("barrier_begin_us")
            be_raw = seg.get("barrier_end_us")
            if bb_raw is not None and be_raw is not None:
                bb_f = float(bb_raw)
                be_f = float(be_raw)
                if be_f > bb_f + 0.5:
                    has_barrier = True

        if has_barrier:
            if prev_end is not None and bb_f > prev_end + 1:
                _draw_hatch_gap(ax, prev_end, bb_f - prev_end, y, bar_h, label="wait")
            barrier_rect = FancyBboxPatch(
                (bb_f, y - bar_h / 2),
                be_f - bb_f,
                bar_h,
                boxstyle="round,pad=0.015,rounding_size=4",
                linewidth=1.0,
                edgecolor="#5B2C6F",
                facecolor=PHASE_COLORS["combine_barrier"],
                alpha=0.88,
            )
            barrier_rect.set_zorder(5)
            ax.add_patch(barrier_rect)
            xmax = max(xmax, be_f)
            packed_visual_tail = max(packed_visual_tail, be_f)
            if wb > be_f + 1:
                _draw_hatch_gap(ax, be_f, wb - be_f, y, bar_h, zorder=4)

        # AIC gmm：多核墙钟交叠时可串行摆 active；也可仅跨阶段接续
        x_draw = wb
        first_expert = int(ordered[0].get("expert", 0)) if ordered else -1
        cross_phase_start = (
            packed_floor is not None and expert == first_expert and pack_aic_walls
        )
        if pack_aic_walls and active >= 1:
            if pack_aic_intra_phase:
                if prev_end is not None:
                    if not has_barrier and wb > prev_end + 1:
                        _draw_hatch_gap(ax, prev_end, wb - prev_end, y, bar_h, label="wait")
                        x_draw = wb
                    else:
                        x_draw = wb if has_barrier else prev_end
                else:
                    x_draw = wb
            else:
                # 阶段内：墙钟起点（允许 expert 条交叠）
                x_draw = wb
                if cross_phase_start and wb < packed_floor:
                    x_draw = packed_floor
                elif prev_end is not None and not has_barrier and wb > prev_end + 1:
                    _draw_hatch_gap(ax, prev_end, wb - prev_end, y, bar_h, label="wait")
        elif prev_end is not None and not has_barrier and wb > prev_end + 1:
            # expert 间空隙（墙钟等待，非 active）
            _draw_hatch_gap(ax, prev_end, wb - prev_end, y, bar_h, label="wait")

        if active >= 1:
            color = _expert_color(expert, phase_name)
            rect = FancyBboxPatch(
                (x_draw, y - bar_h / 2),
                active,
                bar_h,
                boxstyle="round,pad=0.015,rounding_size=4",
                linewidth=1.0,
                edgecolor="#2d3436",
                facecolor=color,
                alpha=0.92,
            )
            rect.set_zorder(6)
            ax.add_patch(rect)
            if label_bars and active >= 50:
                fs = 7 if active >= 100 else 6
                ax.text(
                    x_draw + active / 2,
                    y,
                    f"e{expert}\n{active:.0f}µs",
                    ha="center",
                    va="center",
                    fontsize=fs,
                    color="white",
                    fontweight="bold",
                    zorder=7,
                )
            xmax = max(xmax, x_draw + active)
            packed_visual_tail = max(packed_visual_tail, x_draw + active)
            intra_end = x_draw + active
            # expert 内：active 结束 → 墙钟结束
            if we > intra_end + 1:
                _draw_hatch_gap(ax, intra_end, we - intra_end, y, bar_h, zorder=5)
            if has_barrier:
                prev_end = max(we, be_f) if we > 0 else be_f
            else:
                prev_end = we if we > 0 else intra_end
        else:
            if we > wb + 1:
                _draw_hatch_gap(ax, wb, we - wb, y, bar_h)
            prev_end = we if we > 0 else prev_end

    if ordered:
        xmax = max(xmax, float(ordered[-1].get("wall_end_us", 0)))
    packed_tail = packed_visual_tail if pack_aic_walls else None
    return xmax, packed_tail


def _draw_expert_segments(
    ax,
    y: float,
    phase_name: str,
    segments: list[dict[str, Any]],
    *,
    bar_h: float = 0.64,
) -> None:
    """旧版：在阶段大块内叠画 per-expert 子条（保留兼容）。"""
    if not segments:
        return
    base_color = PHASE_COLORS.get(phase_name, "#999999")
    sub_h = min(0.22, bar_h * 0.38)
    sub_y = y - bar_h / 2 + sub_h / 2 + 0.02
    ordered = sorted(segments, key=lambda s: int(s.get("expert", 0)))
    prev_end = None
    for seg in ordered:
        wb = float(seg.get("wall_begin_us", 0))
        we = float(seg.get("wall_end_us", 0))
        active = float(seg.get("active_us", 0))
        if we < wb and active > 0:
            we = wb + active
        if prev_end is not None and wb > prev_end + 2:
            _draw_hatch_gap(ax, prev_end, wb - prev_end, sub_y, sub_h)
        ax_w = active if active >= 1 else max(0.0, we - wb)
        ax_x = wb
        if ax_w < 1:
            prev_end = we if we > 0 else prev_end
            continue
        alpha = 0.55 + 0.35 * (int(seg.get("expert", 0)) % 4) / 3.0
        rect = FancyBboxPatch(
            (ax_x, sub_y - sub_h / 2),
            ax_w,
            sub_h,
            boxstyle="round,pad=0.01,rounding_size=2",
            linewidth=0.8,
            edgecolor="#333333",
            facecolor=base_color,
            alpha=min(0.98, alpha),
        )
        rect.set_zorder(6)
        ax.add_patch(rect)
        prev_end = we if we > 0 else ax_x + ax_w


def _draw_whisker(
    ax,
    y: float,
    x0: float,
    x1: float,
    color: str,
    *,
    cap_h: float = 0.12,
) -> None:
    """阶段起点/终点 min-max 误差须。"""
    if x1 < x0:
        x0, x1 = x1, x0
    if x1 - x0 < 0.5:
        return
    ax.plot([x0, x1], [y, y], color=color, linewidth=1.2, alpha=0.85, solid_capstyle="butt", zorder=5)
    ax.plot([x0, x0], [y - cap_h, y + cap_h], color=color, linewidth=1.2, alpha=0.85, zorder=5)
    ax.plot([x1, x1], [y - cap_h, y + cap_h], color=color, linewidth=1.2, alpha=0.85, zorder=5)


def load_bandwidth(case_dir: Path) -> dict[str, Any] | None:
    """读取同目录 bandwidth.json（可选）。"""
    fp = case_dir / "bandwidth.json"
    if not fp.is_file():
        return None
    with open(fp, encoding="utf-8") as f:
        return json.load(f)


def _bw_pct(gbps: float | None, baseline: float = HCCS_BASELINE_GBPS) -> str:
    if gbps is None or baseline <= 0:
        return "N/A"
    return f"{100.0 * gbps / baseline:.0f}%"


def _format_bandwidth_lines(bw: dict[str, Any] | None) -> list[str]:
    """per-rank 中位数 vs HCCS 392 GB/s；附 Job 级聚合吞吐。"""
    if not bw:
        return ["bandwidth: (no bandwidth.json)"]
    job = bw.get("job") or {}
    pr_d = (bw.get("per_rank_bw_dispatch_gbps") or {}).get("median")
    pr_c = (bw.get("per_rank_bw_combine_gbps") or {}).get("median")
    job_d = job.get("bw_dispatch_gbps")
    job_c = job.get("bw_combine_gbps")

    lines = [
        (
            f"dispatch  {pr_d:.0f} GB/s per-rank (median) = {_bw_pct(pr_d)} of HCCS {HCCS_BASELINE_GBPS:.0f} GB/s"
            if pr_d is not None
            else "dispatch  N/A"
        ),
        (
            f"combine   {pr_c:.0f} GB/s per-rank (median) = {_bw_pct(pr_c)} of HCCS {HCCS_BASELINE_GBPS:.0f} GB/s"
            if pr_c is not None
            else "combine   N/A"
        ),
    ]
    if job_d is not None and job_c is not None:
        ep = int((bw.get("case_params") or {}).get("ep", 0))
        ws_label = f"{ep} ranks" if ep > 0 else "job"
        lines.append(
            f"Job aggregate ({ws_label}): dispatch {job_d:.0f} GB/s  |  combine {job_c:.0f} GB/s"
        )
    return lines


def _swiglu_waves_ready(agg: dict) -> bool:
    """两波 SwiGLU 数据齐全时可分条绘制。"""
    ph = agg.get("phases", {})
    return all(ph.get(w, {}).get("timeline_duration_us", 0) >= 1 for w in SWIGLU_WAVE_NAMES)


def _aiv_phase_draw_order(agg: dict) -> list[str]:
    """AIV 轨绘制顺序：prep/dispatch → swiglu 等待区+两波 → combine → unpermute。"""
    names: list[str] = []
    ph = agg.get("phases", {})
    for n in PHASE_NAMES:
        if n not in AIV_PHASES:
            continue
        if n == "swiglu" and _swiglu_waves_ready(agg):
            names.extend(["swiglu", *SWIGLU_WAVE_NAMES])
        else:
            names.append(n)
        if n == "combine" and ph.get(UNPERMUTE_PHASE_NAME, {}).get("timeline_duration_us", 0) >= 1:
            names.append(UNPERMUTE_PHASE_NAME)
    return names


def _phase_legend_duration(agg: dict, name: str, row: dict[str, Any]) -> float:
    """图例时长：expert-active 模式用 sum(active)，否则用墙钟 duration。"""
    if agg.get("timeline_draw_mode") == "expert_active_only" and name in _EXPERT_PHASE_TRACKS:
        segs = (agg.get("expert_segments") or {}).get(name) or []
        active_sum = sum(float(s.get("active_us", 0)) for s in segs)
        if active_sum >= 1:
            return active_sum
    return float(row.get("timeline_duration_us", 0))


def _legend_items(
    agg: dict,
    phases: frozenset[str],
    *,
    skip_phases: frozenset[str] = frozenset(),
) -> list[tuple[str, float, str]]:
    items: list[tuple[str, float, str]] = []
    draw_names = _aiv_phase_draw_order(agg) if phases is AIV_PHASES else list(PHASE_NAMES)
    expert_only = agg.get("timeline_draw_mode") == "expert_active_only"
    for name in draw_names:
        if name not in phases or name in skip_phases:
            continue
        row = agg["phases"].get(name)
        if row is None:
            continue
        dur = _phase_legend_duration(agg, name, row)
        if dur < 1:
            continue
        label = name
        color = PHASE_COLORS.get(name, "#999999")
        if name == "swiglu" and _swiglu_waves_ready(agg):
            label = "swiglu (wall)"
            color = PHASE_COLORS["swiglu"]
        elif expert_only and name in _EXPERT_PHASE_TRACKS:
            label = f"{name} (Σactive)"
        items.append((label, dur, color))
    return items


def _draw_track(
    ax,
    y: float,
    phases: frozenset[str],
    agg: dict,
    label: str,
    *,
    skip_phases: frozenset[str] = frozenset(),
    label_bars: bool = False,
    min_label_us: float = 800.0,
    expert_active_only: bool = False,
    pack_aic_walls: bool = True,
    pack_aic_intra_phase: bool = True,
) -> float:
    ax.text(-0.02, y, label, transform=ax.get_yaxis_transform(), ha="right", va="center", fontsize=11)
    xmax = 0.0
    waves_ready = phases is AIV_PHASES and _swiglu_waves_ready(agg)
    draw_names = _aiv_phase_draw_order(agg) if phases is AIV_PHASES else list(PHASE_NAMES)
    sw_w1 = agg["phases"].get("swiglu_w1", {}) if waves_ready else {}
    sw_w2 = agg["phases"].get("swiglu_w2", {}) if waves_ready else {}
    w1_end = float(sw_w1.get("timeline_start_us", 0)) + float(sw_w1.get("timeline_duration_us", 0))
    w2_start = float(sw_w2.get("timeline_start_us", 0))
    # AIC gmm 串行摆条尾部：gmm2 必须接在 gmm1 之后，避免 e7/e0 假重叠
    aic_gmm_packed_tail: float | None = None

    for name in draw_names:
        if name not in phases or name in skip_phases:
            continue
        row = agg["phases"].get(name)
        if row is None:
            continue

        # 两波模式：w1/w2 分上下子轨；中间等待区单独画（避免大 K 时像一条 swiglu）
        bar_y = y
        bar_h = 0.64
        if waves_ready and name == "swiglu":
            gap_w = w2_start - w1_end
            if gap_w < 1:
                continue
            x, w = w1_end, gap_w
            color = PHASE_COLORS["swiglu_wait"]
            linestyle = "-"
            alpha = 0.55
            missing = False
            bar_label_suffix = ""
            zorder = 2
            hatch = "///"
            edge_lw = 0.8
            bar_name = "swiglu_wait"
            bar_y = y
            bar_h = 0.22
        elif waves_ready and name == "swiglu_w1":
            x = float(row["timeline_start_us"])
            w = float(row.get("timeline_duration_us", 0))
            missing = w < 1 or bool(row.get("insufficient_ranks"))
            color = PHASE_COLORS["swiglu_w1"]
            linestyle = "-"
            alpha = 0.96
            bar_label_suffix = ""
            zorder = 7
            hatch = None
            edge_lw = 1.5
            bar_name = name
            bar_y = y + 0.24
            bar_h = 0.28
        elif waves_ready and name == "swiglu_w2":
            x = float(row["timeline_start_us"])
            w = float(row.get("timeline_duration_us", 0))
            missing = w < 1 or bool(row.get("insufficient_ranks"))
            color = PHASE_COLORS["swiglu_w2"]
            linestyle = "-"
            alpha = 0.96
            bar_label_suffix = ""
            zorder = 7
            hatch = None
            edge_lw = 1.5
            bar_name = name
            bar_y = y - 0.24
            bar_h = 0.28
        else:
            x = float(row["timeline_start_us"])
            w = float(row.get("timeline_duration_us", 0))
            insufficient = bool(row.get("insufficient_ranks"))
            missing = w < 1 or insufficient
            color = PHASE_COLORS.get(name, "#999999")
            if missing:
                w = max(120.0, float(row.get("begin_us_median", 0)) * 0.02 + 80.0)
                linestyle = "--"
                alpha = 0.35
                bar_label_suffix = "\n(data?)" if insufficient else "\n(missing)"
            else:
                linestyle = "-"
                alpha = 0.92
                bar_label_suffix = ""
            zorder = 3
            hatch = None
            edge_lw = 0.8
            bar_name = name

        # v9 expert-active 模式：dispatch/combine/gmm 只画 active 条，不画阶段墙钟大块
        use_expert_only = (
            expert_active_only
            and bar_name in _EXPERT_PHASE_TRACKS
            and agg.get("expert_segments")
            and agg["expert_segments"].get(bar_name)
            and not missing
        )
        if use_expert_only:
            bar_y = y
            bar_h = 0.64
            segs = agg["expert_segments"][bar_name]
            # 默认仍可对非单调 AIC 墙钟串行摆条；--no-pack-aic-walls 时按原始时间轴画 active
            # AIC gmm 轨：始终串行摆 active，gmm2 接 gmm1 尾部，避免跨阶段墙钟假重叠
            pack_aic = (
                pack_aic_walls
                and bar_name in _AIC_PACK_PHASES
                and phases is AIC_PHASES
            )
            packed_floor = aic_gmm_packed_tail if bar_name == "gmm2" else None
            phase_xmax, packed_tail = _draw_expert_active_only(
                ax,
                bar_y,
                bar_name,
                segs,
                row,
                bar_h=bar_h,
                label_bars=label_bars,
                pack_aic_walls=pack_aic,
                pack_aic_intra_phase=pack_aic_intra_phase,
                packed_floor=packed_floor,
            )
            xmax = max(xmax, phase_xmax)
            if pack_aic and bar_name in _AIC_PACK_PHASES and packed_tail is not None:
                aic_gmm_packed_tail = packed_tail
            if not missing and agg.get("timeline_aggregation") == "relative_median":
                if "offset_min_us" in row and "offset_max_us" in row:
                    off_min = float(row["offset_min_us"])
                    off_max = float(row["offset_max_us"])
                    # gmm2 已串行接续 gmm1：起点须不早于 packed 尾部，避免须线穿入 gmm1 e7
                    if pack_aic and bar_name == "gmm2" and packed_floor is not None:
                        off_min = max(off_min, packed_floor)
                    if off_max > off_min + 0.5:
                        _draw_whisker(ax, bar_y, off_min, off_max, color)
                if "end_min_us" in row and "end_max_us" in row:
                    _draw_whisker(ax, bar_y, float(row["end_min_us"]), float(row["end_max_us"]), color)
            continue

        xmax = max(xmax, x + w)
        if name != "swiglu" or not waves_ready:
            if "end_max_us" in row:
                xmax = max(xmax, float(row["end_max_us"]))
            if "offset_max_us" in row:
                xmax = max(xmax, float(row["offset_max_us"]))
        elif waves_ready:
            xmax = max(xmax, w2_start + float(sw_w2.get("timeline_duration_us", 0)))
        rect = FancyBboxPatch(
            (x, bar_y - bar_h / 2),
            w,
            bar_h,
            boxstyle="round,pad=0.02,rounding_size=4",
            linewidth=edge_lw,
            edgecolor="#333333",
            facecolor=color,
            alpha=alpha,
            linestyle=linestyle,
        )
        if hatch:
            rect.set_hatch(hatch)
        rect.set_zorder(zorder)
        ax.add_patch(rect)

        # v9：dispatch/combine/gmm 轨内 per-expert 子条
        if (
            bar_name in _EXPERT_PHASE_TRACKS
            and agg.get("expert_segments")
            and agg["expert_segments"].get(bar_name)
            and not missing
        ):
            _draw_expert_segments(
                ax,
                bar_y,
                bar_name,
                agg["expert_segments"][bar_name],
                bar_h=bar_h,
            )
        # relative_median：起点/终点 min-max 须
        if not missing and agg.get("timeline_aggregation") == "relative_median":
            whisk_y = bar_y
            if "offset_min_us" in row and "offset_max_us" in row:
                _draw_whisker(ax, whisk_y, float(row["offset_min_us"]), float(row["offset_max_us"]), color)
            if "end_min_us" in row and "end_max_us" in row:
                _draw_whisker(ax, whisk_y, float(row["end_min_us"]), float(row["end_max_us"]), color)
            # prep 右端 skew 须（完整版）
            if name == "prep" and agg.get("prep_skew_us"):
                ps = agg["prep_skew_us"]
                _draw_whisker(ax, y, float(ps["min"]), float(ps["max"]), color)
        # focus 视图：条内标注阶段名 + 耗时
        if label_bars:
            wave_min = min_label_us * 0.25 if bar_name in SWIGLU_WAVE_NAMES else min_label_us
            if missing:
                bar_text = f"{bar_name}\n0 µs{bar_label_suffix}"
                fs = 7
            elif w >= wave_min:
                bar_text = f"{bar_name}\n{w:.0f} µs" if w >= wave_min * 1.8 else bar_name
                fs = 7 if bar_name in SWIGLU_WAVE_NAMES else 8
            else:
                bar_text = ""
            if bar_text:
                ax.text(
                    x + w / 2,
                    bar_y,
                    bar_text,
                    ha="center",
                    va="center",
                    fontsize=fs,
                    color="white",
                    fontweight="bold",
                    zorder=zorder + 1,
                )
    return xmax


def _draw_legend(ax, items: list[tuple[str, float, str]]) -> None:
    """图例：色块 + 阶段名 + 时长（µs）。"""
    ax.axis("off")
    if not items:
        return
    handles = [
        Patch(facecolor=color, edgecolor="#333333", label=f"{name}  {dur:.0f} µs")
        for name, dur, color in items
    ]
    ax.legend(
        handles=handles,
        loc="center",
        ncol=min(len(handles), 6),
        frameon=False,
        fontsize=10,
        handlelength=1.6,
        handleheight=1.0,
    )


def _draw_bandwidth(ax, bw: dict[str, Any] | None) -> None:
    """有效带宽脚注：per-rank vs HCCS 392 GB/s。"""
    ax.axis("off")
    lines = _format_bandwidth_lines(bw)
    text = "\n".join(lines)
    ax.text(
        0.5,
        0.5,
        text,
        transform=ax.transAxes,
        ha="center",
        va="center",
        fontsize=9.5,
        family="monospace",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="#f7f7f7", edgecolor="#cccccc"),
    )


def gen_png(
    breakdown: dict,
    out_path: Path,
    title: str,
    *,
    skip_phases: frozenset[str] = frozenset(),
    xlabel: str = "relative time (us), prep aligned to 0",
    label_bars: bool = False,
    bandwidth: dict[str, Any] | None = None,
    expert_active_only: bool = False,
    pack_aic_walls: bool = True,
    pack_aic_intra_phase: bool = True,
) -> None:
    draw_bd = breakdown
    if expert_active_only:
        draw_bd = copy.deepcopy(breakdown)
        draw_bd["timeline_draw_mode"] = "expert_active_only"

    # expert 图字小、条密，导出用更高 dpi
    fig_w = 16.0 if expert_active_only else 14.0
    fig_h = 6.8 if expert_active_only else 5.6
    fig = plt.figure(figsize=(fig_w, fig_h), facecolor="#fafbfc")
    gs = fig.add_gridspec(3, 1, height_ratios=[3.2, 0.9, 0.7], hspace=0.36)
    ax = fig.add_subplot(gs[0])
    lax = fig.add_subplot(gs[1])
    bax = fig.add_subplot(gs[2])

    ymax = _draw_track(
        ax, 1.0, AIV_PHASES, draw_bd, "AIV",
        skip_phases=skip_phases, label_bars=label_bars,
        expert_active_only=expert_active_only,
        pack_aic_walls=pack_aic_walls,
        pack_aic_intra_phase=pack_aic_intra_phase,
    )
    xmax = _draw_track(
        ax, 0.0, AIC_PHASES, draw_bd, "AIC",
        skip_phases=skip_phases, label_bars=label_bars,
        expert_active_only=expert_active_only,
        pack_aic_walls=pack_aic_walls,
        pack_aic_intra_phase=pack_aic_intra_phase,
    )
    xmax = max(ymax, xmax) * 1.05

    ax.set_xlim(0, xmax)
    ax.set_ylim(-0.6, 1.6)
    ax.set_xlabel(xlabel)
    ax.set_yticks([])
    subtitle = _agg_subtitle(breakdown)
    ax.set_title(f"{title}\n{subtitle}")
    # rank0 单 rank 出图时角标注明数据来源
    if breakdown.get("timeline_aggregation") == "rank0":
        rk = int(breakdown.get("timeline_rank", 0))
        ax.text(
            0.99,
            0.97,
            f"timeline source: rank{rk}",
            transform=ax.transAxes,
            ha="right",
            va="top",
            fontsize=8,
            color="#555555",
            style="italic",
            bbox=dict(boxstyle="round,pad=0.25", facecolor="white", edgecolor="#cccccc", alpha=0.85),
        )
    ax.set_facecolor("#fafbfc")
    ax.grid(axis="x", linestyle=":", alpha=0.35, color="#bdc3c7")
    if expert_active_only:
        # expert 色板图例角标
        for i, c in enumerate(EXPERT_COLORS[:8]):
            ax.scatter([], [], c=c, s=40, label=f"e{i}", edgecolors="#333")
        ax.legend(
            loc="upper right",
            ncol=4,
            fontsize=7,
            framealpha=0.9,
            title="expert",
            title_fontsize=8,
        )

    legend_items = _legend_items(draw_bd, AIV_PHASES | AIC_PHASES, skip_phases=skip_phases)
    _draw_legend(lax, legend_items)
    _draw_bandwidth(bax, bandwidth)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_dpi = 220 if expert_active_only else 200
    fig.savefig(out_path, dpi=out_dpi, bbox_inches="tight")
    plt.close(fig)
    print(f"[timeline] {out_path}")


def gen_timeline_pair(
    breakdown: dict,
    out_dir: Path,
    title_base: str,
    *,
    bandwidth: dict[str, Any] | None = None,
    expert_active_only: bool = False,
    out_stem: str = "timeline",
) -> None:
    """生成 timeline.png（完整）与 timeline_focus.png（去 prep）。"""
    bw = bandwidth if bandwidth is not None else load_bandwidth(out_dir)
    suffix = "_active" if expert_active_only else ""
    gen_png(
        breakdown,
        out_dir / f"{out_stem}{suffix}.png",
        f"{title_base}",
        xlabel="relative time (µs), prep = 0",
        label_bars=False,
        bandwidth=bw,
        expert_active_only=expert_active_only,
    )
    focus = build_focus_breakdown(breakdown)
    gen_png(
        focus,
        out_dir / f"{out_stem}_focus{suffix}.png",
        f"{title_base} (focus)",
        skip_phases=frozenset({"prep"}),
        xlabel="relative time (µs), dispatch = 0 (prep omitted, idle gaps kept)",
        label_bars=True,
        bandwidth=bw,
        expert_active_only=expert_active_only,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--breakdown", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=None, help="完整版 PNG；默认 <breakdown_dir>/timeline.png")
    parser.add_argument("--out-focus", type=Path, default=None, help="聚焦版 PNG；默认 <breakdown_dir>/timeline_focus.png")
    parser.add_argument("--title", default="dispatch_ffn_combine timeline")
    parser.add_argument("--focus-only", action="store_true", help="仅生成聚焦版")
    parser.add_argument("--full-only", action="store_true", help="仅生成完整版")
    parser.add_argument(
        "--expert-active-only",
        action="store_true",
        help="dispatch/combine/gmm 仅画 per-expert active 条，阶段墙钟大块+子条叠画改为斜线空白",
    )
    parser.add_argument(
        "--no-pack-aic-walls",
        action="store_true",
        help="gmm1/gmm2 不按 expert 序串行摆 active，直接用 profile 墙钟坐标",
    )
    args = parser.parse_args()
    pack_aic = not args.no_pack_aic_walls

    with open(args.breakdown, encoding="utf-8") as f:
        breakdown = json.load(f)

    out_dir = args.breakdown.parent
    bw = load_bandwidth(out_dir)
    stem = "timeline_active" if args.expert_active_only else "timeline"
    out_full = args.out or (out_dir / f"{stem}.png")
    out_focus = args.out_focus or (out_dir / f"{stem.replace('timeline', 'timeline_focus')}.png")
    if args.expert_active_only and args.out is None:
        out_focus = out_dir / "timeline_focus_active.png"

    if not args.focus_only:
        gen_png(
            breakdown,
            out_full,
            args.title,
            xlabel="relative time (µs), prep = 0",
            label_bars=False,
            bandwidth=bw,
            expert_active_only=args.expert_active_only,
            pack_aic_walls=pack_aic,
        )
    if not args.full_only:
        focus = build_focus_breakdown(breakdown)
        focus_title = args.title if args.title.endswith("(focus)") else f"{args.title} (focus)"
        gen_png(
            focus,
            out_focus,
            focus_title,
            skip_phases=frozenset({"prep"}),
            xlabel="relative time (µs), dispatch = 0 (prep omitted, idle gaps kept)",
            label_bars=True,
            bandwidth=bw,
            expert_active_only=args.expert_active_only,
            pack_aic_walls=pack_aic,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
