# dispatch_ffn_combine BREAKDOWN

- valid ranks: 16 [0, 10, 11, 12, 13, 14, 15, 1, 2, 3, 4, 5, 6, 7, 8, 9]
- profile version: 10
- timeline 聚合: relative_median
- prep skew (µs): median=1470 [1282, 1561]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 1282.0 | 1470.0 | 1561.0 | 0.0 | 1470.0 | [0, 0] |
| dispatch | 4412.0 | 4463.0 | 4531.0 | 1470.0 | 4463.0 | [1470, 1470] |
| swiglu | 6969.0 | 7006.5 | 7056.0 | 10634.0 | 7006.5 | [10436, 10948] |
| swiglu_w1 | 2523.0 | 2538.5 | 2596.0 | 10951.0 | 2538.5 | [10785, 11284] |
| swiglu_w2 | 1545.0 | 1559.5 | 1569.0 | 16420.5 | 1559.5 | [16230, 16767] |
| combine | 3249.0 | 7048.5 | 7327.0 | 17989.0 | 7048.5 | [17789, 18336] |
| unpermute | 1043.0 | 1057.0 | 1069.0 | 27567.0 | 1057.0 | [27566, 27568] |
| gmm1 | 14195.0 | 14348.5 | 14580.0 | 1707.0 | 14348.5 | [1528, 2023] |
| gmm2 | 8118.0 | 8203.0 | 9712.0 | 16055.5 | 8203.0 | [15889, 16350] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
