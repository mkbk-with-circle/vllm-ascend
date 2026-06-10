"""profile JSON 解析：v2+ 相对时间 + duration 语义。"""
from __future__ import annotations

import statistics
from typing import Any

from tools.dffc_profile.profile_constants import (
    COMBINE_V1_M_TOPK_THRESHOLD,
    DFFC_AIC_MAX_CORES,
    DFFC_PROFILE_MAGIC,
    DFFC_PROFILE_SLOT_GMM1_BEGIN,
    DFFC_PROFILE_SLOT_GMM1_DUR_BASE,
    DFFC_PROFILE_SLOT_GMM1_END,
    DFFC_PROFILE_SLOT_GMM2_BEGIN,
    DFFC_PROFILE_SLOT_GMM2_END,
    PHASE_NAMES,
)

# dispatch→swiglu 间隔中 dispatch 活跃占比的经验系数（由 M=8192,K=6144 标定）
_DISPATCH_GAP_FRACTION = 0.36


def u32(v: int) -> int:
    return v & 0xFFFFFFFF


def phase_duration_us(version: int, begin: int, end: int) -> int:
    """v2+: end 槽存 active_duration；v1: end-begin。"""
    if version >= 2:
        return u32(end)
    b, e = sign_ext32(begin), sign_ext32(end)
    return max(0, e - b)


def sign_ext32(v: int) -> int:
    v &= 0xFFFFFFFF
    return v - 0x100000000 if v & 0x80000000 else v


def phase_begin_rel_us(version: int, begin: int) -> int:
    if version >= 2:
        return u32(begin)
    return sign_ext32(begin)


def _gmm_wall_from_raw(
    raw: list[int],
    prep0: int,
    begin_slot: int,
    end_slot: int,
) -> tuple[int, int, int] | None:
    """v5：从 BEGIN/END 辅助槽解析墙钟跨度。"""
    if len(raw) <= end_slot:
        return None
    b = u32(raw[begin_slot])
    e = u32(raw[end_slot])
    if b > 0 and e > b:
        begin = max(0, b - prep0)
        dur = e - b
        return begin, begin + dur, dur
    return None


def _gmm1_from_raw(raw: list[int], prep0: int, version: int) -> tuple[int, int, int] | None:
    if version >= 5:
        wall = _gmm_wall_from_raw(raw, prep0, DFFC_PROFILE_SLOT_GMM1_BEGIN, DFFC_PROFILE_SLOT_GMM1_END)
        if wall:
            return wall
        if version >= 6:
            return None
        # v5：仅有 END 或仅有 per-core active 时反推墙钟
        if len(raw) > DFFC_PROFILE_SLOT_GMM1_END:
            e_slot = u32(raw[DFFC_PROFILE_SLOT_GMM1_END])
            b_slot = u32(raw[DFFC_PROFILE_SLOT_GMM1_BEGIN])
            if e_slot > 0:
                e_rel = max(0, e_slot - prep0)
                if b_slot > 0 and e_slot > b_slot:
                    b_rel = max(0, b_slot - prep0)
                    return b_rel, e_rel, e_rel - b_rel
                gmm1_max = 0
                for i in range(DFFC_AIC_MAX_CORES):
                    d = u32(raw[DFFC_PROFILE_SLOT_GMM1_DUR_BASE + i])
                    gmm1_max = max(gmm1_max, d)
                if gmm1_max > 0:
                    b_rel = max(0, e_rel - gmm1_max)
                    return b_rel, e_rel, gmm1_max
    if len(raw) <= DFFC_PROFILE_SLOT_GMM1_BEGIN:
        return None
    slot_begin = u32(raw[DFFC_PROFILE_SLOT_GMM1_BEGIN])
    if slot_begin > 0:
        begin = max(0, slot_begin - prep0)
        phase_dur = u32(raw[3 + 4 * 2 + 1]) if len(raw) > 3 + 4 * 2 + 1 else 0
        dur = phase_dur
        return begin, begin + dur, dur
    return None


def _gmm2_from_raw(raw: list[int], prep0: int, version: int) -> tuple[int, int, int] | None:
    if version >= 5:
        wall = _gmm_wall_from_raw(raw, prep0, DFFC_PROFILE_SLOT_GMM2_BEGIN, DFFC_PROFILE_SLOT_GMM2_END)
        if wall:
            return wall
        if version >= 6:
            return None
    if len(raw) <= DFFC_PROFILE_SLOT_GMM2_BEGIN:
        return None
    slot_begin = u32(raw[DFFC_PROFILE_SLOT_GMM2_BEGIN])
    if slot_begin > 0:
        begin = max(0, slot_begin - prep0)
        phase_dur = u32(raw[3 + 5 * 2 + 1]) if len(raw) > 3 + 5 * 2 + 1 else 0
        dur = phase_dur
        return begin, begin + dur, dur
    return None


def _is_combine_v1(case_params: dict[str, Any] | None) -> bool:
    if not case_params:
        return True
    m = int(case_params.get("m", 0))
    topk = int(case_params.get("topk", 8))
    return m * topk > COMBINE_V1_M_TOPK_THRESHOLD


def repair_phases(
    phases: dict[str, dict[str, Any]],
    *,
    raw: list[int] | None = None,
    prep0: int = 0,
    version: int = 4,
    case_params: dict[str, Any] | None = None,
) -> None:
    """修复 export 后时间戳异常，并施加阶段因果约束。"""
    gmm1 = phases["gmm1"]
    gmm2 = phases["gmm2"]
    combine = phases["combine"]

    if raw:
        g1 = _gmm1_from_raw(raw, prep0, version)
        if g1:
            gmm1["begin_us"], gmm1["end_us"], gmm1["duration_us"] = g1
        g2 = _gmm2_from_raw(raw, prep0, version)
        if g2:
            gmm2["begin_us"], gmm2["end_us"], gmm2["duration_us"] = g2

    swiglu = phases["swiglu"]
    disp_end = int(phases["dispatch"].get("end_us", 0))
    sw_end = (
        int(swiglu["begin_us"]) + int(swiglu["duration_us"])
        if swiglu["duration_us"] >= 1
        else disp_end
    )

    if version >= 6:
        # v6 必须由 kernel 写真实 GMM 墙钟 BEGIN/END；缺失时不要用 active duration 反推。
        for gmm in (gmm1, gmm2):
            if gmm["duration_us"] >= 1 and gmm["begin_us"] < 1:
                gmm["duration_us"] = 0
                gmm["end_us"] = 0

    # v5 及更早：dur>0 但 begin 槽位缺失时保留历史反推逻辑
    if version < 6 and gmm1["duration_us"] >= 1 and gmm1["begin_us"] < 1:
        inferred = max(0, int(gmm1.get("end_us", 0)) - int(gmm1["duration_us"]))
        gmm1["begin_us"] = inferred if inferred >= 1 else max(disp_end, sw_end)
        gmm1["end_us"] = gmm1["begin_us"] + gmm1["duration_us"]

    if version < 6 and gmm2["duration_us"] >= 1 and gmm2["begin_us"] < 1:
        inferred = max(0, int(gmm2.get("end_us", 0)) - int(gmm2["duration_us"]))
        gmm2["begin_us"] = inferred if inferred >= 1 else sw_end
        gmm2["end_us"] = gmm2["begin_us"] + gmm2["duration_us"]

    # gmm2 首波须不早于 swiglu 结束
    if gmm2["duration_us"] >= 1 and swiglu["duration_us"] >= 1:
        if gmm2["begin_us"] < sw_end - 50:
            gmm2["begin_us"] = sw_end
            gmm2["end_us"] = gmm2["begin_us"] + gmm2["duration_us"]

    # gmm1 槽位全缺失时：用 dispatch→gmm2 流水线窗口估算
    if version < 6 and gmm1["duration_us"] < 1 and gmm2["duration_us"] >= 1:
        g2_begin = int(gmm2.get("begin_us", 0))
        if g2_begin > disp_end:
            gmm1["end_us"] = g2_begin
            gmm1["begin_us"] = disp_end
            gmm1["duration_us"] = g2_begin - disp_end

    # 同 rank 因果序
    if gmm1["duration_us"] >= 1 and gmm2["duration_us"] >= 1:
        if gmm2["begin_us"] < gmm1["begin_us"]:
            gmm2["begin_us"] = gmm1["begin_us"]
            gmm2["end_us"] = gmm2["begin_us"] + gmm2["duration_us"]

    if _is_combine_v1(case_params):
        if gmm2["duration_us"] >= 1 and combine["duration_us"] >= 1:
            if combine["begin_us"] < gmm2["end_us"]:
                shift = gmm2["end_us"] - combine["begin_us"]
                combine["begin_us"] += shift
                combine["end_us"] = combine["begin_us"] + combine["duration_us"]
    else:
        if gmm2["duration_us"] >= 1 and combine["duration_us"] >= 1:
            if combine["begin_us"] < gmm2["begin_us"]:
                shift = gmm2["begin_us"] - combine["begin_us"]
                combine["begin_us"] += shift
                combine["end_us"] = combine["begin_us"] + combine["duration_us"]


def pick_rank_profile(profiles: list[dict[str, Any]], rank: int = 0) -> dict[str, Any]:
    """选取指定 rank 的 profile；缺省时回退 rank0 文件或首个。"""
    for p in profiles:
        if p.get("rank") == rank:
            return p
    for p in profiles:
        src = str(p.get("source", ""))
        if src.startswith(f"rank{rank}_"):
            return p
    return profiles[0]


def aggregate_timeline_single_rank(
    profiles: list[dict[str, Any]],
    *,
    rank: int = 0,
) -> dict[str, dict[str, float | int]]:
    """timeline 直接取自单个 rank 的 per-phase begin/duration。"""
    pick = pick_rank_profile(profiles, rank)
    rows: dict[str, dict[str, float | int]] = {}
    for name in PHASE_NAMES:
        ph = pick["phases"][name]
        start = float(ph["begin_us"])
        dur = float(ph["duration_us"])
        rows[name] = {
            "timeline_start_us": start,
            "timeline_duration_us": dur,
            "timeline_end_us": start + dur,
            "timeline_n_ranks": 1,
        }
    return rows


def aggregate_timeline_relative_median(
    profiles: list[dict[str, Any]],
) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    """dispatch 锚定：相对偏移/时长取中位，prep 单列 skew；返回 phase rows + meta。"""
    prep_durs = [float(p["phases"]["prep"]["duration_us"]) for p in profiles]
    prep_skew = {
        "median": float(statistics.median(prep_durs)),
        "min": float(min(prep_durs)),
        "max": float(max(prep_durs)),
    }
    prep_lead = prep_skew["median"]

    rows: dict[str, dict[str, Any]] = {
        "prep": {
            "timeline_start_us": 0.0,
            "timeline_duration_us": prep_lead,
            "timeline_end_us": prep_lead,
            "offset_min_us": 0.0,
            "offset_max_us": 0.0,
            "end_min_us": prep_skew["min"],
            "end_max_us": prep_skew["max"],
            "timeline_n_ranks": len(profiles),
            "insufficient_ranks": False,
        }
    }

    for name in PHASE_NAMES:
        if name == "prep":
            continue

        offsets: list[float] = []
        durs: list[float] = []
        ends: list[float] = []
        for p in profiles:
            ph = p["phases"][name]
            anchor = float(p["phases"]["dispatch"]["begin_us"])
            if ph["duration_us"] >= 1 and ph["begin_us"] > 0:
                off = float(ph["begin_us"]) - anchor
                dur = float(ph["duration_us"])
                offsets.append(off)
                durs.append(dur)
                ends.append(off + dur)

        insufficient = len(offsets) < 3
        if offsets:
            med_off = float(statistics.median(offsets))
            med_dur = float(statistics.median(durs))
            off_min = float(min(offsets))
            off_max = float(max(offsets))
            end_min = float(min(ends))
            end_max = float(max(ends))
            n_ranks = len(offsets)
        else:
            med_off = med_dur = 0.0
            off_min = off_max = end_min = end_max = 0.0
            n_ranks = 0

        start = prep_lead + med_off
        rows[name] = {
            "timeline_start_us": start,
            "timeline_duration_us": med_dur,
            "timeline_end_us": start + med_dur,
            "offset_min_us": prep_lead + off_min,
            "offset_max_us": prep_lead + off_max,
            "end_min_us": prep_lead + end_min,
            "end_max_us": prep_lead + end_max,
            "timeline_n_ranks": n_ranks,
            "insufficient_ranks": insufficient,
        }

    meta = {
        "prep_skew_us": prep_skew,
        "prep_lead_us": prep_lead,
    }
    return rows, meta


def repair_aggregate_phases_tracked(
    agg_phases: dict[str, dict[str, Any]],
    *,
    case_params: dict[str, Any] | None = None,
) -> list[str]:
    """因果 repair 并返回被移动过的阶段名。"""
    snap = {
        name: (
            ph.get("timeline_start_us"),
            ph.get("timeline_duration_us"),
        )
        for name, ph in agg_phases.items()
    }
    repair_aggregate_phases(agg_phases, case_params=case_params)
    repaired: list[str] = []
    for name, ph in agg_phases.items():
        cur = (ph.get("timeline_start_us"), ph.get("timeline_duration_us"))
        if snap.get(name) != cur:
            repaired.append(name)
        ph["timeline_end_us"] = ph.get("timeline_start_us", 0) + ph.get("timeline_duration_us", 0)
        # repair 后右端须至少覆盖新 end
        if name in repaired and "end_max_us" in ph:
            ph["end_max_us"] = max(float(ph["end_max_us"]), float(ph["timeline_end_us"]))
            ph["end_min_us"] = min(float(ph["end_min_us"]), float(ph["timeline_end_us"]))
    return repaired


def aggregate_timeline_trimmed_by_duration(
    begins: list[float],
    ends: list[float],
    durs: list[float],
) -> tuple[float, float, int]:
    """job timeline：按 duration 去掉最小/最大各 1 rank，余下对 begin 与 duration 求均值。

    用于削弱 EP 负载不均导致的极端 rank（begin 跨度大、偶发 profile 异常）。
    n<=2 时退化为 begin/duration 中位数。
    返回 (timeline_start_us, timeline_duration_us, n_ranks_used)。
    """
    active = [
        (begins[i], ends[i], durs[i])
        for i in range(len(durs))
        if durs[i] >= 1
    ]
    good = [(b, e, d) for b, e, d in active if b > 0]
    pool = good if good else active
    if not pool:
        return 0.0, 0.0, 0
    if len(pool) <= 2:
        start = float(statistics.median([x[0] for x in pool]))
        dur = float(statistics.median([x[2] for x in pool]))
        return start, dur, len(pool)

    pool_sorted = sorted(pool, key=lambda x: (x[2], x[0]))
    trimmed = pool_sorted[1:-1]
    start = float(statistics.mean(x[0] for x in trimmed))
    dur = float(statistics.mean(x[2] for x in trimmed))
    return start, dur, len(trimmed)


def repair_profiles_batch(profiles: list[dict[str, Any]]) -> None:
    """跨 rank 修复 dispatch duration=0（单 rank 修完后仍可能全 0）。"""
    for p in profiles:
        raw = p.get("raw")
        prep0 = 0
        version = int(p.get("version", 4))
        case_params = p.get("case_params")
        if raw and len(raw) > 2:
            prep0 = int(p.get("phases", {}).get("prep", {}).get("begin_us", 0))
        repair_phases(
            p["phases"],
            raw=raw,
            prep0=prep0,
            version=version,
            case_params=case_params,
        )

    durs = [p["phases"]["dispatch"]["duration_us"] for p in profiles]
    if max(durs, default=0) >= 1:
        good = [d for d in durs if d >= 1]
        med = statistics.median(good)
        for p in profiles:
            d = p["phases"]["dispatch"]
            if d["duration_us"] < 1 and med >= 1:
                d["duration_us"] = int(med)
                d["end_us"] = d["begin_us"] + d["duration_us"]
        return

    gaps = []
    for p in profiles:
        d0 = p["phases"]["dispatch"]["begin_us"]
        s0 = p["phases"]["swiglu"]["begin_us"]
        if s0 > d0:
            gaps.append(s0 - d0)
    if not gaps:
        return
    est = int(statistics.median(gaps) * _DISPATCH_GAP_FRACTION)
    if est < 1:
        return
    for p in profiles:
        d = p["phases"]["dispatch"]
        if d["duration_us"] < 1:
            d["duration_us"] = est
            d["end_us"] = d["begin_us"] + est


def repair_aggregate_phases(
    agg_phases: dict[str, dict[str, Any]],
    *,
    case_params: dict[str, Any] | None = None,
) -> None:
    """job 级聚合后的因果约束。"""
    gmm1 = agg_phases["gmm1"]
    gmm2 = agg_phases["gmm2"]
    swiglu = agg_phases["swiglu"]
    combine = agg_phases["combine"]

    g1_start = gmm1.get("timeline_start_us", 0)
    g1_dur = gmm1.get("timeline_duration_us", 0)
    g1_end = g1_start + g1_dur

    g2_start = gmm2.get("timeline_start_us", 0)
    g2_dur = gmm2.get("timeline_duration_us", 0)
    g2_end = g2_start + g2_dur

    if g1_dur >= 1 and g2_dur >= 1 and g2_start < g1_start:
        gmm2["timeline_start_us"] = g1_start
        gmm2["timeline_duration_us"] = max(g2_dur, g2_end - g1_start)

    g2_start = gmm2.get("timeline_start_us", 0)
    g2_dur = gmm2.get("timeline_duration_us", 0)
    g2_end = g2_start + g2_dur

    sw_start = swiglu.get("timeline_start_us", 0)
    sw_dur = swiglu.get("timeline_duration_us", 0)
    if sw_dur >= 1 and g2_dur >= 1 and g2_start < sw_start:
        gmm2["timeline_start_us"] = sw_start
        gmm2["timeline_duration_us"] = max(g2_dur, g2_end - sw_start)

    g2_start = gmm2.get("timeline_start_us", 0)
    g2_dur = gmm2.get("timeline_duration_us", 0)
    g2_end = g2_start + g2_dur

    c_start = combine.get("timeline_start_us", 0)
    c_dur = combine.get("timeline_duration_us", 0)

    if g2_dur >= 1 and c_dur >= 1:
        if _is_combine_v1(case_params):
            if c_start < g2_end:
                combine["timeline_start_us"] = g2_end
        elif c_start < g2_start:
            combine["timeline_start_us"] = g2_start


def normalize_rank_profile(payload: dict) -> dict | None:
    """单 rank 归一化；magic 无效则丢弃；prep 对齐到 0。"""
    magic = payload.get("magic", 0)
    if magic != DFFC_PROFILE_MAGIC:
        return None
    version = int(payload.get("version", 1))
    phases_in = payload.get("phases", {})
    raw = payload.get("raw")
    case_params = payload.get("case_params")
    phases_out: dict[str, dict[str, Any]] = {}
    for name in PHASE_NAMES:
        p = phases_in.get(name, {})
        b_raw = int(p.get("begin_us", 0))
        e_raw = int(p.get("end_us", 0))
        dur = phase_duration_us(version, b_raw, e_raw)
        begin_rel = phase_begin_rel_us(version, b_raw)
        phases_out[name] = {
            "begin_us": begin_rel,
            "end_us": begin_rel + dur,
            "duration_us": dur,
        }

    # 以 prep 为 timeline 零点
    prep0 = phases_out["prep"]["begin_us"]
    for name in PHASE_NAMES:
        phases_out[name]["begin_us"] = max(0, phases_out[name]["begin_us"] - prep0)
        phases_out[name]["end_us"] = phases_out[name]["begin_us"] + phases_out[name]["duration_us"]

    repair_phases(
        phases_out,
        raw=raw,
        prep0=prep0,
        version=version,
        case_params=case_params,
    )

    out: dict[str, Any] = {
        "magic": magic,
        "version": version,
        "phases": phases_out,
        "rank": payload.get("rank"),
        "case": payload.get("case"),
        "ep": payload.get("ep"),
    }
    if raw:
        out["raw"] = raw
    if case_params:
        out["case_params"] = case_params
    return out
