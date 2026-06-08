# dispatch_ffn_combine 分阶段打点与 Timeline

宿主机隔离环境（无 Docker）下对 `dispatch_ffn_combine` 做 EP=8 分阶段墙钟打点，并生成 AIV/AIC 双轨 timeline。

## 环境准备

```bash
# 1. 项目内 conda（Python 3.10）
cd vllm-ascend
./.dffc_profile/miniconda3/bin/conda create -y -n dffc python=3.10 pip

# 2. 安装依赖（CANN 9.0 + README 指定版本）
source tools/dffc_profile/source_env.sh
pip install torch==2.10.0 torch-npu==2.10.0 matplotlib

# 3. 带 profile 重编 mc2
export DISPATCH_FFN_COMBINE_PROFILE=1
tools/dffc_profile/rebuild_mc2.sh
```

`source_env.sh` 会 `source` CANN（优先 9.0.0，回退 8.5.0），设置 `ASCEND_RT_VISIBLE_DEVICES=0-7`，**不修改** `~/.bashrc`。

## 六阶段定义

| 阶段 | 核 | 锚点 |
|------|-----|------|
| prep | AIV | mask → cumsum → expert_token_nums |
| dispatch | AIV | Pull 环 |
| gmm1 | AIC | `GMM1()` |
| swiglu | AIV | 两波 `blockEpilogue1` |
| gmm2 | AIC | `GMM2()` |
| combine | AIV | `CombineV1/V2` |

编译开关：`DISPATCH_FFN_COMBINE_PROFILE=1`（CMake `-DDISPATCH_FFN_COMBINE_PROFILE=ON` 或环境变量）。`=0` 时宏为空操作。

Profile GM 区在 **workspace 尾部** 256B；kernel 结束后拷到 `expert_token_nums[E:]` 供 host 读回。

## 一键命令

```bash
source tools/dffc_profile/source_env.sh

# EP=8 smoke
tools/dffc_profile/run_smoke.sh

# 单 case（默认 S1）+ JSON
python tools/dffc_profile/run_case.py --case S1

# 解析 + timeline
python tools/dffc_profile/parse_profile.py --indir .dffc_profile/prof_dffc/S1
python tools/dffc_profile/gen_timeline.py --breakdown .dffc_profile/prof_dffc/S1/breakdown.json

# 四 case 扫描
tools/dffc_profile/run_sweep.sh
```

## 聚合口径

- **块长度（墙钟）**：`max_rank(t_end - t_begin)`（straggler）
- **块起点**：`median_rank(t_begin) - t0`，`t0 = min(all prep_begin)`
- **异常**：某阶段 max duration &lt; 1µs 或 `begin==end`

## Case 网格

| Case | M | K | E | topK | max_output_size |
|------|---|---|---|------|-----------------|
| S1 | 1024 | 4096 | 2 | 8 | 16K |
| S2 | 8192 | 4096 | 2 | 8 | 64K |
| S3 | 8192 | 6144 | 2 | 8 | 64K |
| S4 | 8192 | 4096 | 2 | 16 | 128K |

每个 case 脚本会**重新计算并设置** `HCCL_BUFFSIZE`，避免串 case 污染。

## 已知坑

1. **UB 越界**：禁止在 UB scratch 或 `CopyGMToGMPerToken` 内层循环打点。
2. **AIV 全 0**：确认 AIV `coreIdx==0` 写戳、`profileGmOffset` 非 0、已用 `PROFILE=1` 重编。
3. **HCCL_BUFFSIZE**：case 间必须重置；过小会导致 tiling 失败。
4. **matplotlib**：若 pip 无 aarch64 wheel，可用 `conda install matplotlib`。
