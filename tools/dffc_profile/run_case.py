#!/usr/bin/env python3
"""EP=8 单次 forward + profile 读回，输出 rank{r}_profile.json。"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
from pathlib import Path

import torch
import torch.distributed as dist
import torch.multiprocessing as mp
import torch_npu
from torch.distributed.distributed_c10d import _get_default_group

# 保证可 import tools.dffc_profile
_TOOLS_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _TOOLS_DIR.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from tools.dffc_profile.cases import CASES, DEFAULT_CASE, hccl_buffsize_mb
from tools.dffc_profile.profile_constants import (
    DFFC_PROFILE_MAGIC,
    DFFC_PROFILE_VERSION,
    DFFC_PROFILE_WORDS,
    PHASE_NAMES,
)
from vllm_ascend.utils import enable_custom_op

enable_custom_op()


def _get_hcomm(rank: int) -> str:
    pg = _get_default_group()
    if torch.__version__ > "2.0.1":
        return pg._get_backend(torch.device("npu")).get_hccl_comm_name(rank)
    return pg.get_hccl_comm_name(rank)


def _parse_profile_words(words: list[int]) -> dict:
    if len(words) < DFFC_PROFILE_WORDS:
        raise ValueError(f"profile words 不足: {len(words)} < {DFFC_PROFILE_WORDS}")
    magic, version = words[0], words[1]
    phases = {}
    for i, name in enumerate(PHASE_NAMES):
        b = words[2 + i * 2]
        e = words[2 + i * 2 + 1]
        phases[name] = {"begin_us": b, "end_us": e, "duration_us": max(0, e - b)}
    return {
        "magic": magic,
        "version": version,
        "phases": phases,
        "raw": words[:DFFC_PROFILE_WORDS],
    }


def _worker(rank: int, world_size: int, port: int, case_name: str, out_dir: Path) -> None:
    case = CASES.get(case_name, DEFAULT_CASE)
    torch_npu.npu.set_device(rank)
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
    # 尾部预留 profile 槽位
    expert_token_nums = torch.zeros(1, e + DFFC_PROFILE_WORDS, dtype=torch.int32).npu()

    torch.ops._C_ascend.dispatch_ffn_combine(
        x=x,
        weight1=weight1_list,
        weight2=weight2_list,
        expert_idx=expert_idx,
        bias1=torch.tensor([]),
        bias2=torch.tensor([]),
        scale1=scale1_list,
        scale2=scale2_list,
        probs=probs,
        group=hcomm,
        max_output_size=case.max_output_size,
        x_active_mask=x_active_mask,
        out=out,
        expert_token_nums=expert_token_nums,
    )
    torch.npu.synchronize()

    profile_words = expert_token_nums[0, e:].detach().cpu().tolist()
    payload = _parse_profile_words(profile_words)
    payload["rank"] = rank
    payload["case"] = case.name
    payload["ep"] = ep

    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"rank{rank}_profile.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    if rank == 0:
        print(f"[dffc] wrote {out_path} magic=0x{payload['magic']:08x} version={payload['version']}")

    dist.destroy_process_group()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", default="S1", choices=list(CASES.keys()))
    parser.add_argument("--world-size", type=int, default=8)
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--out-dir", type=Path, default=None)
    args = parser.parse_args()

    case = CASES[args.case]
    # 每 case 强制重置，避免串 case 污染
    os.environ["HCCL_BUFFSIZE"] = str(hccl_buffsize_mb(case))

    port = args.port or (29500 + random.randint(0, 9999))
    out_dir = args.out_dir or (_REPO_ROOT / ".dffc_profile" / "prof_dffc" / args.case)

    mp.spawn(
        _worker,
        args=(args.world_size, port, args.case, out_dir),
        nprocs=args.world_size,
        join=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
