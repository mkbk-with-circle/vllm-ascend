# dispatch_ffn_combine BREAKDOWN

- valid ranks: 4 [0, 1, 2, 3]
- profile version: 10
- timeline 聚合: relative_median
- prep skew (µs): median=624 [591, 655]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 591.0 | 623.5 | 655.0 | 0.0 | 623.5 | [0, 0] |
| dispatch | 6809.0 | 6818.0 | 6881.0 | 623.5 | 6818.0 | [624, 624] |
| swiglu | 4269.0 | 4321.5 | 4375.0 | 8243.0 | 4321.5 | [8180, 8466] |
| swiglu_w1 | 1273.0 | 1280.5 | 1287.0 | 8243.0 | 1280.5 | [8180, 8466] |
| swiglu_w2 | 752.0 | 760.5 | 765.0 | 11802.5 | 760.5 | [11696, 12080] |
| combine | 4813.0 | 7265.5 | 9759.0 | 12560.0 | 7265.5 | [12468, 12642] |
| unpermute | 580.0 | 592.0 | 594.0 | 22778.5 | 592.0 | [22740, 22840] |
| gmm1 | 7130.0 | 7199.5 | 7453.0 | 1329.5 | 7199.5 | [1312, 1422] |
| gmm2 | 5045.0 | 5260.5 | 5370.0 | 9395.0 | 5260.5 | [9292, 9560] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
