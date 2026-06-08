# dispatch_ffn_combine BREAKDOWN

- valid ranks: 16 [0, 10, 11, 12, 13, 14, 15, 1, 2, 3, 4, 5, 6, 7, 8, 9]
- profile version: 10
- timeline 聚合: relative_median
- prep skew (µs): median=592 [374, 679]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 374.0 | 591.5 | 679.0 | 0.0 | 591.5 | [0, 0] |
| dispatch | 611.0 | 616.0 | 635.0 | 591.5 | 616.0 | [592, 592] |
| swiglu | 851.0 | 876.5 | 900.0 | 3911.0 | 876.5 | [1594, 4100] |
| swiglu_w1 | 311.0 | 317.0 | 322.0 | 1826.5 | 317.0 | [1804, 1854] |
| swiglu_w2 | 179.0 | 183.5 | 189.0 | 2512.0 | 183.5 | [2496, 2552] |
| combine | 321.0 | 886.0 | 908.0 | 2706.5 | 886.0 | [2684, 2748] |
| unpermute | 171.0 | 175.5 | 180.0 | 3875.5 | 175.5 | [3874, 3878] |
| gmm1 | 1808.0 | 1832.5 | 1863.0 | 2751.0 | 1832.5 | [436, 2958] |
| gmm2 | 1147.0 | 1166.5 | 1194.0 | 4580.5 | 1166.5 | [2246, 4788] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
