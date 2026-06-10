# dispatch_ffn_combine BREAKDOWN

- valid ranks: 8 [0, 1, 2, 3, 4, 5, 6, 7]
- profile version: 7
- timeline 聚合: relative_median
- prep skew (µs): median=4042 [3902, 4203]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 3902.0 | 4042.0 | 4203.0 | 0.0 | 4042.0 | [0, 0] |
| dispatch | 23611.0 | 23710.5 | 23898.0 | 4042.0 | 23710.5 | [4042, 4042] |
| swiglu | 59082.0 | 65924.0 | 68353.0 | 79247.5 | 65924.0 | [71809, 81101] |
| swiglu_w1 | 7753.0 | 7839.5 | 7926.0 | 79247.5 | 7839.5 | [71809, 81101] |
| swiglu_w2 | 6673.0 | 6712.0 | 6739.0 | 138789.5 | 6712.0 | [124184, 142376] |
| combine | 25681.0 | 35701.0 | 36240.0 | 203054.5 | 35701.0 | [199544, 205321] |
| gmm1 | 108363.0 | 123148.5 | 126911.0 | 15514.5 | 123148.5 | [15212, 15815] |
| gmm2 | 54824.0 | 56767.0 | 59683.0 | 145499.0 | 56767.0 | [130891, 149108] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
