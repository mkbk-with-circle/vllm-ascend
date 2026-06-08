# dispatch_ffn_combine BREAKDOWN

- valid ranks: 4 [0, 1, 2, 3]
- profile version: 10
- timeline 聚合: relative_median
- prep skew (µs): median=1088 [790, 1189]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 790.0 | 1088.5 | 1189.0 | 0.0 | 1088.5 | [0, 0] |
| dispatch | 7480.0 | 7521.5 | 7536.0 | 1088.5 | 7521.5 | [1088, 1088] |
| swiglu | 14325.0 | 14404.5 | 14536.0 | 26358.5 | 14404.5 | [26048, 26978] |
| swiglu_w1 | 1912.0 | 1926.5 | 1929.0 | 26358.5 | 1926.5 | [26048, 26978] |
| swiglu_w2 | 1089.0 | 1093.5 | 1112.0 | 39669.5 | 1093.5 | [39284, 40402] |
| combine | 6528.0 | 9405.0 | 12446.0 | 41904.0 | 9405.0 | [41508, 42078] |
| unpermute | 1018.0 | 1037.0 | 1074.0 | 61278.0 | 1037.0 | [61224, 61478] |
| gmm1 | 30323.0 | 30385.0 | 31629.0 | 1941.0 | 30385.0 | [1920, 2134] |
| gmm2 | 14954.0 | 15264.5 | 15824.0 | 32379.0 | 15264.5 | [32262, 32534] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
