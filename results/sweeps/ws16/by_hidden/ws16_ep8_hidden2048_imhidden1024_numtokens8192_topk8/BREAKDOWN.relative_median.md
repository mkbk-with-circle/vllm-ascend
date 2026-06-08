# dispatch_ffn_combine BREAKDOWN

- valid ranks: 16 [0, 10, 11, 12, 13, 14, 15, 1, 2, 3, 4, 5, 6, 7, 8, 9]
- profile version: 10
- timeline 聚合: relative_median
- prep skew (µs): median=927 [754, 1021]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 754.0 | 927.0 | 1021.0 | 0.0 | 927.0 | [0, 0] |
| dispatch | 1822.0 | 1849.5 | 1871.0 | 927.0 | 1849.5 | [927, 927] |
| swiglu | 1513.0 | 1527.0 | 1541.0 | 2709.0 | 1527.0 | [2266, 2830] |
| swiglu_w1 | 922.0 | 927.0 | 937.0 | 2778.5 | 927.0 | [2751, 2800] |
| swiglu_w2 | 587.0 | 596.5 | 605.0 | 3707.0 | 596.5 | [3675, 3738] |
| combine | 1153.0 | 2582.0 | 2640.0 | 4313.5 | 2582.0 | [4277, 4343] |
| unpermute | 339.0 | 345.0 | 350.0 | 7171.5 | 345.0 | [7170, 7173] |
| gmm1 | 2115.0 | 2153.0 | 2172.0 | 1122.5 | 2153.0 | [910, 1225] |
| gmm2 | 1476.0 | 1524.5 | 1560.0 | 3644.5 | 1524.5 | [3189, 3763] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
