# dispatch_ffn_combine BREAKDOWN

- valid ranks: 4 [0, 1, 2, 3]
- profile version: 10
- timeline 聚合: relative_median
- prep skew (µs): median=161 [130, 170]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 130.0 | 161.0 | 170.0 | 0.0 | 161.0 | [0, 0] |
| dispatch | 770.0 | 778.0 | 792.0 | 161.0 | 778.0 | [161, 161] |
| swiglu | 243.0 | 244.5 | 250.0 | 967.5 | 244.5 | [932, 978] |
| swiglu_w1 | 151.0 | 152.5 | 153.0 | 967.5 | 152.5 | [932, 978] |
| swiglu_w2 | 89.0 | 91.0 | 96.0 | 1121.0 | 91.0 | [1086, 1132] |
| combine | 526.0 | 873.0 | 1203.0 | 1193.5 | 873.0 | [1186, 1212] |
| unpermute | 51.0 | 51.5 | 55.0 | 2506.0 | 51.5 | [2479, 2508] |
| gmm1 | 754.0 | 767.0 | 782.0 | 275.5 | 767.0 | [251, 282] |
| gmm2 | 349.0 | 351.0 | 353.0 | 1117.0 | 351.0 | [1084, 1129] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
