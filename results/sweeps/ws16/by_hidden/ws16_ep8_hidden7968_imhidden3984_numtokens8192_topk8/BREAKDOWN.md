# dispatch_ffn_combine BREAKDOWN

- valid ranks: 16 [0, 10, 11, 12, 13, 14, 15, 1, 2, 3, 4, 5, 6, 7, 8, 9]
- profile version: 10
- timeline 聚合: relative_median
- prep skew (µs): median=1463 [1100, 1533]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 1100.0 | 1463.0 | 1533.0 | 0.0 | 1463.0 | [0, 0] |
| dispatch | 3801.0 | 3812.0 | 3838.0 | 1463.0 | 3812.0 | [1463, 1463] |
| swiglu | 11224.0 | 11356.5 | 14230.0 | 19102.0 | 11356.5 | [18671, 22171] |
| swiglu_w1 | 1949.0 | 1962.0 | 1973.0 | 19113.0 | 1962.0 | [18847, 19633] |
| swiglu_w2 | 1126.0 | 1140.5 | 1156.0 | 29473.5 | 1140.5 | [29051, 30359] |
| combine | 2211.0 | 6727.5 | 6860.0 | 31286.5 | 6727.5 | [30873, 32312] |
| unpermute | 1071.0 | 1088.5 | 1101.0 | 50954.0 | 1088.5 | [50952, 50955] |
| gmm1 | 27127.0 | 27244.5 | 33127.0 | 2035.5 | 27244.5 | [1492, 2111] |
| gmm2 | 14198.0 | 15154.0 | 16034.0 | 29001.5 | 15154.0 | [27746, 39550] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
