# dispatch_ffn_combine BREAKDOWN

- valid ranks: 8 [0, 1, 2, 3, 4, 5, 6, 7]
- profile version: 10
- timeline 聚合: relative_median
- prep skew (µs): median=1032 [1004, 1159]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 1004.0 | 1032.0 | 1159.0 | 0.0 | 1032.0 | [0, 0] |
| dispatch | 4090.0 | 4136.5 | 4179.0 | 1032.0 | 4136.5 | [1032, 1032] |
| swiglu | 7330.0 | 7955.0 | 8637.0 | 13368.5 | 7955.0 | [12767, 14512] |
| swiglu_w1 | 1638.0 | 1652.5 | 1666.0 | 14068.5 | 1652.5 | [13838, 14354] |
| swiglu_w2 | 962.0 | 974.0 | 993.0 | 21257.0 | 974.0 | [20980, 21797] |
| combine | 2890.0 | 5875.0 | 5955.0 | 22532.0 | 5875.0 | [22273, 23073] |
| unpermute | 831.0 | 841.0 | 848.0 | 33167.0 | 841.0 | [33166, 33168] |
| gmm1 | 16475.0 | 17380.5 | 18744.0 | 1177.5 | 17380.5 | [1022, 1370] |
| gmm2 | 8843.0 | 10620.5 | 12076.0 | 17866.5 | 10620.5 | [17564, 18280] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
