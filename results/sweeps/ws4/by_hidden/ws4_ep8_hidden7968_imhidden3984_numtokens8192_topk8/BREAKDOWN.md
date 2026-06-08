# dispatch_ffn_combine BREAKDOWN

- valid ranks: 4 [0, 1, 2, 3]
- profile version: 10
- timeline 聚合: relative_median
- prep skew (µs): median=1063 [1011, 1205]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 1011.0 | 1063.0 | 1205.0 | 0.0 | 1063.0 | [0, 0] |
| dispatch | 7373.0 | 7467.5 | 7519.0 | 1063.0 | 7467.5 | [1063, 1063] |
| swiglu | 13358.0 | 13602.0 | 13618.0 | 24748.0 | 13602.0 | [24538, 24832] |
| swiglu_w1 | 1963.0 | 1971.5 | 1983.0 | 24748.0 | 1971.5 | [24538, 24832] |
| swiglu_w2 | 1136.0 | 1138.0 | 1155.0 | 37084.5 | 1138.0 | [37020, 37290] |
| combine | 6680.0 | 9752.5 | 13040.0 | 39445.0 | 9752.5 | [39307, 39600] |
| unpermute | 1038.0 | 1043.0 | 1065.0 | 58686.0 | 1043.0 | [58596, 58801] |
| gmm1 | 27710.0 | 27899.5 | 35391.0 | 1717.5 | 27899.5 | [1628, 1849] |
| gmm2 | 15465.0 | 15807.5 | 27931.0 | 29270.0 | 15807.5 | [29077, 29442] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
