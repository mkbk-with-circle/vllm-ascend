# dispatch_ffn_combine BREAKDOWN

- valid ranks: 4 [0, 1, 2, 3]
- profile version: 10
- timeline 聚合: relative_median
- prep skew (µs): median=466 [450, 517]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 450.0 | 466.0 | 517.0 | 0.0 | 466.0 | [0, 0] |
| dispatch | 5973.0 | 6070.5 | 6084.0 | 466.0 | 6070.5 | [466, 466] |
| swiglu | 1493.0 | 1500.5 | 1511.0 | 6541.0 | 1500.5 | [6454, 6569] |
| swiglu_w1 | 901.0 | 903.5 | 906.0 | 6541.0 | 903.5 | [6454, 6569] |
| swiglu_w2 | 589.0 | 596.0 | 603.0 | 7445.5 | 596.0 | [7358, 7477] |
| combine | 3961.0 | 6244.5 | 8631.0 | 8049.5 | 6244.5 | [7939, 8070] |
| unpermute | 347.0 | 349.5 | 352.0 | 16828.0 | 349.5 | [16810, 16841] |
| gmm1 | 5541.0 | 5605.5 | 5640.0 | 1188.5 | 5605.5 | [1172, 1201] |
| gmm2 | 1449.0 | 1466.5 | 1484.0 | 7441.5 | 1466.5 | [7358, 7475] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
