# dispatch_ffn_combine BREAKDOWN

- valid ranks: 8 [0, 1, 2, 3, 4, 5, 6, 7]
- profile version: 7
- timeline 聚合: relative_median
- prep skew (µs): median=824 [681, 945]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 681.0 | 824.0 | 945.0 | 0.0 | 824.0 | [0, 0] |
| dispatch | 3503.0 | 3531.5 | 3549.0 | 824.0 | 3531.5 | [824, 824] |
| swiglu | 4330.0 | 4356.5 | 4382.0 | 6063.5 | 4356.5 | [5932, 6277] |
| swiglu_w1 | 996.0 | 1003.0 | 1008.0 | 6063.5 | 1003.0 | [5932, 6277] |
| swiglu_w2 | 897.0 | 901.0 | 920.0 | 9497.0 | 901.0 | [9400, 9722] |
| combine | 3834.0 | 5452.0 | 5501.0 | 15152.5 | 5452.0 | [15089, 15250] |
| gmm1 | 7172.0 | 7216.5 | 7247.0 | 2279.5 | 7216.5 | [2166, 2501] |
| gmm2 | 4431.0 | 4466.5 | 4527.0 | 10394.5 | 4466.5 | [10307, 10631] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
