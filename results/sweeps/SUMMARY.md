# dispatch_ffn_combine 参数 Sweep 数据总结与分析

> 环境：Ascend 910，`dispatch_ffn_combine` + profile v10  
> 数据目录：`results/sweeps/ws{N}/by_{numtokens,hidden,imhidden,topk}/`（`N ∈ {4,8,16}` 为 rank 数；`ep{E}` 为 expert-per-rank，grid 默认 `E=8`）  
> 趋势图：各轴 `summary_bandwidth.png`、`summary_timeline*.png`  
> 下文数值主要来自 **ws8**（19 个标准 grid case）；ws4/ws16 见同结构子目录

---

## 1. 度量口径（阅读本文前必读）

| 项目 | 定义 |
|------|------|
| **通信字节（单 rank）** | `sum(expert_token_nums) × bytes_per_token` |
| dispatch bytes/token | `K + 32`（int8 hidden + peermem scale 布局） |
| combine bytes/token | `K × 2`（bf16 写回） |
| **Job 有效带宽** | `sum_所有rank(bytes) / max_rank(阶段耗时)`，单位 GB/s |
| **阶段耗时** | profile `dispatch` / `combine` 的 `duration_us`（combine 已排除等 GMM2 的等待） |

Job 级带宽反映 **全网总流量 / 最慢 rank 完成时间**，适合看 EP=8 整体通信效率；与单链路物理带宽上限之间还有差距，因含 SyncAll、epilogue 等开销。

---

## 2. 总览

共完成 **4 条 sweep 轴、19 个有效 case**（另 **9 点**因 aicore 异常或打点异常未纳入趋势）。

| 轴 | 固定参数 | 遍历 | 有效点数 | 趋势图 |
|----|----------|------|----------|--------|
| numtokens | K=4096, N=4096, topk=8 | M=1K~16K | 5（1 点 dispatch 异常） | `ws8/by_numtokens/summary_bandwidth.png` |
| hidden | M=8192, topk=8, N=K | K=2K~8K | **8**（K≥8064 aicore 异常，**未达 HBM OOM**） | `ws8/by_hidden/summary_bandwidth.png` |
| imhidden | M=8192, K=4096, topk=8 | imhidden=1K~3K | 3（imhidden=4K 失败） | `ws8/by_imhidden/summary_bandwidth.png` |
| topk | M=8192, K=4096, N=4096 | topk=4,8,16 | 3 | `ws8/by_topk/summary_bandwidth.png` |

**跨轴共性（M≥4K、K=4096、topk=8 附近）：**

- **combine 有效带宽稳定高于 dispatch**，约 **770 vs 600 GB/s**（高约 25~30%）。
- 在 **token 数、topk、imhidden** 变化而 **K 不变** 时，Job 带宽大致 **平台化**（~600/770 GB/s），说明通信已接近当前实现下的 **带宽饱和区**。
- **hidden（K）** 是唯一显著拉高有效带宽的维度：K=6144 起 combine Job 带宽进入 **~1060–1127 GB/s 平台**；dispatch 仍随 K 上升至 K=8000 约 **975 GB/s**（Job 级）。单 rank 中位数 combine 约 **138–143 GB/s**，接近 HCCS 有效上限。
- **Job 级 1000+ GB/s** 为 8 rank 聚合吞吐（`sum(bytes)/max(time)`），对比硬件应看 **per-rank 中位数**（折线图虚线）。

---

## 3. 分轴数据表

### 3.1 by_numtokens（M 变化，K=4096, topk=8）

| M | 总 dispatch 字节 (8 rank) | max dispatch 耗时 (µs) | dispatch GB/s | combine GB/s | dispatch 阶段 median (µs) |
|---|---------------------------|------------------------|---------------|--------------|---------------------------|
| 1024 | 270 MB | 412 | **657** | 764 | 396 |
| 2048 | 541 MB | 0 ⚠️ | **N/A** | 778 | 0 ⚠️ |
| 4096 | 1.08 GB | 1776 | 609 | 771 | 1755 |
| 8192 | 2.16 GB | 3583 | 604 | 775 | 3520 |
| 16384 | 4.33 GB | 7100 | 610 | 772 | 7059 |

**趋势：**

- M 从 4K→16K：**dispatch/combine 带宽在 600~610 / 770~778 GB/s 窄幅波动**，几乎不随 batch 增大而提升。
- 通信总字节随 `M×topk` 近似线性增长，耗时也近似线性（例如 dispatch median：1.8ms→3.5ms→7.1ms），故 **带宽≈常数**（饱和）。
- M=1024 时 dispatch 略高（657 GB/s），符合 **小 payload 下固定同步开销占比大、算出来略“虚高”或波动大** 的现象。
- M=2048：**dispatch 各 rank duration 记为 0**（profile 异常），Job 带宽无法计算；combine 正常（778 GB/s）。该点 **不宜用于 dispatch 结论**。

### 3.2 by_hidden（K 变化，M=8192, topk=8, N=K）

| K | imhidden | 总 dispatch 字节 | max dispatch (µs) | dispatch Job GB/s | combine Job GB/s | per-rank dispatch | per-rank combine |
|---|----------|------------------|-------------------|-------------------|------------------|-------------------|------------------|
| 2048 | 1024 | 1.09 GB | 3133 | **348** | 455 | 44 | 59 |
| 4096 | 2048 | 2.16 GB | 3564 | **607** | 774 | 77 | 99 |
| 6144 | 3072 | 3.24 GB | 3995 | **811** | **1063** | 102 | 138 |
| 7168 | 3584 | 3.77 GB | 4224 | **894** | 1066 | 113 | 135 |
| 7680 | 3840 | 4.04 GB | 4338 | **932** | 1087 | 118 | 140 |
| 7936 | 3968 | 4.18 GB | 4383 | **953** | **1127** | 122 | 143 |
| 7968 | 3984 | 4.19 GB | 4303 | **975** | 1089 | 123 | 139 |
| **8000** | 4000 | 4.21 GB | 4346 | **969** | 1101 | 122 | 141 |

**未跑通（K≥7984 部分点，m=8192）：** 7984、8016、8064、8192、8448、10240、16384 → `aicore exception (507015)`（VEC UB 未对齐 / timeout），**非 HBM OOM**。本机 **m=8192 下最大可用 K=8000**。

**趋势：**

- **dispatch Job 带宽随 K 持续上升**（348→975 GB/s），耗时从 3.1ms→4.3ms，增幅小于字节增幅，单 token 传输效率提高。
- **combine Job 带宽在 K≥6144 后平台化**（1060–1127 GB/s）；per-rank combine 中位数稳定在 **~135–143 GB/s**（约为单卡 HCCS 392 GB/s 的 35%）。
- K 从 4096→6144（+50%）：dispatch 607→811（+34%），combine 774→1063（+37%），与早期结论一致。
- K=2048 明显低于平台（348/455 GB/s），小消息 + 固定开销主导。
- **继续增大 K 无法触及 OOM**：64GB HBM 在 m=8192 下估算占用仅 ~2 GB/rank；瓶颈在 **kernel 对大 K 的支持**，需修 tiling/对齐而非加显存。

### 3.3 by_imhidden（N/2 变化，K=4096 固定）

| imhidden | N | 总 dispatch 字节 | dispatch GB/s | combine GB/s |
|----------|---|------------------|---------------|--------------|
| 1024 | 2048 | 2.16 GB | 604 | 770 |
| 2048 | 4096 | 2.16 GB | 609 | 776 |
| 3072 | 6144 | 2.16 GB | 599 | 771 |
| 4096 | 8192 | — | **失败** | — |

**趋势：**

- 在 **K 固定** 时，改变 imhidden（FFN 中间维 N）**几乎不改变 dispatch/combine 通信量**（bytes/token 只依赖 K），三条有效曲线 **带宽均在 ~600/770 GB/s 平台**。
- 符合实现：`CopyGMToGMPerToken` Pull 的是 **K 维量化 token**；combine 写回 **K 维 bf16**，与 N/imhidden 无直接关系。
- **imhidden 主要影响 GMM/SwiGLU 计算**，而非本报告中的通信带宽；imhidden=4096（N=8192）在本机 **aicore 异常**，未出带宽数据。

### 3.4 by_topk（topk 变化，M=8192, K=4096）

| topk | 总 dispatch 字节 | max dispatch (µs) | dispatch GB/s | combine GB/s |
|------|------------------|-------------------|---------------|--------------|
| 4 | 1.08 GB | 1793 | 604 | 759 |
| 8 | 2.16 GB | 3562 | 608 | 784 |
| 16 | 4.33 GB | 7136 | 607 | 779 |

**趋势：**

- topk 翻倍 → 总字节翻倍 → 耗时近似翻倍 → **Job 带宽几乎恒定**（~604–608 / 759–784 GB/s）。
- 典型的 **已饱和链路**：增加路由 token 数只拉长阶段时间，不提高有效 GB/s。
- topk=8→16 时 combine 略降（784→779），在测量噪声范围内。

---

## 4. 综合分析

### 4.1 什么在驱动带宽？

```text
有效带宽 ≈ (路由 token 总数 × bytes_per_token) / 阶段活跃时间
```

| 变量 | 对通信字节的影响 | 对耗时的影响 | 对 Job 带宽的影响 |
|------|------------------|--------------|-------------------|
| **M / topk** | ∝ M×topk | 近似线性 | **平台化（饱和）** |
| **K (hidden)** | ∝ K | dispatch sub-linear；combine K≥6K 饱和 | **dispatch 随 K 升；combine 平台** |
| **imhidden (N)** | 几乎不变（K 固定） | 主要影响 GMM，非本阶段字节 | **平台化** |

### 4.2 dispatch vs combine

- 在同一 case 下，**combine Job 带宽 consistently 高于 dispatch**（约 +25~30%）。
- 每 token combine 搬运 **2× 字节**（bf16 vs int8+layout），但耗时增幅 **小于 2×**，因此 GB/s 更高。
- combine 路径为 `blockEpilogue` 写远端 peermem，dispatch 为 `CopyGMToGMPerToken` Pull；更高带宽可能来自 **写路径流水更满** 或 **计时边界内纯通信占比更高**（需 Level-3 kernel 字节计数验证）。

### 4.3 与 timeline 的关系

- **dispatch 活跃时间**远小于 **gmm1**（例如 M=8192、K=4096：dispatch ~3.5ms vs gmm1 数 ms~十余 ms，视 rank 而定），通信与计算 **流水线重叠**。
- 有效带宽只衡量 **AIV dispatch/combine 阶段内的 peermem 流量**，不包含 prep 里的 token 计数 AllGather，也不包含 unpermute。

### 4.4 数据质量与异常点

| 问题 | 影响 | 建议 |
|------|------|------|
| M=2048 dispatch duration=0 | dispatch Job 带宽为 null | 重跑或剔除；combine 仍可信 |
| imhidden=4096 aicore 异常 | 无带宽/timeline | 检查 N=8192 权重与 workspace 上限 |
| K≥8064（m=8192）aicore 异常 | hidden 轴 7 点失败 | kernel VEC UB 对齐/timeout；**非 OOM**；可用上限 **K=8000** |
| 部分 case gmm1 median=0 | 不影响带宽 JSON | profile 聚合问题，与通信分析无关 |

---

## 5. 结论与建议

### 结论

1. **在典型 LLM 形状（K=4096, M≥4K, topk=8）下，dispatch/combine 通信已进入带宽饱和区**，继续增大 batch 或 topk **不会** 明显提高 Job 级 GB/s，只会线性拉长通信阶段时间。
2. **增大 hidden（K）可显著提升 dispatch 有效带宽**（至 K=8000 约 **975 GB/s** Job / **123 GB/s** per-rank）；**combine 在 K≥6144 后饱和**（Job **~1060–1127 GB/s**，per-rank **~140 GB/s**）。
3. **单独增大 imhidden（N）不改变 dispatch/combine 通信带宽**，优化应聚焦 GMM/SwiGLU 计算而非 EP 通信。
4. **combine 通信效率略高于 dispatch**；Job 级 1000+ GB/s 为 8 卡聚合指标，物理对比用 per-rank 中位数（约为 HCCS 理论 392 GB/s 的 30–35%）。

### 后续优化方向（按优先级）

1. **大 batch / 大 topk**：优化方向是 **重叠与并行**（Pull 与 GMM1、combine 与 GMM2），而非期望更高 GB/s。
2. **大 hidden（K≥6K）**：combine 已饱和；dispatch 仍有上升空间但 **K>8000 触发 aicore 异常**，需修 kernel 对齐/tiling 后才能继续 sweep。
3. **度量增强**：Level-3 在 `CopyGMToGMPerToken` / `blockEpilogue` 内累加字节，分离 **纯 peermem 流量** 与 SyncAll 开销。
4. **修复 M=2048 profile 异常**、**imhidden=4096**、**K≥8064 kernel 异常**（VEC UB 对齐）。

---

## 6. 文件索引

| 路径 | 内容 |
|------|------|
| `by_*/manifest.json` | 各轴 case 列表 + Job 带宽摘要 |
| `by_*/summary_bandwidth.png` | dispatch/combine 带宽折线图（实线 Job，虚线 per-rank 中位数） |
| `by_*/<slug>/bandwidth.json` | 完整 per-rank + Job 聚合 |
| `by_*/<slug>/BANDWIDTH.md` | 单 case 带宽表 |
| `by_*/<slug>/timeline.png` | 完整六阶段 timeline（色块 + 图例；脚注带宽） |
| `by_*/<slug>/timeline_focus.png` | 去 prep、条内标注 µs；脚注带宽 |

---

## 7. Profile v5：AIC GMM 计时语义（2026-06-08）

| 阶段 | BEGIN | END | 计入 duration |
|------|-------|-----|----------------|
| **GMM1** | 首个 `currentM>0` 的 `blockMmad` 前 | GMM2 入口（`SYNCFLAGV2C` 前墙钟 END 槽） | 首 expert 后 Pull / expert 间等待、尾部 Pull |
| **GMM2** | 首个 `currentM>0` 的 `blockMmad` 前 | 函数末尾 `Stop` | 首 expert 后 `SYNCFLAGV2C` 等等待 |

**不计入**：cumsum、首个 expert 前 Pull/`SYNCFLAGV2C` 等待。

**聚合（job timeline）**：每阶段在 8 rank 上按 **duration 去掉最小/最大各 1 个 rank**，余下 6 rank 对 `begin_us` 与 `duration_us` **分别求均值** 作为 `timeline_start_us` / `timeline_duration_us`（削弱 EP 偏载与异常 rank；`n≤2` 退化为中位数）。`repair_aggregate_phases` 仍强制 gmm2≥swiglu、combine≥gmm2 等因果序。`begin_us_median` / `min`/`max` 统计字段保留。带宽 **不变**：Job 仍用 `max(duration)`（最慢 rank）算吞吐。

**流水线**：`e=2` 时 GMM2 可与 GMM1 后段交叠（`gmm2.begin` 不必 ≥ `gmm1.end`）。**CombineV1**（`m×topk>4096`）要求 `combine.begin ≥ gmm2.end`；**CombineV2** 要求 `combine.begin ≥ gmm2.begin`。

验收：`tools/dffc_profile/analysis/validate_profile.py --strict`；`dur=0` 在 `plot/gen_timeline.py` 以虚线框标注。

---

*生成说明：基于 `manifest.json` 与各 case `bandwidth.json` / `breakdown.json` 汇总；Job 带宽为主指标，per-rank 中位数用于硬件对比。by_hidden 已扩展至 K=8000；profile v5 重跑见 2026-06-08。*
