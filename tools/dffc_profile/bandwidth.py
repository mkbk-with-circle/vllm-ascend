"""dispatch/combine 有效带宽：基于 expert_token_nums + profile 耗时。"""
from __future__ import annotations

import statistics
from pathlib import Path
from typing import Any

from tools.dffc_profile.profile_constants import UB_ALIGN


def bytes_per_token_dispatch(k: int) -> int:
    # peermem stride: K + UB_ALIGN
    return k + UB_ALIGN


def bytes_per_token_combine(k: int) -> int:
    # bf16 写回，n2 = K
    return k * 2


def _tokens_from_profile(rank_profile: dict[str, Any]) -> int:
    nums = rank_profile.get("expert_token_nums")
    if not nums:
        raise ValueError(f"rank{rank_profile.get('rank')} 缺少 expert_token_nums，需重跑 run_case")
    return int(sum(nums))


def _duration_us(rank_profile: dict[str, Any], phase: str) -> float:
    return float(rank_profile["phases"][phase]["duration_us"])


def calc_rank_bandwidth(rank_profile: dict[str, Any]) -> dict[str, Any]:
    params = rank_profile.get("case_params") or {}
    k = int(params.get("k", 0))
    if k <= 0:
        raise ValueError("case_params.k 无效")

    tokens = _tokens_from_profile(rank_profile)
    b_dispatch = tokens * bytes_per_token_dispatch(k)
    b_combine = tokens * bytes_per_token_combine(k)
    t_dispatch = _duration_us(rank_profile, "dispatch")
    t_combine = _duration_us(rank_profile, "combine")

    rank = rank_profile.get("rank")
    max_out = int(params.get("max_output_size", 0))
    truncation_warning = max_out > 0 and tokens >= max_out * 0.95

    def _bw(bytes_val: int, time_us: float) -> float | None:
        if time_us < 1.0:
            return None
        return bytes_val / time_us / 1e3  # GB/s

    return {
        "rank": rank,
        "tokens": tokens,
        "bytes_dispatch": b_dispatch,
        "bytes_combine": b_combine,
        "time_dispatch_us": t_dispatch,
        "time_combine_us": t_combine,
        "bw_dispatch_gbps": _bw(b_dispatch, t_dispatch),
        "bw_combine_gbps": _bw(b_combine, t_combine),
        "truncation_warning": truncation_warning,
    }


def _stats(values: list[float]) -> dict[str, float]:
    if not values:
        return {"min": 0.0, "median": 0.0, "max": 0.0, "mean": 0.0}
    return {
        "min": min(values),
        "median": statistics.median(values),
        "max": max(values),
        "mean": statistics.mean(values),
    }


def aggregate_bandwidth(
    rank_rows: list[dict[str, Any]],
    case_params: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if not rank_rows:
        raise ValueError("无 rank 带宽数据")

    total_b_dispatch = sum(r["bytes_dispatch"] for r in rank_rows)
    total_b_combine = sum(r["bytes_combine"] for r in rank_rows)
    t_dispatch_max = max(r["time_dispatch_us"] for r in rank_rows)
    t_combine_max = max(r["time_combine_us"] for r in rank_rows)

    def _job_bw(total_b: int, t_max: float) -> float | None:
        if t_max < 1.0:
            return None
        return total_b / t_max / 1e3

    bw_d = [r["bw_dispatch_gbps"] for r in rank_rows if r["bw_dispatch_gbps"] is not None]
    bw_c = [r["bw_combine_gbps"] for r in rank_rows if r["bw_combine_gbps"] is not None]

    warnings = [r["rank"] for r in rank_rows if r.get("truncation_warning")]

    params = case_params or {}
    return {
        "case_params": params,
        "bytes_per_token": {
            "dispatch": bytes_per_token_dispatch(int(params.get("k", 0))),
            "combine": bytes_per_token_combine(int(params.get("k", 0))),
        },
        "per_rank": rank_rows,
        "job": {
            "total_bytes_dispatch": total_b_dispatch,
            "total_bytes_combine": total_b_combine,
            "time_dispatch_us_max": t_dispatch_max,
            "time_combine_us_max": t_combine_max,
            "bw_dispatch_gbps": _job_bw(total_b_dispatch, t_dispatch_max),
            "bw_combine_gbps": _job_bw(total_b_combine, t_combine_max),
        },
        "per_rank_bw_dispatch_gbps": _stats(bw_d),
        "per_rank_bw_combine_gbps": _stats(bw_c),
        "truncation_warning_ranks": warnings,
    }


def load_rank_profiles_for_bandwidth(indir: Path) -> list[dict[str, Any]]:
    import json

    files = sorted(indir.glob("rank*_profile.json"))
    if not files:
        raise FileNotFoundError(f"未找到 profile: {indir}")
    out = []
    for fp in files:
        with open(fp, encoding="utf-8") as f:
            out.append(json.load(f))
    return out


def compute_bandwidth_from_dir(indir: Path) -> dict[str, Any]:
    profiles = load_rank_profiles_for_bandwidth(indir)
    case_params = profiles[0].get("case_params", {})
    rank_rows = [calc_rank_bandwidth(p) for p in profiles]
    return aggregate_bandwidth(rank_rows, case_params)
