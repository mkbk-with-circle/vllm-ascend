# dispatch_ffn_combine BREAKDOWN

- valid ranks: 8 [0, 1, 2, 3, 4, 5, 6, 7]
- profile version: 7
- timeline 聚合: relative_median
- prep skew (µs): median=900 [781, 966]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 781.0 | 900.5 | 966.0 | 0.0 | 900.5 | [0, 0] |
| dispatch | 3515.0 | 3546.0 | 3597.0 | 900.5 | 3546.0 | [900, 900] |
| swiglu | 6399.0 | 6441.0 | 6483.0 | 7805.0 | 6441.0 | [7756, 8022] |
| swiglu_w1 | 1239.0 | 1246.0 | 1250.0 | 7805.0 | 1246.0 | [7756, 8022] |
| swiglu_w2 | 1113.0 | 1125.0 | 1133.0 | 13121.5 | 1125.0 | [13046, 13308] |
| combine | 3849.0 | 5450.0 | 5550.0 | 20407.0 | 5450.0 | [20294, 20464] |
| gmm1 | 10758.0 | 10808.0 | 10850.0 | 2304.5 | 10808.0 | [2270, 2494] |
| gmm2 | 5800.0 | 5818.0 | 5882.0 | 14246.0 | 5818.0 | [14166, 14420] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
