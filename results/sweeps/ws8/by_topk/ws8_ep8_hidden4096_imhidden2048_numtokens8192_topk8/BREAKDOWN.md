# dispatch_ffn_combine BREAKDOWN

- valid ranks: 8 [0, 1, 2, 3, 4, 5, 6, 7]
- profile version: 10
- timeline 聚合: relative_median
- prep skew (µs): median=662 [617, 677]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 617.0 | 662.5 | 677.0 | 0.0 | 662.5 | [0, 0] |
| dispatch | 3688.0 | 3724.5 | 3765.0 | 662.5 | 3724.5 | [662, 662] |
| swiglu | 3893.0 | 3933.0 | 3982.0 | 6681.0 | 3933.0 | [6598, 6720] |
| swiglu_w1 | 1302.0 | 1308.0 | 1313.0 | 6681.0 | 1308.0 | [6598, 6720] |
| swiglu_w2 | 777.0 | 794.0 | 800.0 | 9826.0 | 794.0 | [9690, 9902] |
| combine | 2570.0 | 5392.5 | 5463.0 | 10628.5 | 5392.5 | [10502, 10710] |
| unpermute | 580.0 | 586.5 | 593.0 | 16700.5 | 586.5 | [16698, 16702] |
| gmm1 | 7455.0 | 7605.5 | 9214.0 | 1003.0 | 7605.5 | [962, 1060] |
| gmm2 | 4224.0 | 5220.0 | 7121.0 | 8467.5 | 5220.0 | [7402, 8520] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
