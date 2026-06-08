# dispatch_ffn_combine BREAKDOWN

- valid ranks: 4 [0, 1, 2, 3]
- profile version: 10
- timeline 聚合: relative_median
- prep skew (µs): median=699 [685, 767]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 685.0 | 699.0 | 767.0 | 0.0 | 699.0 | [0, 0] |
| dispatch | 6792.0 | 6819.5 | 6882.0 | 699.0 | 6819.5 | [699, 699] |
| swiglu | 4272.0 | 4330.5 | 4380.0 | 8257.0 | 4330.5 | [8119, 8439] |
| swiglu_w1 | 1274.0 | 1279.5 | 1290.0 | 8257.0 | 1279.5 | [8119, 8439] |
| swiglu_w2 | 749.0 | 756.5 | 764.0 | 11831.0 | 756.5 | [11642, 12055] |
| combine | 4811.0 | 7270.5 | 9746.0 | 12670.5 | 7270.5 | [12550, 12729] |
| unpermute | 584.0 | 585.0 | 599.0 | 22702.0 | 585.0 | [22662, 22710] |
| gmm1 | 7329.0 | 7386.5 | 10718.0 | 1328.5 | 7386.5 | [1267, 1343] |
| gmm2 | 5137.0 | 5233.5 | 8320.0 | 9327.5 | 5233.5 | [9200, 9411] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
