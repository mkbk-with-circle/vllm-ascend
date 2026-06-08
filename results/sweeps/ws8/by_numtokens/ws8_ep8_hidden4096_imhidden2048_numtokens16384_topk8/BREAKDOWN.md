# dispatch_ffn_combine BREAKDOWN

- valid ranks: 8 [0, 1, 2, 3, 4, 5, 6, 7]
- profile version: 10
- timeline 聚合: relative_median
- prep skew (µs): median=1436 [1234, 1509]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 1234.0 | 1435.5 | 1509.0 | 0.0 | 1435.5 | [0, 0] |
| dispatch | 7267.0 | 7301.0 | 7367.0 | 1435.5 | 7301.0 | [1436, 1436] |
| swiglu | 7445.0 | 7602.0 | 8102.0 | 12522.0 | 7602.0 | [12332, 13008] |
| swiglu_w1 | 2633.0 | 2649.0 | 2656.0 | 12885.0 | 2649.0 | [12770, 12984] |
| swiglu_w2 | 1596.0 | 1610.0 | 1620.0 | 18926.5 | 1610.0 | [18720, 19084] |
| combine | 5728.0 | 10836.5 | 10964.0 | 20542.0 | 10836.5 | [20326, 20706] |
| unpermute | 1092.0 | 1105.0 | 1124.0 | 32319.5 | 1105.0 | [32316, 32320] |
| gmm1 | 14337.0 | 14430.5 | 16713.0 | 1977.0 | 14430.5 | [1930, 2322] |
| gmm2 | 8200.0 | 9017.0 | 12917.0 | 16269.5 | 9017.0 | [16190, 16490] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
