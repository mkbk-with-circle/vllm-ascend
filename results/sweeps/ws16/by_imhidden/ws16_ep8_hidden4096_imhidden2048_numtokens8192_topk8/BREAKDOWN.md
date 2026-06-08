# dispatch_ffn_combine BREAKDOWN

- valid ranks: 16 [0, 10, 11, 12, 13, 14, 15, 1, 2, 3, 4, 5, 6, 7, 8, 9]
- profile version: 10
- timeline 聚合: relative_median
- prep skew (µs): median=1146 [863, 1186]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 863.0 | 1146.0 | 1186.0 | 0.0 | 1146.0 | [0, 0] |
| dispatch | 2258.0 | 2286.5 | 2320.0 | 1146.0 | 2286.5 | [1146, 1146] |
| swiglu | 3427.0 | 3452.5 | 3485.0 | 5564.5 | 3452.5 | [5483, 5824] |
| swiglu_w1 | 1251.0 | 1260.0 | 1274.0 | 6089.0 | 1260.0 | [6050, 6155] |
| swiglu_w2 | 754.0 | 759.5 | 771.0 | 8777.0 | 759.5 | [8740, 8832] |
| combine | 1388.0 | 3613.0 | 3717.0 | 9551.5 | 3613.0 | [9505, 9609] |
| unpermute | 632.0 | 634.5 | 640.0 | 13959.0 | 634.5 | [13957, 13961] |
| gmm1 | 7281.0 | 7334.0 | 7386.0 | 889.0 | 7334.0 | [801, 1453] |
| gmm2 | 4209.0 | 4436.0 | 4700.0 | 8160.5 | 4436.0 | [7828, 8453] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
