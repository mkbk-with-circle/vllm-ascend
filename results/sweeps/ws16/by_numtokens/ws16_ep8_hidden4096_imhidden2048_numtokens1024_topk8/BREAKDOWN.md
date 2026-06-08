# dispatch_ffn_combine BREAKDOWN

- valid ranks: 16 [0, 10, 11, 12, 13, 14, 15, 1, 2, 3, 4, 5, 6, 7, 8, 9]
- profile version: 10
- timeline 聚合: relative_median
- prep skew (µs): median=300 [255, 342]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 255.0 | 300.0 | 342.0 | 0.0 | 300.0 | [0, 0] |
| dispatch | 319.0 | 325.0 | 333.0 | 300.0 | 325.0 | [300, 300] |
| swiglu | 309.0 | 326.0 | 341.0 | 687.0 | 326.0 | [611, 786] |
| swiglu_w1 | 149.0 | 154.0 | 164.0 | 760.5 | 154.0 | [749, 768] |
| swiglu_w2 | 83.0 | 88.0 | 91.0 | 1002.5 | 88.0 | [984, 1019] |
| combine | 170.0 | 430.0 | 452.0 | 1098.0 | 430.0 | [1079, 1118] |
| unpermute | 53.0 | 58.5 | 65.0 | 1696.5 | 58.5 | [1695, 1698] |
| gmm1 | 627.0 | 655.0 | 665.0 | 297.5 | 655.0 | [196, 363] |
| gmm2 | 338.0 | 347.5 | 359.0 | 919.0 | 347.5 | [831, 1009] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
