# dispatch_ffn_combine BREAKDOWN

- valid ranks: 8 [0, 1, 2, 3, 4, 5, 6, 7]
- profile version: 7
- timeline 聚合: relative_median
- prep skew (µs): median=840 [684, 922]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 684.0 | 840.0 | 922.0 | 0.0 | 840.0 | [0, 0] |
| dispatch | 3506.0 | 3532.0 | 3546.0 | 840.0 | 3532.0 | [840, 840] |
| swiglu | 4341.0 | 4357.0 | 5057.0 | 6916.5 | 4357.0 | [6153, 7088] |
| swiglu_w1 | 989.0 | 1002.5 | 1035.0 | 6916.5 | 1002.5 | [6153, 7088] |
| swiglu_w2 | 894.0 | 902.0 | 919.0 | 10366.5 | 902.0 | [9682, 11239] |
| combine | 3838.0 | 5456.5 | 5510.0 | 15770.5 | 5456.5 | [15288, 16663] |
| gmm1 | 7190.0 | 7231.0 | 8167.0 | 3119.0 | 7231.0 | [2393, 3312] |
| gmm2 | 4445.0 | 4493.0 | 4527.0 | 11267.5 | 4493.0 | [10602, 12145] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
