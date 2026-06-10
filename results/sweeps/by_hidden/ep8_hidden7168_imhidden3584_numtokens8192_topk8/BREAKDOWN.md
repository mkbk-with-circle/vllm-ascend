# dispatch_ffn_combine BREAKDOWN

- valid ranks: 8 [0, 1, 2, 3, 4, 5, 6, 7]
- profile version: 7
- timeline 聚合: relative_median
- prep skew (µs): median=1164 [964, 1299]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 964.0 | 1164.0 | 1299.0 | 0.0 | 1164.0 | [0, 0] |
| dispatch | 4169.0 | 4203.5 | 4210.0 | 1164.0 | 4203.5 | [1164, 1164] |
| swiglu | 14311.0 | 14367.0 | 14495.0 | 15682.5 | 14367.0 | [15393, 15782] |
| swiglu_w1 | 1419.0 | 1437.5 | 1459.0 | 15682.5 | 1437.5 | [15393, 15782] |
| swiglu_w2 | 1211.0 | 1220.0 | 1229.0 | 28819.5 | 1220.0 | [28523, 28983] |
| combine | 4860.0 | 6861.0 | 6935.0 | 42788.5 | 6861.0 | [42422, 43608] |
| gmm1 | 25710.0 | 25923.0 | 26043.0 | 2886.0 | 25923.0 | [2773, 3003] |
| gmm2 | 11984.0 | 12203.0 | 12468.0 | 30037.5 | 12203.0 | [29743, 30211] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
