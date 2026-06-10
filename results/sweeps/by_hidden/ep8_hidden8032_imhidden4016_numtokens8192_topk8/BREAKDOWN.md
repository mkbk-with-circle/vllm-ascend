# dispatch_ffn_combine BREAKDOWN

- valid ranks: 8 [0, 1, 2, 3, 4, 5, 6, 7]
- profile version: 7
- timeline 聚合: relative_median
- prep skew (µs): median=1150 [1117, 1304]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 1117.0 | 1150.0 | 1304.0 | 0.0 | 1150.0 | [0, 0] |
| dispatch | 4267.0 | 4282.0 | 4327.0 | 1150.0 | 4282.0 | [1150, 1150] |
| swiglu | 15390.0 | 15738.0 | 15965.0 | 17170.0 | 15738.0 | [16968, 17607] |
| swiglu_w1 | 1540.0 | 1555.0 | 1577.0 | 17170.0 | 1555.0 | [16968, 17607] |
| swiglu_w2 | 1348.0 | 1357.0 | 1366.0 | 31501.0 | 1357.0 | [31310, 32207] |
| combine | 5236.0 | 7295.5 | 7403.0 | 48909.0 | 7295.5 | [48481, 49097] |
| gmm1 | 28407.0 | 28658.5 | 29349.0 | 2874.0 | 28658.5 | [2787, 2920] |
| gmm2 | 14663.0 | 14885.0 | 14987.0 | 32857.0 | 14885.0 | [32664, 33572] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
