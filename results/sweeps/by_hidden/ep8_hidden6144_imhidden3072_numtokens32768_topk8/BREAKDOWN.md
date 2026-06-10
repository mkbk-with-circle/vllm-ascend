# dispatch_ffn_combine BREAKDOWN

- valid ranks: 8 [0, 1, 2, 3, 4, 5, 6, 7]
- profile version: 7
- timeline 聚合: relative_median
- prep skew (µs): median=3350 [2831, 3442]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 2831.0 | 3350.5 | 3442.0 | 0.0 | 3350.5 | [0, 0] |
| dispatch | 15627.0 | 15725.5 | 15939.0 | 3350.5 | 15725.5 | [3350, 3350] |
| swiglu | 37002.0 | 37257.0 | 37513.0 | 45734.5 | 37257.0 | [45006, 46972] |
| swiglu_w1 | 5078.0 | 5103.5 | 5136.0 | 45734.5 | 5103.5 | [45006, 46972] |
| swiglu_w2 | 4501.0 | 4542.0 | 4556.0 | 78445.0 | 4542.0 | [77664, 79786] |
| combine | 18490.0 | 25016.5 | 25346.0 | 123247.5 | 25016.5 | [122880, 123552] |
| gmm1 | 67211.0 | 67783.0 | 69228.0 | 10612.0 | 67783.0 | [10450, 10798] |
| gmm2 | 36850.0 | 37862.5 | 38718.0 | 82973.5 | 37862.5 | [82212, 84330] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
