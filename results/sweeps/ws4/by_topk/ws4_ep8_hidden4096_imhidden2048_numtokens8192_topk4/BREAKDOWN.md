# dispatch_ffn_combine BREAKDOWN

- valid ranks: 4 [0, 1, 2, 3]
- profile version: 10
- timeline 聚合: relative_median
- prep skew (µs): median=442 [392, 487]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 392.0 | 442.5 | 487.0 | 0.0 | 442.5 | [0, 0] |
| dispatch | 3366.0 | 3381.5 | 3451.0 | 442.5 | 3381.5 | [442, 442] |
| swiglu | 2018.0 | 2109.5 | 2149.0 | 3843.0 | 2109.5 | [3776, 3926] |
| swiglu_w1 | 672.0 | 679.5 | 681.0 | 3843.0 | 679.5 | [3776, 3926] |
| swiglu_w2 | 383.0 | 390.0 | 393.0 | 5529.5 | 390.0 | [5478, 5682] |
| combine | 2512.0 | 3680.0 | 4861.0 | 5920.0 | 3680.0 | [5866, 5988] |
| unpermute | 327.0 | 336.5 | 339.0 | 11142.5 | 336.5 | [11102, 11164] |
| gmm1 | 3586.0 | 3653.0 | 3707.0 | 831.5 | 3653.0 | [824, 870] |
| gmm2 | 2386.0 | 2452.5 | 2510.0 | 4461.0 | 2452.5 | [4450, 4562] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
