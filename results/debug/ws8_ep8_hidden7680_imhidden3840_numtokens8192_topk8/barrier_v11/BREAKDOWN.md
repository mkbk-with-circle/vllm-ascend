# dispatch_ffn_combine BREAKDOWN

- valid ranks: 8 [0, 1, 2, 3, 4, 5, 6, 7]
- profile version: 11
- timeline 聚合: relative_median
- prep skew (µs): median=1228 [990, 1300]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 990.0 | 1228.0 | 1300.0 | 0.0 | 1228.0 | [0, 0] |
| dispatch | 4406.0 | 4447.5 | 4505.0 | 1228.0 | 4447.5 | [1228, 1228] |
| swiglu | 11972.0 | 12149.5 | 12329.0 | 21868.0 | 12149.5 | [21527, 22075] |
| swiglu_w1 | 1846.0 | 1859.0 | 1902.0 | 21868.0 | 1859.0 | [21527, 22075] |
| swiglu_w2 | 1106.0 | 1117.0 | 1131.0 | 32893.5 | 1117.0 | [32435, 33290] |
| combine | 3384.0 | 6524.0 | 6651.0 | 34886.5 | 6524.0 | [34392, 35263] |
| unpermute | 1012.0 | 1019.5 | 1037.0 | 50089.5 | 1019.5 | [50088, 50091] |
| gmm1 | 28180.0 | 28943.0 | 29371.0 | 1441.0 | 28943.0 | [1215, 1674] |
| gmm2 | 13493.0 | 13620.5 | 13759.0 | 30241.5 | 13620.5 | [29430, 30860] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
