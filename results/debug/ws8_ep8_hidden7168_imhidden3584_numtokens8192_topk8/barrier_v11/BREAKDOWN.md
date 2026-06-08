# dispatch_ffn_combine BREAKDOWN

- valid ranks: 8 [0, 1, 2, 3, 4, 5, 6, 7]
- profile version: 11
- timeline 聚合: relative_median
- prep skew (µs): median=1062 [966, 1195]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 966.0 | 1062.5 | 1195.0 | 0.0 | 1062.5 | [0, 0] |
| dispatch | 4291.0 | 4323.5 | 4380.0 | 1062.5 | 4323.5 | [1062, 1062] |
| swiglu | 10447.0 | 10721.5 | 10994.0 | 18986.0 | 10721.5 | [18578, 19322] |
| swiglu_w1 | 1779.0 | 1800.0 | 1834.0 | 18986.0 | 1800.0 | [18578, 19322] |
| swiglu_w2 | 1059.0 | 1075.5 | 1095.0 | 28609.5 | 1075.5 | [27966, 29102] |
| combine | 3232.0 | 6334.5 | 6503.0 | 30313.0 | 6334.5 | [29618, 30822] |
| unpermute | 948.0 | 962.0 | 981.0 | 44056.0 | 962.0 | [44054, 44058] |
| gmm1 | 24000.0 | 24883.5 | 25458.0 | 1573.5 | 24883.5 | [1304, 1774] |
| gmm2 | 11556.0 | 12069.5 | 12171.0 | 26019.0 | 12069.5 | [25334, 26474] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
