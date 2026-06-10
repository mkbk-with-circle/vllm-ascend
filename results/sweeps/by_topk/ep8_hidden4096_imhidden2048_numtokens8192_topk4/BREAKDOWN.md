# dispatch_ffn_combine BREAKDOWN

- valid ranks: 8 [0, 1, 2, 3, 4, 5, 6, 7]
- profile version: 7
- timeline 聚合: relative_median
- prep skew (µs): median=516 [435, 572]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 435.0 | 515.5 | 572.0 | 0.0 | 515.5 | [0, 0] |
| dispatch | 1748.0 | 1762.0 | 1791.0 | 515.5 | 1762.0 | [516, 516] |
| swiglu | 2078.0 | 2101.0 | 2124.0 | 3131.0 | 2101.0 | [3068, 3216] |
| swiglu_w1 | 501.0 | 511.5 | 513.0 | 3131.0 | 511.5 | [3068, 3216] |
| swiglu_w2 | 439.0 | 439.5 | 448.0 | 4782.0 | 439.5 | [4728, 4894] |
| combine | 1978.0 | 2742.5 | 2797.0 | 7578.5 | 2742.5 | [7540, 7704] |
| gmm1 | 3433.0 | 3479.0 | 3493.0 | 1308.5 | 3479.0 | [1254, 1400] |
| gmm2 | 2277.0 | 2309.0 | 2355.0 | 5221.5 | 2309.0 | [5168, 5340] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
