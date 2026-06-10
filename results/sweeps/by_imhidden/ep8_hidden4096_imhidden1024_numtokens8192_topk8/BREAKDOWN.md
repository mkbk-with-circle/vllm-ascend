# dispatch_ffn_combine BREAKDOWN

- valid ranks: 8 [0, 1, 2, 3, 4, 5, 6, 7]
- profile version: 7
- timeline 聚合: relative_median
- prep skew (µs): median=730 [593, 763]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 593.0 | 730.0 | 763.0 | 0.0 | 730.0 | [0, 0] |
| dispatch | 3509.0 | 3556.5 | 3586.0 | 730.0 | 3556.5 | [730, 730] |
| swiglu | 2398.0 | 2478.0 | 2530.0 | 4374.0 | 2478.0 | [4318, 4465] |
| swiglu_w1 | 761.0 | 768.5 | 782.0 | 4374.0 | 768.5 | [4318, 4465] |
| swiglu_w2 | 689.0 | 700.5 | 703.0 | 6172.5 | 700.5 | [6066, 6207] |
| combine | 3910.0 | 5472.0 | 5539.0 | 10206.5 | 5472.0 | [10107, 10282] |
| gmm1 | 3754.0 | 3838.0 | 3912.0 | 2291.0 | 3838.0 | [2286, 2409] |
| gmm2 | 3127.0 | 3163.5 | 3199.0 | 6872.0 | 3163.5 | [6755, 6905] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
