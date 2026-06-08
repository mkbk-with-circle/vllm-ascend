# dispatch_ffn_combine BREAKDOWN

- valid ranks: 16 [0, 10, 11, 12, 13, 14, 15, 1, 2, 3, 4, 5, 6, 7, 8, 9]
- profile version: 10
- timeline 聚合: relative_median
- prep skew (µs): median=1403 [1045, 1450]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 1045.0 | 1403.0 | 1450.0 | 0.0 | 1403.0 | [0, 0] |
| dispatch | 3834.0 | 3847.5 | 3861.0 | 1403.0 | 3847.5 | [1403, 1403] |
| swiglu | 11868.0 | 12022.0 | 12117.0 | 19534.5 | 12022.0 | [19372, 20090] |
| swiglu_w1 | 1945.0 | 1957.0 | 1987.0 | 20243.0 | 1957.0 | [19941, 20570] |
| swiglu_w2 | 1123.0 | 1128.5 | 1144.0 | 31168.5 | 1128.5 | [30810, 31971] |
| combine | 2196.0 | 6535.5 | 6755.0 | 32954.0 | 6535.5 | [32524, 33837] |
| unpermute | 1074.0 | 1087.5 | 1097.0 | 50639.0 | 1087.5 | [50638, 50641] |
| gmm1 | 28846.0 | 29108.5 | 29436.0 | 1355.0 | 29108.5 | [1246, 1660] |
| gmm2 | 14008.0 | 14209.0 | 15068.0 | 30350.5 | 14209.0 | [30078, 30878] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
