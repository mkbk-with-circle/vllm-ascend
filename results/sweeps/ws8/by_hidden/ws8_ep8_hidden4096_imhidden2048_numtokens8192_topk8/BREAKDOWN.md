# dispatch_ffn_combine BREAKDOWN

- valid ranks: 8 [0, 1, 2, 3, 4, 5, 6, 7]
- profile version: 10
- timeline 聚合: relative_median
- prep skew (µs): median=728 [623, 759]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 623.0 | 727.5 | 759.0 | 0.0 | 727.5 | [0, 0] |
| dispatch | 3693.0 | 3724.5 | 3757.0 | 727.5 | 3724.5 | [728, 728] |
| swiglu | 3850.0 | 3923.0 | 4202.0 | 6595.5 | 3923.0 | [6422, 6808] |
| swiglu_w1 | 1299.0 | 1307.5 | 1315.0 | 6712.5 | 1307.5 | [6658, 6776] |
| swiglu_w2 | 778.0 | 795.5 | 804.0 | 9833.5 | 795.5 | [9776, 9938] |
| combine | 2591.0 | 5394.0 | 5476.0 | 10640.0 | 5394.0 | [10588, 10732] |
| unpermute | 582.0 | 586.5 | 593.0 | 16705.5 | 586.5 | [16704, 16706] |
| gmm1 | 7446.0 | 7524.5 | 8638.0 | 1037.0 | 7524.5 | [1008, 1088] |
| gmm2 | 4253.0 | 4775.0 | 5833.0 | 8450.5 | 4775.0 | [7464, 9646] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
