# dispatch_ffn_combine BREAKDOWN

- valid ranks: 8 [0, 1, 2, 3, 4, 5, 6, 7]
- profile version: 7
- timeline 聚合: relative_median
- prep skew (µs): median=196 [155, 237]
- timeline repaired: ['combine']

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 155.0 | 196.0 | 237.0 | 0.0 | 196.0 | [0, 0] |
| dispatch | 394.0 | 399.0 | 408.0 | 196.0 | 399.0 | [196, 196] |
| swiglu | 377.0 | 388.0 | 390.0 | 661.5 | 388.0 | [642, 677] |
| swiglu_w1 | 98.0 | 103.5 | 109.0 | 661.5 | 103.5 | [642, 677] |
| swiglu_w2 | 90.0 | 93.0 | 96.0 | 950.0 | 93.0 | [934, 971] |
| combine | 456.0 | 685.5 | 699.0 | 1254.5 | 685.5 | [1243, 1268] |
| gmm1 | 591.0 | 596.5 | 605.0 | 353.0 | 596.5 | [336, 370] |
| gmm2 | 190.0 | 211.0 | 234.0 | 1043.5 | 211.0 | [1027, 1067] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
