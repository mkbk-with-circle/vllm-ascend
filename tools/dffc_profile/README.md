# dispatch_ffn_combine 分阶段打点与 Timeline

宿主机环境下对 `dispatch_ffn_combine` 做 EP 分阶段墙钟打点，并生成 AIV/AIC 双轨 timeline。

> **新集群请先阅读 [`env/README.md`](env/README.md)**：CANN / conda / 重编算子 / 验证的完整搭建步骤。

## 目录结构

```
tools/dffc_profile/
├── README.md           # 本文件：工具用法与 timeline 语义
├── env/                # 环境搭建（独立 README）
├── lib/                # 共享库
├── pipeline/           # 跑 case / sweep
├── analysis/           # 解析、校验、审计
├── plot/               # timeline 与 sweep 图
└── maintain/           # 批量重生图 / 重跑 profile
```

| 子目录 | 内容 |
|--------|------|
| **env/** | `source_env.sh`、`install/*`、`build/rebuild_mc2.sh`、`verify/*` — 见 [env/README.md](env/README.md) |
| **lib/** | `cases.py`、`profile_constants.py`、`profile_utils.py`、`sweep_grids.py`、`bandwidth.py`、`paths.py` |
| **pipeline/** | `run_case.py`、`run_one_case.py`、`run_param_sweep.py` |
| **analysis/** | `parse_profile.py`、`validate_profile.py`、`calc_bandwidth.py`、`audit_profile_constraints.py`、`audit_combine_barrier_stitch.py` |
| **plot/** | `gen_timeline.py`、`gen_per_rank_timelines.py`、`gen_all_ranks_expert_focus_mosaic.py`、`plot_sweep_*.py` |
| **maintain/** | `regen_sweep_*`、`rerun_profile_cases.py`（批量重跑 / 仅重生图） |

## 常用命令

```bash
# 环境（详见 env/README.md）
source tools/dffc_profile/env/source_env.sh

# 冒烟
tools/dffc_profile/env/verify/smoke.sh

# 单 case 全流程：benchmark → parse → validate → timeline → 带宽
python tools/dffc_profile/pipeline/run_one_case.py \
  --m 8192 --k 4096 --n 4096 --e 8 --topk 8 --world-size 8 \
  --out-dir results/sweeps/ws8/by_topk/ws8_ep8_hidden4096_imhidden2048_numtokens8192_topk8

# 四轴参数 sweep
python tools/dffc_profile/pipeline/run_param_sweep.py --all --world-size 8

# 仅重生 per_rank expert_focus 图
python tools/dffc_profile/maintain/regen_sweep_per_rank_expert_focus.py \
  --sweeps-root results/sweeps -j 8 --skip-done

# profile 校验
python tools/dffc_profile/analysis/validate_profile.py --indir <case_dir> --strict
```

## 阶段与 Profile

| 阶段 | 核 | 说明 |
|------|-----|------|
| prep | AIV | mask → cumsum → expert_token_nums |
| dispatch | AIV | Pull 环 |
| gmm1 | AIC | GMM1 |
| swiglu | AIV | blockEpilogue1 |
| gmm2 | AIC | 各 expert tile |
| combine | AIV | 各 expert 通信 |
| unpermute | AIV | KernelMoeTokenUnpermute |

v11 在 combine 记录 `barrier_begin` / `barrier_end`（CrossCoreWait + SyncAll）。per-expert 槽位：`wall_begin`、`wall_end`、`active_us`。

## Timeline

实现于 `plot/gen_timeline.py`，数据来自 `breakdown.json` 或 `rank*_profile.json`。

| 输出 | 说明 |
|------|------|
| `timeline.png` | prep=0，阶段墙钟大块 |
| `timeline_focus.png` | dispatch=0 |
| `timeline_expert_focus.png` | 仅 expert active 条 + 空隙 hatch |

**双轨**：AIV（prep/dispatch/swiglu/combine/unpermute）+ AIC（gmm1/gmm2）。

per_rank 图默认保留 AIC 核间墙钟交叠；job 聚合图默认阶段内串行摆条避免假重叠。详见 `gen_per_rank_timelines.py --pack-aic-intra-phase`。

## 结果目录

`results/sweeps/ws{N}/by_<axis>/<slug>/`：

- `rank*_profile.json`、`breakdown.json`、`bandwidth.json`
- `timeline*.png`、`per_rank_timeline/`、`VALIDATION.md`

slug 格式：`ws{WS}_ep{E}_hidden{K}_imhidden{N/2}_numtokens{M}_topk{topK}`。

## Sweep 轴

| 轴 | 固定 | 遍历 |
|----|------|------|
| numtokens | K=4096, N=4096, topk=8, e=8 | M |
| hidden | M=8192, topk=8, e=8 | K |
| imhidden | M=8192, K=4096, topk=8, e=8 | imhidden |
| topk | M=8192, K=4096, N=4096, e=8 | topk |

## 带宽

- dispatch 分子：`sum(expert_token_nums) × (K + 32)`
- combine 分子：`sum(expert_token_nums) × K × 2`

## 已知限制

1. profile 需 `DISPATCH_FFN_COMBINE_PROFILE=1` 重编 mc2。
2. UB 内层循环禁止打点。
3. case 间须重置 `HCCL_BUFFSIZE`（`run_case.py` 已处理）。
4. ws16 等多 rank 场景 validate 默认非 strict。
