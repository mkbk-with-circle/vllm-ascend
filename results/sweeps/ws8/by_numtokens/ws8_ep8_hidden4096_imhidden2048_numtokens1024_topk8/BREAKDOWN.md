# dispatch_ffn_combine BREAKDOWN

- valid ranks: 8 [0, 1, 2, 3, 4, 5, 6, 7]
- profile version: 10
- timeline 聚合: relative_median
- prep skew (µs): median=154 [125, 179]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 125.0 | 154.5 | 179.0 | 0.0 | 154.5 | [0, 0] |
| dispatch | 464.0 | 467.0 | 485.0 | 154.5 | 467.0 | [154, 154] |
| swiglu | 308.0 | 323.0 | 336.0 | 620.0 | 323.0 | [602, 652] |
| swiglu_w1 | 149.0 | 158.0 | 160.0 | 632.0 | 158.0 | [630, 662] |
| swiglu_w2 | 85.0 | 87.0 | 90.0 | 872.5 | 87.0 | [858, 898] |
| combine | 290.0 | 658.5 | 688.0 | 969.5 | 658.5 | [952, 994] |
| unpermute | 51.0 | 55.0 | 59.0 | 1766.5 | 55.0 | [1766, 1768] |
| gmm1 | 630.0 | 648.5 | 667.0 | 203.5 | 648.5 | [188, 212] |
| gmm2 | 334.0 | 352.0 | 368.0 | 839.0 | 352.0 | [814, 876] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
