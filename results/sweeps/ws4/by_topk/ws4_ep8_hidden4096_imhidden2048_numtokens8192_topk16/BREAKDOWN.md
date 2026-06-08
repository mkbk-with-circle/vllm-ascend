# dispatch_ffn_combine BREAKDOWN

- valid ranks: 4 [0, 1, 2, 3]
- profile version: 10
- timeline 聚合: relative_median
- prep skew (µs): median=1216 [944, 1327]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 944.0 | 1215.5 | 1327.0 | 0.0 | 1215.5 | [0, 0] |
| dispatch | 13409.0 | 13497.5 | 13552.0 | 1215.5 | 13497.5 | [1216, 1216] |
| swiglu | 8312.0 | 8423.0 | 8473.0 | 15914.5 | 8423.0 | [15678, 16106] |
| swiglu_w1 | 2608.0 | 2619.0 | 2624.0 | 15914.5 | 2619.0 | [15678, 16106] |
| swiglu_w2 | 1521.0 | 1549.5 | 1575.0 | 22767.5 | 1549.5 | [22504, 23010] |
| combine | 10187.0 | 14801.5 | 19409.0 | 24353.5 | 14801.5 | [24144, 24510] |
| unpermute | 1008.0 | 1017.5 | 1042.0 | 44365.5 | 1017.5 | [44242, 44486] |
| gmm1 | 13596.0 | 13672.0 | 13755.0 | 2565.5 | 13672.0 | [2486, 2720] |
| gmm2 | 9547.0 | 9699.0 | 9727.0 | 18538.0 | 9699.0 | [18288, 18724] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
