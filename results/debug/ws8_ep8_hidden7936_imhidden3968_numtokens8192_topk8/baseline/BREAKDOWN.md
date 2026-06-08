# dispatch_ffn_combine BREAKDOWN

- valid ranks: 8 [0, 1, 2, 3, 4, 5, 6, 7]
- profile version: 10
- timeline 聚合: relative_median
- prep skew (µs): median=1458 [1076, 1591]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 1076.0 | 1457.5 | 1591.0 | 0.0 | 1457.5 | [0, 0] |
| dispatch | 4428.0 | 4498.5 | 4518.0 | 1457.5 | 4498.5 | [1458, 1458] |
| swiglu | 12250.0 | 12548.0 | 13535.0 | 22916.0 | 12548.0 | [21846, 23284] |
| swiglu_w1 | 1852.0 | 1888.5 | 1931.0 | 22588.5 | 1888.5 | [22228, 22956] |
| swiglu_w2 | 1123.0 | 1127.5 | 1137.0 | 34235.0 | 1127.5 | [33530, 34962] |
| combine | 3482.0 | 6664.5 | 6910.0 | 36293.5 | 6664.5 | [35530, 37064] |
| unpermute | 1031.0 | 1048.0 | 1077.0 | 52846.5 | 1048.0 | [52844, 52848] |
| gmm1 | 29378.0 | 29732.5 | 33220.0 | 2191.0 | 29732.5 | [1452, 2396] |
| gmm2 | 14056.0 | 15007.5 | 20613.0 | 31015.5 | 15007.5 | [29762, 31452] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
