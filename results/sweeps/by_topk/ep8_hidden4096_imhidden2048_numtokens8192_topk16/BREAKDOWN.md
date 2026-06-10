# dispatch_ffn_combine BREAKDOWN

- valid ranks: 8 [0, 1, 2, 3, 4, 5, 6, 7]
- profile version: 7
- timeline 聚合: relative_median
- prep skew (µs): median=1261 [1093, 1339]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 1093.0 | 1261.0 | 1339.0 | 0.0 | 1261.0 | [0, 0] |
| dispatch | 7021.0 | 7053.0 | 7101.0 | 1261.0 | 7053.0 | [1261, 1261] |
| swiglu | 9201.0 | 9326.0 | 9503.0 | 12132.0 | 9326.0 | [11985, 12294] |
| swiglu_w1 | 2061.0 | 2082.5 | 2101.0 | 12132.0 | 2082.5 | [11985, 12294] |
| swiglu_w2 | 1801.0 | 1826.5 | 1841.0 | 19635.5 | 1826.5 | [19382, 19921] |
| combine | 8198.0 | 10889.5 | 10950.0 | 31211.5 | 10889.5 | [31090, 31566] |
| gmm1 | 15002.0 | 15207.5 | 15583.0 | 4389.5 | 15207.5 | [4286, 4505] |
| gmm2 | 9244.0 | 9280.5 | 9360.0 | 21463.5 | 9280.5 | [21186, 21760] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
