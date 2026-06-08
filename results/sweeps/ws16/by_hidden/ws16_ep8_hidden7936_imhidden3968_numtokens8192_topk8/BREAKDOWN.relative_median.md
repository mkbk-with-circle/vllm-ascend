# dispatch_ffn_combine BREAKDOWN

- valid ranks: 16 [0, 10, 11, 12, 13, 14, 15, 1, 2, 3, 4, 5, 6, 7, 8, 9]
- profile version: 10
- timeline 聚合: relative_median
- prep skew (µs): median=1591 [1164, 1659]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 1164.0 | 1591.0 | 1659.0 | 0.0 | 1591.0 | [0, 0] |
| dispatch | 3811.0 | 3823.0 | 3840.0 | 1591.0 | 3823.0 | [1591, 1591] |
| swiglu | 12158.0 | 12260.0 | 14915.0 | 20079.0 | 12260.0 | [19781, 22408] |
| swiglu_w1 | 1906.0 | 1916.0 | 1938.0 | 20661.0 | 1916.0 | [20496, 20900] |
| swiglu_w2 | 1079.0 | 1092.0 | 1105.0 | 31874.5 | 1092.0 | [31656, 32285] |
| combine | 2150.0 | 6591.5 | 6758.0 | 33690.0 | 6591.5 | [33423, 34175] |
| unpermute | 1064.0 | 1072.5 | 1083.0 | 51018.5 | 1072.5 | [51017, 51020] |
| gmm1 | 29507.0 | 29702.5 | 34612.0 | 1494.5 | 29702.5 | [1306, 1897] |
| gmm2 | 14292.0 | 14547.0 | 23268.0 | 31177.5 | 14547.0 | [30926, 31504] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
