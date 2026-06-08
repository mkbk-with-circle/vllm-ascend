# dispatch_ffn_combine BREAKDOWN

- valid ranks: 4 [0, 1, 2, 3]
- profile version: 10
- timeline 聚合: relative_median
- prep skew (µs): median=1253 [1135, 1401]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 1135.0 | 1253.0 | 1401.0 | 0.0 | 1253.0 | [0, 0] |
| dispatch | 13453.0 | 13471.5 | 13481.0 | 1253.0 | 13471.5 | [1253, 1253] |
| swiglu | 8305.0 | 8381.0 | 8492.0 | 15973.5 | 8381.0 | [15744, 16118] |
| swiglu_w1 | 2611.0 | 2627.0 | 2630.0 | 15973.5 | 2627.0 | [15744, 16118] |
| swiglu_w2 | 1526.0 | 1535.0 | 1542.0 | 22819.5 | 1535.0 | [22523, 23068] |
| combine | 10170.0 | 14795.0 | 19491.0 | 24432.0 | 14795.0 | [24343, 24560] |
| unpermute | 1085.0 | 1094.5 | 1101.0 | 44330.0 | 1094.5 | [44194, 44449] |
| gmm1 | 13537.0 | 13706.5 | 14964.0 | 2671.5 | 13706.5 | [2480, 2779] |
| gmm2 | 9586.0 | 9604.5 | 9750.0 | 18602.5 | 9604.5 | [18373, 18730] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
