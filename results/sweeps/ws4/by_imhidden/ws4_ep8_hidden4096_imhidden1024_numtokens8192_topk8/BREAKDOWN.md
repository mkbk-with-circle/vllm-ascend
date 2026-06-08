# dispatch_ffn_combine BREAKDOWN

- valid ranks: 4 [0, 1, 2, 3]
- profile version: 10
- timeline 聚合: relative_median
- prep skew (µs): median=562 [553, 567]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 553.0 | 561.5 | 567.0 | 0.0 | 561.5 | [0, 0] |
| dispatch | 6471.0 | 6519.0 | 6558.0 | 561.5 | 6519.0 | [562, 562] |
| swiglu | 1508.0 | 1513.5 | 1523.0 | 7040.5 | 1513.5 | [6990, 7102] |
| swiglu_w1 | 908.0 | 917.0 | 925.0 | 7040.5 | 917.0 | [6990, 7102] |
| swiglu_w2 | 593.0 | 596.5 | 599.0 | 7964.5 | 596.5 | [7900, 8018] |
| combine | 4789.0 | 7262.0 | 9713.0 | 8611.0 | 7262.0 | [8552, 8644] |
| unpermute | 580.0 | 586.0 | 593.0 | 18356.0 | 586.0 | [18340, 18364] |
| gmm1 | 6141.0 | 6202.5 | 6257.0 | 1307.0 | 6202.5 | [1300, 1320] |
| gmm2 | 2846.0 | 2899.5 | 3410.0 | 7944.0 | 2899.5 | [7856, 8010] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
