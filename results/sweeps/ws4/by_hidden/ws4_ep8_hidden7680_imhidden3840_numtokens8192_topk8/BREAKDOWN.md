# dispatch_ffn_combine BREAKDOWN

- valid ranks: 4 [0, 1, 2, 3]
- profile version: 10
- timeline 聚合: relative_median
- prep skew (µs): median=938 [854, 1019]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 854.0 | 938.0 | 1019.0 | 0.0 | 938.0 | [0, 0] |
| dispatch | 7583.0 | 7639.0 | 7658.0 | 938.0 | 7639.0 | [938, 938] |
| swiglu | 13972.0 | 14037.5 | 14127.0 | 25916.0 | 14037.5 | [25433, 26075] |
| swiglu_w1 | 1911.0 | 1918.5 | 1923.0 | 25916.0 | 1918.5 | [25433, 26075] |
| swiglu_w2 | 1073.0 | 1080.0 | 1088.0 | 38878.5 | 1080.0 | [38422, 39014] |
| combine | 6398.0 | 9310.0 | 12261.0 | 40881.0 | 9310.0 | [40839, 40931] |
| unpermute | 988.0 | 1009.5 | 1026.0 | 59456.5 | 1009.5 | [59425, 59565] |
| gmm1 | 29972.0 | 30004.5 | 37286.0 | 1558.0 | 30004.5 | [1524, 1670] |
| gmm2 | 14742.0 | 15286.0 | 26444.0 | 31119.5 | 15286.0 | [30929, 31486] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
