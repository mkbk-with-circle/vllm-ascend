# dispatch_ffn_combine BREAKDOWN

- valid ranks: 4 [0, 1, 2, 3]
- profile version: 10
- timeline 聚合: relative_median
- prep skew (µs): median=649 [586, 717]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 586.0 | 649.0 | 717.0 | 0.0 | 649.0 | [0, 0] |
| dispatch | 6803.0 | 6825.0 | 6840.0 | 649.0 | 6825.0 | [649, 649] |
| swiglu | 6286.0 | 6309.5 | 6355.0 | 10988.5 | 6309.5 | [10926, 11193] |
| swiglu_w1 | 1627.0 | 1653.5 | 1660.0 | 10988.5 | 1653.5 | [10926, 11193] |
| swiglu_w2 | 948.0 | 950.5 | 960.0 | 16334.0 | 950.5 | [16321, 16558] |
| combine | 5032.0 | 7375.5 | 9793.0 | 17320.0 | 7375.5 | [17230, 17327] |
| unpermute | 581.0 | 593.5 | 599.0 | 27457.5 | 593.5 | [27453, 27497] |
| gmm1 | 11096.0 | 11277.0 | 15148.0 | 1362.0 | 11277.0 | [1356, 1405] |
| gmm2 | 7410.0 | 7579.0 | 12529.0 | 12460.0 | 7579.0 | [12122, 12600] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
