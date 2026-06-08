#!/usr/bin/env python3
"""EP=8 benchmark：单进程 warmup + 多次 forward 取 profile 均值，输出 rank{r}_profile.json。"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
from pathlib import Path
from typing import Any

import torch
import torch.distributed as dist
import torch.multiprocessing as mp
import torch_npu
from torch.distributed.distributed_c10d import _get_default_group

from tools.dffc_profile.lib.paths import DFFC_ROOT, REPO_ROOT, ensure_repo_on_path, script_path

ensure_repo_on_path()

from tools.dffc_profile.lib.bootstrap_ops import bootstrap_custom_ops
from tools.dffc_profile.lib.cases import CASES, DffcCase, hccl_buffsize_mb, make_case
from tools.dffc_profile.lib.profile_constants import (
    DFFC_PROFILE_WORDS,
    PHASE_NAMES,
    SWIGLU_WAVE_NAMES,
    TIMELINE_EXTRA_PHASES,
)
from tools.dffc_profile.lib.profile_utils import (
    normalize_rank_profile,
    parse_expert_segments,
    repair_phases,
)

bootstrap_custom_ops(REPO_ROOT)

DEFAULT_WARMUP_ITERS = int(os.environ.get("DFFC_WARMUP", "10"))
DEFAULT_MEASURE_ITERS = int(os.environ.get("DFFC_ITERS", "50"))
SINGLE_FORWARD_WARMUP = 0
SINGLE_FORWARD_MEASURE = 1


def _get_hcomm(rank: int) -> str:
    pg = _get_default_group()
    if torch.__version__ > "2.0.1":
        return pg._get_backend(torch.device("npu")).get_hccl_comm_name(rank)
    return pg.get_hccl_comm_name(rank)


def _parse_profile_words(words: list[int]) -> dict:
    if len(words) < DFFC_PROFILE_WORDS:
        raise ValueError(f"profile words 不足: {len(words)} < {DFFC_PROFILE_WORDS}")
    raw = {
        "magic": words[0],
        "version": words[1],
        "t0_us": words[2],
        "phases": {},
        "raw": words[:DFFC_PROFILE_WORDS],
    }
    for i, name in enumerate(PHASE_NAMES):
        b = words[3 + i * 2]
        e = words[3 + i * 2 + 1]
        raw["phases"][name] = {"begin_us": b, "end_us": e}
    norm = normalize_rank_profile(raw)
    if norm is None:
        raise ValueError(f"profile magic 无效: 0x{words[0]:08x}")
    # 保留 export 原始槽位，便于核对 GMM BEGIN/END 辅助槽。
    norm["raw"] = raw["raw"]
    return norm


def _case_params_payload(case: DffcCase, ep: int) -> dict[str, Any]:
    return {
        "m": case.m,
        "k": case.k,
        "n": case.n,
        "imhidden": case.imhidden,
        "e": case.e,
        "topk": case.topk,
        "ep": ep,
        "max_output_size": case.max_output_size,
    }


def _average_profiles(
    profiles: list[dict[str, Any]],
    *,
    warmup_iters: int,
    measure_iters: int,
) -> dict[str, Any]:
    """测量轮次取均值；每阶段 begin/duration 仅对 duration>=1 的有效轮次平均。"""
    if not profiles:
        raise ValueError("profiles 为空")
    base = profiles[0]
    version = int(base.get("version", 5))
    case_params = base.get("case_params")
    n_valid_iters: dict[str, int] = {}
    phases: dict[str, dict[str, int]] = {}

    for name in PHASE_NAMES:
        valid = [p for p in profiles if p["phases"][name]["duration_us"] >= 1]
        n_valid_iters[name] = len(valid)
        if valid:
            begin_avg = sum(p["phases"][name]["begin_us"] for p in valid) / len(valid)
            dur_avg = sum(p["phases"][name]["duration_us"] for p in valid) / len(valid)
        else:
            begin_avg = 0.0
            dur_avg = 0.0
        begin_us = 0 if name == "prep" else int(round(begin_avg))
        duration_us = int(round(dur_avg))
        phases[name] = {
            "begin_us": begin_us,
            "duration_us": duration_us,
            "end_us": begin_us + duration_us,
        }

    raw_words = base.get("raw")
    prep0 = int(phases.get("prep", {}).get("begin_us", 0))
    repair_phases(
        phases,
        raw=raw_words,
        prep0=prep0,
        version=version,
        case_params=case_params,
    )
    # v7+：辅助阶段（SwiGLU 两波、v10 unpermute）对有效轮次取均值
    for wname in TIMELINE_EXTRA_PHASES:
        valid_w = [p for p in profiles if p.get("phases", {}).get(wname, {}).get("duration_us", 0) >= 1]
        if not valid_w:
            continue
        b_avg = sum(p["phases"][wname]["begin_us"] for p in valid_w) / len(valid_w)
        d_avg = sum(p["phases"][wname]["duration_us"] for p in valid_w) / len(valid_w)
        begin_us = int(round(b_avg))
        duration_us = int(round(d_avg))
        phases[wname] = {
            "begin_us": begin_us,
            "duration_us": duration_us,
            "end_us": begin_us + duration_us,
        }

    expert_token_nums = [int(x) for x in (base.get("expert_token_nums") or [])]

    out = {
        "magic": base.get("magic"),
        "version": base.get("version"),
        "phases": phases,
        "rank": base.get("rank"),
        "case": base.get("case"),
        "ep": base.get("ep"),
        "expert_token_nums": expert_token_nums,
        "case_params": case_params,
        "profile_iters": {"warmup": warmup_iters, "measure": measure_iters},
        "n_valid_iters": n_valid_iters,
    }
    # 保留首轮 raw 槽位，便于核对 GMM BEGIN/END 辅助槽
    if base.get("raw"):
        out["raw"] = base["raw"]
    e = int((case_params or {}).get("e", 0))
    if base.get("raw") and e > 0 and version >= 9:
        segs = parse_expert_segments(
            base["raw"],
            expert_per_rank=e,
            prep0=prep0,
            version=version,
            expert_token_nums=expert_token_nums,
        )
        if segs:
            out["expert_segments"] = segs
    return out


def _zero_profile_buf(expert_token_nums: torch.Tensor, e: int) -> None:
    """host 侧清零 export 区；kernel export 后会封印 workspace magic。"""
    expert_token_nums[0, e:].zero_()
    torch.npu.synchronize()


def _dispatch_forward(
    *,
    case: DffcCase,
    hcomm: str,
    x: torch.Tensor,
    weight1_list: list,
    weight2_list: list,
    expert_idx: torch.Tensor,
    scale1_list: list,
    scale2_list: list,
    probs: torch.Tensor,
    x_active_mask: torch.Tensor,
    out: torch.Tensor,
    expert_token_nums: torch.Tensor,
    e: int,
) -> None:
    _zero_profile_buf(expert_token_nums, e)
    torch.ops._C_ascend.dispatch_ffn_combine(
        x=x,
        weight1=weight1_list,
        weight2=weight2_list,
        expert_idx=expert_idx,
        scale1=scale1_list,
        scale2=scale2_list,
        bias1=None,
        bias2=None,
        probs=probs,
        group=hcomm,
        max_output_size=case.max_output_size,
        x_active_mask=x_active_mask,
        out=out,
        expert_token_nums=expert_token_nums,
    )
    torch.npu.synchronize()


def _read_profile_payload(
    expert_token_nums: torch.Tensor,
    e: int,
    *,
    rank: int,
    case: DffcCase,
    ep: int,
) -> dict[str, Any]:
    token_counts = expert_token_nums[0, :e].detach().cpu().tolist()
    profile_words = expert_token_nums[0, e:].detach().cpu().tolist()
    payload = _parse_profile_words(profile_words)
    payload["rank"] = rank
    payload["case"] = case.name
    payload["ep"] = ep
    payload["expert_token_nums"] = [int(x) for x in token_counts]
    payload["case_params"] = _case_params_payload(case, ep)
    return payload


def _worker(
    rank: int,
    world_size: int,
    port: int,
    case_dict: dict,
    out_dir: str,
    warmup_iters: int,
    measure_iters: int,
) -> None:
    """单进程：张量构造一次，warmup + measure 循环复用 HCCL。"""
    case = DffcCase.from_dict(case_dict)
    out_path_dir = Path(out_dir)
    torch_npu.npu.set_device(rank)
    bootstrap_custom_ops(REPO_ROOT)
    dist.init_process_group(
        backend="hccl",
        rank=rank,
        world_size=world_size,
        init_method=f"tcp://127.0.0.1:{port}",
    )
    hcomm = _get_hcomm(rank)

    m, k, n = case.m, case.k, case.n
    topk = case.topk
    e = case.expert_per_rank
    k2 = n // 2
    n2 = k
    ep = world_size

    torch_npu.npu.config.allow_internal_format = True
    torch.manual_seed(42 + rank)
    x = torch.randn(m, k, dtype=torch.bfloat16).npu()
    weight1 = torch.randint(-128, 127, (e, k, n), dtype=torch.int8).npu()
    weight1 = torch_npu.npu_format_cast(weight1, 29)
    weight2 = torch.randint(-128, 127, (e, k2, n2), dtype=torch.int8).npu()
    weight2 = torch_npu.npu_format_cast(weight2, 29)

    expert_idx = torch.randint(0, ep * e, (m, topk), dtype=torch.int32).npu()
    scale1 = torch.randint(0, 1, (e, n), dtype=torch.int64).npu()
    scale2 = torch.randint(0, 1, (e, n2), dtype=torch.int64).npu()
    probs = torch.randn(m, topk, dtype=torch.float32).npu()
    x_active_mask = torch.ones(m, dtype=torch.bool).npu()

    weight1_list = [torch_npu.npu_format_cast(weight1[i], 29) for i in range(e)]
    scale1_list = [scale1[i] for i in range(e)]
    weight2_list = [torch_npu.npu_format_cast(weight2[i], 29) for i in range(e)]
    scale2_list = [scale2[i] for i in range(e)]

    out = torch.empty(m, k, dtype=torch.bfloat16).npu()
    expert_token_nums = torch.zeros(1, e + DFFC_PROFILE_WORDS, dtype=torch.int32).npu()

    fwd_kw = dict(
        case=case,
        hcomm=hcomm,
        x=x,
        weight1_list=weight1_list,
        weight2_list=weight2_list,
        expert_idx=expert_idx,
        scale1_list=scale1_list,
        scale2_list=scale2_list,
        probs=probs,
        x_active_mask=x_active_mask,
        out=out,
        expert_token_nums=expert_token_nums,
        e=e,
    )

    try:
        for _ in range(warmup_iters):
            _dispatch_forward(**fwd_kw)

        measure_profiles: list[dict[str, Any]] = []
        for _ in range(measure_iters):
            _dispatch_forward(**fwd_kw)
            measure_profiles.append(
                _read_profile_payload(expert_token_nums, e, rank=rank, case=case, ep=ep)
            )
    except Exception:
        dist.destroy_process_group()
        raise

    payload = _average_profiles(
        measure_profiles,
        warmup_iters=warmup_iters,
        measure_iters=measure_iters,
    )

    out_path_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_path_dir / f"rank{rank}_profile.json"
    tmp_path = out_path_dir / f"rank{rank}_profile.json.tmp"
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        tmp_path.replace(out_path)
    except Exception:
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)
        raise

    if rank == 0:
        tag = "single forward" if measure_iters == 1 and warmup_iters == 0 else f"mean×{measure_iters}"
        print(f"[dffc] wrote {out_path} warmup={warmup_iters} measure={measure_iters} ({tag})")

    dist.destroy_process_group()


def resolve_case_from_args(args: argparse.Namespace) -> DffcCase:
    if args.m is not None:
        return make_case(
            name=args.name or "custom",
            m=args.m,
            k=args.k,
            n=args.n,
            e=args.e,
            topk=args.topk,
            max_output_size=args.max_output_size,
        )
    return CASES[args.case]


def run_case(
    case: DffcCase,
    world_size: int,
    out_dir: Path,
    port: int = 0,
    *,
    warmup_iters: int = DEFAULT_WARMUP_ITERS,
    measure_iters: int = DEFAULT_MEASURE_ITERS,
) -> Path:
    os.environ["HCCL_BUFFSIZE"] = str(hccl_buffsize_mb(case))
    port = port or (29500 + random.randint(0, 9999))
    out_dir.mkdir(parents=True, exist_ok=True)
    case_payload = case.to_dict()
    case_payload["profile_iters"] = {
        "warmup": warmup_iters,
        "measure": measure_iters,
    }
    with open(out_dir / "case.json", "w", encoding="utf-8") as f:
        json.dump(case_payload, f, indent=2)

    mp.spawn(
        _worker,
        args=(world_size, port, case.to_dict(), str(out_dir), warmup_iters, measure_iters),
        nprocs=world_size,
        join=True,
    )
    return out_dir


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", default="S1", choices=list(CASES.keys()))
    parser.add_argument("--name", default=None, help="自定义 case 名（与 --m 联用）")
    parser.add_argument("--m", type=int, default=None)
    parser.add_argument("--k", type=int, default=None)
    parser.add_argument("--n", type=int, default=None, help="FFN 输出宽；默认等于 k")
    parser.add_argument("--e", type=int, default=2)
    parser.add_argument("--topk", type=int, default=8)
    parser.add_argument("--max-output-size", type=int, default=None)
    parser.add_argument("--world-size", type=int, default=8)
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--out-dir", type=Path, default=None)
    parser.add_argument("--warmup", type=int, default=DEFAULT_WARMUP_ITERS)
    parser.add_argument("--measure-iters", type=int, default=DEFAULT_MEASURE_ITERS)
    parser.add_argument("--single-forward", action="store_true")
    args = parser.parse_args()

    if args.single_forward:
        args.warmup = SINGLE_FORWARD_WARMUP
        args.measure_iters = SINGLE_FORWARD_MEASURE

    if args.m is not None:
        if args.k is None:
            parser.error("--m 需配合 --k")
        case = resolve_case_from_args(args)
    else:
        case = CASES[args.case]

    out_dir = args.out_dir or (REPO_ROOT / "results" / "dffc" / case.result_slug(args.world_size))
    run_case(
        case,
        args.world_size,
        out_dir,
        args.port,
        warmup_iters=args.warmup,
        measure_iters=args.measure_iters,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
