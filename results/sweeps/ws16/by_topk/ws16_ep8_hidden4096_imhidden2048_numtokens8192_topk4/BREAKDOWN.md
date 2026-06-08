# dispatch_ffn_combine BREAKDOWN

- valid ranks: 16 [0, 10, 11, 12, 13, 14, 15, 1, 2, 3, 4, 5, 6, 7, 8, 9]
- profile version: 10
- timeline 聚合: relative_median
- prep skew (µs): median=614 [485, 651]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 485.0 | 613.5 | 651.0 | 0.0 | 613.5 | [0, 0] |
| dispatch | 1149.0 | 1179.5 | 1199.0 | 613.5 | 1179.5 | [614, 614] |
| swiglu | 1705.0 | 1742.5 | 1753.0 | 3006.5 | 1742.5 | [2866, 3074] |
| swiglu_w1 | 631.0 | 641.5 | 645.0 | 2989.0 | 641.5 | [2944, 3018] |
| swiglu_w2 | 374.0 | 380.0 | 385.0 | 4339.5 | 380.0 | [4306, 4378] |
| combine | 709.0 | 1783.5 | 1840.0 | 4727.0 | 1783.5 | [4696, 4766] |
| unpermute | 377.0 | 380.0 | 388.0 | 6968.5 | 380.0 | [6966, 6970] |
| gmm1 | 3537.0 | 3572.5 | 3600.0 | 772.5 | 3572.5 | [648, 858] |
| gmm2 | 2049.0 | 2326.0 | 2633.0 | 4132.5 | 2326.0 | [3920, 4384] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
