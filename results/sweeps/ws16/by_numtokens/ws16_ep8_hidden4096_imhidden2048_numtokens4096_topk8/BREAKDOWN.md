# dispatch_ffn_combine BREAKDOWN

- valid ranks: 16 [0, 10, 11, 12, 13, 14, 15, 1, 2, 3, 4, 5, 6, 7, 8, 9]
- profile version: 10
- timeline 聚合: relative_median
- prep skew (µs): median=566 [488, 658]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 488.0 | 566.5 | 658.0 | 0.0 | 566.5 | [0, 0] |
| dispatch | 1166.0 | 1187.0 | 1201.0 | 566.5 | 1187.0 | [566, 566] |
| swiglu | 1716.0 | 1738.5 | 1766.0 | 2714.5 | 1738.5 | [2654, 2820] |
| swiglu_w1 | 624.0 | 641.0 | 645.0 | 2946.0 | 641.0 | [2892, 2968] |
| swiglu_w2 | 375.0 | 382.0 | 386.0 | 4299.5 | 382.0 | [4238, 4330] |
| combine | 700.0 | 1805.0 | 1876.0 | 4688.0 | 1805.0 | [4628, 4722] |
| unpermute | 364.0 | 368.5 | 373.0 | 6928.5 | 368.5 | [6928, 6930] |
| gmm1 | 3519.0 | 3571.5 | 3611.0 | 497.0 | 3571.5 | [436, 722] |
| gmm2 | 2055.0 | 2327.5 | 2484.0 | 4004.0 | 2327.5 | [3718, 4216] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
