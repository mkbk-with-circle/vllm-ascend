# dispatch_ffn_combine BREAKDOWN

- valid ranks: 8 [0, 1, 2, 3, 4, 5, 6, 7]
- profile version: 10
- timeline 聚合: relative_median
- prep skew (µs): median=1432 [1023, 1604]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 1023.0 | 1431.5 | 1604.0 | 0.0 | 1431.5 | [0, 0] |
| dispatch | 7266.0 | 7309.5 | 7400.0 | 1431.5 | 7309.5 | [1432, 1432] |
| swiglu | 7431.0 | 7609.5 | 8124.0 | 12477.0 | 7609.5 | [12126, 12802] |
| swiglu_w1 | 2628.0 | 2646.5 | 2667.0 | 12841.5 | 2646.5 | [12770, 12960] |
| swiglu_w2 | 1581.0 | 1610.5 | 1623.0 | 18895.5 | 1610.5 | [18804, 18994] |
| combine | 5748.0 | 10794.0 | 11017.0 | 20507.0 | 10794.0 | [20430, 20608] |
| unpermute | 1020.0 | 1032.5 | 1037.0 | 32329.5 | 1032.5 | [32324, 32330] |
| gmm1 | 14261.0 | 14403.5 | 16704.0 | 1925.0 | 14403.5 | [1742, 2364] |
| gmm2 | 8214.0 | 9086.5 | 13080.0 | 16139.0 | 9086.5 | [15930, 16418] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
