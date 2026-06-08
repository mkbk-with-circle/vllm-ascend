# dispatch_ffn_combine BREAKDOWN

- valid ranks: 16 [0, 10, 11, 12, 13, 14, 15, 1, 2, 3, 4, 5, 6, 7, 8, 9]
- profile version: 10
- timeline 聚合: relative_median
- prep skew (µs): median=1124 [837, 1193]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 837.0 | 1124.5 | 1193.0 | 0.0 | 1124.5 | [0, 0] |
| dispatch | 2263.0 | 2288.0 | 2323.0 | 1124.5 | 2288.0 | [1124, 1124] |
| swiglu | 3422.0 | 3456.0 | 3490.0 | 6642.5 | 3456.0 | [5542, 6882] |
| swiglu_w1 | 1252.0 | 1261.0 | 1273.0 | 6073.5 | 1261.0 | [6022, 6128] |
| swiglu_w2 | 758.0 | 763.0 | 771.0 | 8770.0 | 763.0 | [8722, 8806] |
| combine | 1393.0 | 3618.0 | 3713.0 | 9540.0 | 3618.0 | [9492, 9582] |
| unpermute | 631.0 | 635.5 | 640.0 | 13940.5 | 635.5 | [13940, 13942] |
| gmm1 | 7285.0 | 7336.0 | 7403.0 | 1962.5 | 7336.0 | [882, 2172] |
| gmm2 | 4537.0 | 5693.0 | 5795.0 | 8240.5 | 5693.0 | [8096, 9568] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
