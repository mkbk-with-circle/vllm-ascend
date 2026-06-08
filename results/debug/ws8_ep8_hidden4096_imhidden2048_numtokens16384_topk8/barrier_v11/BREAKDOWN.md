# dispatch_ffn_combine BREAKDOWN

- valid ranks: 8 [0, 1, 2, 3, 4, 5, 6, 7]
- profile version: 11
- timeline 聚合: relative_median
- prep skew (µs): median=1267 [1162, 1360]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 1162.0 | 1267.0 | 1360.0 | 0.0 | 1267.0 | [0, 0] |
| dispatch | 7262.0 | 7300.5 | 7361.0 | 1267.0 | 7300.5 | [1267, 1267] |
| swiglu | 7148.0 | 7264.0 | 7325.0 | 12606.0 | 7264.0 | [12518, 12741] |
| swiglu_w1 | 2532.0 | 2552.5 | 2565.0 | 12606.0 | 2552.5 | [12518, 12741] |
| swiglu_w2 | 1561.0 | 1572.0 | 1583.0 | 18308.0 | 1572.0 | [18105, 18489] |
| combine | 5233.0 | 10855.5 | 10978.0 | 19889.0 | 10855.5 | [19677, 20077] |
| unpermute | 1099.0 | 1112.5 | 1127.0 | 31477.0 | 1112.5 | [31476, 31478] |
| gmm1 | 13896.0 | 13984.5 | 14653.0 | 2000.0 | 13984.5 | [1908, 2185] |
| gmm2 | 7940.0 | 8172.0 | 8257.0 | 15763.5 | 8172.0 | [15692, 15947] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
