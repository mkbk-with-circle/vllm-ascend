# Combine barrier 批量对比摘要

## 各 case per-rank median gap（µs）

| case | rank0 | rank1 | rank6 | rank7 | spread | tail_max |
|------|-------|-------|-------|-------|--------|----------|
| ws8_ep8_hidden7936_imhidden3968_numtoken… | 1683 | 1690 | 1196 | 1163 | 527 | 1 |
| ws8_ep8_hidden7680_imhidden3840_numtoken… | 1544 | 1574 | 1123 | 1154 | 451 | 1 |
| ws8_ep8_hidden7168_imhidden3584_numtoken… | 1348 | 1338 | 913 | 881 | 467 | 1 |
| ws8_ep8_hidden6144_imhidden3072_numtoken… | 1001 | 1014 | 519 | 510 | 506 | 1 |
| ws8_ep8_hidden4096_imhidden2048_numtoken… | 834 | 847 | 70 | 70 | 828 | 1 |

**解读**：`spread` = 同 case 内 rank0 与 rank6 的 median gap 差；`tail_max` 为全 rank 最大 `wall_end[e]→barrier_begin[e+1]`，全程 ≈1µs 说明 **combine expert 间无残留计时缝**。numtokens16384 的 rank6/7 gap 仅 ~70µs，是负载极不均下的真实短等待，不是打点错误。

## combine 轨 vs 图上其它「空隙」

| 位置 | 是什么 | 是否 combine 计时 bug |
|------|--------|----------------------|
| AIV combine 行：彩色 active 条之间 | v11 应用紫色 **barrier** 填满；数值 `gap≈barrier_w` | 否，原先 v10 未画 barrier |
| AIV combine 行：若仍见细 hatch | `tail_gap`（we→bb），实测 ≤1µs，肉眼难辨 | 否 |
| AIC gmm1/gmm2 行：expert 间 hatch | GMM 流水线墙钟；expert 可**重叠**（gap 可为负） | 与 combine 无关 |
| swiglu wait / gmm2→combine 之间 | 阶段级依赖等待 | 与 per-expert combine 无关 |

## 为何 rank1 gap 大、rank6 gap 小？

同一 case 内各 rank **dispatch 到的 token 分布不同** → 各 expert 的 GMM2 完成时刻不同 → combine 在 `CrossCoreWait` 上等 GMM2 的时长不同。

- **rank0/1** 往往承担更多/更早的 expert 计算，combine 更常等 GMM2 → barrier ~1.5–1.7ms（hidden7680/7936）
- **rank4/6/7** 负载较轻或 GMM2 与 combine 更贴合 → barrier ~0.5–1.1ms
- **numtokens16384**：rank6/7 median gap 仅 **70µs**（spread 828µs），极端不均，属真实调度而非计时

## 如何理解图上的「空隙」

1. **combine 轨（AIV）expert 之间**：数值上 `gap_viz ≈ barrier_width`，`tail_gap ≈ 0`。   v11 图里应看到紫色 barrier 条接上彩色 active 条；若仍见 hatch，多半是 **gmm1/gmm2 轨** 或 **阶段间**（swiglu wait、gmm2→combine）的空隙，不是 combine 计时 bug。
2. **rank 间 gap 大小不同**：各 rank 分到的 token / expert 负载不同，等 GMM2 的 CrossCoreWait 时长不同；
   hidden 越大、单 expert GMM2 越慢，barrier 越宽（rank0/1 往往略高于 rank4/6）。
3. **AIC gmm 轨 expert 间 hatch**：墙钟上 gmm1/gmm2 各 expert 可重叠也可串行等待，
   与 combine 的 barrier 无关；`--no-pack-aic-walls` 时按真实墙钟画，交叠处不会人为消除。

