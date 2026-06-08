# dispatch_ffn_combine BREAKDOWN

- valid ranks: 8 [0, 1, 2, 3, 4, 5, 6, 7]
- profile version: 10
- timeline 聚合: relative_median
- prep skew (µs): median=1283 [948, 1351]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 948.0 | 1283.0 | 1351.0 | 0.0 | 1283.0 | [0, 0] |
| dispatch | 4279.0 | 4323.5 | 4373.0 | 1283.0 | 4323.5 | [1283, 1283] |
| swiglu | 10315.0 | 11093.0 | 11768.0 | 19502.5 | 11093.0 | [18520, 20283] |
| swiglu_w1 | 1783.0 | 1799.5 | 1830.0 | 19165.5 | 1799.5 | [18817, 19457] |
| swiglu_w2 | 1062.0 | 1076.5 | 1095.0 | 28842.5 | 1076.5 | [28239, 29272] |
| combine | 3231.0 | 6417.5 | 6538.0 | 30548.5 | 6417.5 | [29896, 30981] |
| unpermute | 951.0 | 960.5 | 977.0 | 44522.0 | 960.5 | [44521, 44523] |
| gmm1 | 24199.0 | 24773.5 | 27902.0 | 1820.0 | 24773.5 | [1227, 2221] |
| gmm2 | 11595.0 | 12206.0 | 17997.0 | 25663.5 | 12206.0 | [24982, 26651] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
