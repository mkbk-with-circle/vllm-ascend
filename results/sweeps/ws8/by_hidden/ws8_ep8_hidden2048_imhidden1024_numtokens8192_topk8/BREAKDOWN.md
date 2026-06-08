# dispatch_ffn_combine BREAKDOWN

- valid ranks: 8 [0, 1, 2, 3, 4, 5, 6, 7]
- profile version: 10
- timeline 聚合: relative_median
- prep skew (µs): median=714 [638, 788]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 638.0 | 713.5 | 788.0 | 0.0 | 713.5 | [0, 0] |
| dispatch | 3189.0 | 3257.0 | 3303.0 | 713.5 | 3257.0 | [714, 714] |
| swiglu | 1490.0 | 1502.0 | 1521.0 | 3784.0 | 1502.0 | [3712, 3950] |
| swiglu_w1 | 900.0 | 909.0 | 918.0 | 3972.5 | 909.0 | [3904, 4020] |
| swiglu_w2 | 586.0 | 596.0 | 601.0 | 4882.5 | 596.0 | [4808, 4940] |
| combine | 2134.0 | 4572.0 | 4657.0 | 5481.0 | 4572.0 | [5404, 5548] |
| unpermute | 344.0 | 348.5 | 354.0 | 10404.0 | 348.5 | [10400, 10408] |
| gmm1 | 3070.0 | 3142.0 | 3181.0 | 972.0 | 3142.0 | [836, 1122] |
| gmm2 | 1449.0 | 1476.5 | 1643.0 | 4683.0 | 1476.5 | [4534, 4758] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
