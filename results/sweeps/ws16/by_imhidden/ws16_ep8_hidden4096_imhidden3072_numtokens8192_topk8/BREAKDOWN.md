# dispatch_ffn_combine BREAKDOWN

- valid ranks: 16 [0, 10, 11, 12, 13, 14, 15, 1, 2, 3, 4, 5, 6, 7, 8, 9]
- profile version: 10
- timeline 聚合: relative_median
- prep skew (µs): median=876 [753, 966]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 753.0 | 876.0 | 966.0 | 0.0 | 876.0 | [0, 0] |
| dispatch | 2254.0 | 2288.5 | 2309.0 | 876.0 | 2288.5 | [876, 876] |
| swiglu | 4972.0 | 5014.5 | 5074.0 | 7716.0 | 5014.5 | [7581, 7845] |
| swiglu_w1 | 1569.0 | 1583.5 | 1593.0 | 7954.5 | 1583.5 | [7883, 8054] |
| swiglu_w2 | 943.0 | 952.5 | 965.0 | 12026.5 | 952.5 | [11933, 12101] |
| combine | 1309.0 | 3591.5 | 3714.0 | 12990.0 | 3591.5 | [12893, 13074] |
| unpermute | 639.0 | 644.0 | 649.0 | 18487.0 | 644.0 | [18485, 18488] |
| gmm1 | 10748.0 | 10857.5 | 10934.0 | 946.0 | 10857.5 | [836, 1166] |
| gmm2 | 5825.0 | 5877.0 | 6255.0 | 11722.5 | 5877.0 | [11654, 11994] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
