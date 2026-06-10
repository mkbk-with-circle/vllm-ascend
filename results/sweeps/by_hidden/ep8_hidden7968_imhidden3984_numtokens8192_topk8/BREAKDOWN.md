# dispatch_ffn_combine BREAKDOWN

- valid ranks: 8 [0, 1, 2, 3, 4, 5, 6, 7]
- profile version: 7
- timeline 聚合: relative_median
- prep skew (µs): median=1176 [1066, 1253]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 1066.0 | 1176.5 | 1253.0 | 0.0 | 1176.5 | [0, 0] |
| dispatch | 4221.0 | 4270.5 | 4308.0 | 1176.5 | 4270.5 | [1176, 1176] |
| swiglu | 14641.0 | 15728.0 | 17321.0 | 17438.5 | 15728.0 | [16812, 18496] |
| swiglu_w1 | 1549.0 | 1564.0 | 1573.0 | 17438.5 | 1564.0 | [16812, 18496] |
| swiglu_w2 | 1340.0 | 1347.5 | 1367.0 | 31486.5 | 1347.5 | [31078, 34460] |
| combine | 5111.0 | 7132.0 | 7328.0 | 48792.5 | 7132.0 | [48310, 50758] |
| gmm1 | 28250.0 | 28567.5 | 31439.0 | 2893.5 | 28567.5 | [2776, 3016] |
| gmm2 | 14656.0 | 14784.0 | 15284.0 | 32845.5 | 14784.0 | [32422, 35816] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
