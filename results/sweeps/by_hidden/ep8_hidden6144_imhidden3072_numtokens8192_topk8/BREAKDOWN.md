# dispatch_ffn_combine BREAKDOWN

- valid ranks: 8 [0, 1, 2, 3, 4, 5, 6, 7]
- profile version: 7
- timeline 聚合: relative_median
- prep skew (µs): median=1002 [879, 1168]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 879.0 | 1002.0 | 1168.0 | 0.0 | 1002.0 | [0, 0] |
| dispatch | 3958.0 | 3965.5 | 3983.0 | 1002.0 | 3965.5 | [1002, 1002] |
| swiglu | 9781.0 | 10579.5 | 10990.0 | 12732.5 | 10579.5 | [10988, 13336] |
| swiglu_w1 | 1295.0 | 1303.0 | 1318.0 | 12732.5 | 1303.0 | [10988, 13336] |
| swiglu_w2 | 1112.0 | 1117.5 | 1131.0 | 22267.5 | 1117.5 | [19830, 22727] |
| combine | 4254.0 | 5904.0 | 6008.0 | 32569.0 | 5904.0 | [32306, 32937] |
| gmm1 | 17325.0 | 19227.5 | 19603.0 | 3063.0 | 19227.5 | [2395, 3138] |
| gmm2 | 8973.0 | 9107.5 | 9217.0 | 23390.0 | 9107.5 | [20951, 23845] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
