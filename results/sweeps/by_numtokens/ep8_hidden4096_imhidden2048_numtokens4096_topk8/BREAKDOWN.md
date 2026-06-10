# dispatch_ffn_combine BREAKDOWN

- valid ranks: 8 [0, 1, 2, 3, 4, 5, 6, 7]
- profile version: 7
- timeline 聚合: relative_median
- prep skew (µs): median=549 [422, 676]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 422.0 | 549.0 | 676.0 | 0.0 | 549.0 | [0, 0] |
| dispatch | 1737.0 | 1752.5 | 1773.0 | 549.0 | 1752.5 | [549, 549] |
| swiglu | 2066.0 | 2115.0 | 2134.0 | 3042.0 | 2115.0 | [2968, 3237] |
| swiglu_w1 | 504.0 | 510.0 | 523.0 | 3042.0 | 510.0 | [2968, 3237] |
| swiglu_w2 | 435.0 | 443.0 | 449.0 | 4707.0 | 443.0 | [4654, 4906] |
| combine | 2004.0 | 2745.0 | 2766.0 | 7638.5 | 2745.0 | [7559, 7709] |
| gmm1 | 3438.0 | 3461.5 | 3502.0 | 1246.5 | 3461.5 | [1152, 1458] |
| gmm2 | 2268.0 | 2324.0 | 2351.0 | 5152.5 | 2324.0 | [5095, 5348] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
