# dispatch_ffn_combine BREAKDOWN

- valid ranks: 8 [0, 1, 2, 3, 4, 5, 6, 7]
- profile version: 7
- timeline 聚合: relative_median
- prep skew (µs): median=5346 [5100, 5418]
- timeline repaired: ['combine']

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 5100.0 | 5345.5 | 5418.0 | 0.0 | 5345.5 | [0, 0] |
| dispatch | 31252.0 | 31460.0 | 31590.0 | 5345.5 | 31460.0 | [5346, 5346] |
| swiglu | 77445.0 | 77584.5 | 78124.0 | 94140.5 | 77584.5 | [92950, 95570] |
| swiglu_w1 | 10470.0 | 10497.0 | 10514.0 | 94140.5 | 10497.0 | [92950, 95570] |
| swiglu_w2 | 9042.0 | 9076.0 | 9106.0 | 163007.5 | 9076.0 | [161338, 164064] |
| combine | 36761.0 | 49882.5 | 50562.0 | 247714.5 | 49882.5 | [245480, 250588] |
| gmm1 | 140760.0 | 142137.5 | 143135.0 | 20822.5 | 142137.5 | [20396, 21040] |
| gmm2 | 74299.0 | 75626.5 | 77440.0 | 172088.0 | 75626.5 | [170396, 173148] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
