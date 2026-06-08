# dispatch_ffn_combine BREAKDOWN

- valid ranks: 16 [0, 10, 11, 12, 13, 14, 15, 1, 2, 3, 4, 5, 6, 7, 8, 9]
- profile version: 10
- timeline 聚合: relative_median
- prep skew (µs): median=1649 [1340, 1878]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 1340.0 | 1649.0 | 1878.0 | 0.0 | 1649.0 | [0, 0] |
| dispatch | 3474.0 | 3491.0 | 3514.0 | 1649.0 | 3491.0 | [1649, 1649] |
| swiglu | 9567.0 | 10291.5 | 10416.0 | 16488.0 | 10291.5 | [16100, 17034] |
| swiglu_w1 | 1795.0 | 1817.5 | 1826.0 | 17435.0 | 1817.5 | [17265, 18147] |
| swiglu_w2 | 1026.0 | 1036.0 | 1083.0 | 26749.5 | 1036.0 | [26489, 28253] |
| combine | 1995.0 | 5901.5 | 6074.0 | 28251.0 | 5901.5 | [27965, 30039] |
| unpermute | 957.0 | 993.5 | 1004.0 | 46391.0 | 993.5 | [46390, 46393] |
| gmm1 | 23869.0 | 24394.5 | 24709.0 | 1255.0 | 24394.5 | [1095, 1651] |
| gmm2 | 11595.0 | 11881.5 | 12519.0 | 25532.0 | 11881.5 | [25274, 25874] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
