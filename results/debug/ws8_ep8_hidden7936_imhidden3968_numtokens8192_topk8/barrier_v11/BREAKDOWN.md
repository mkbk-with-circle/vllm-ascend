# dispatch_ffn_combine BREAKDOWN

- valid ranks: 8 [0, 1, 2, 3, 4, 5, 6, 7]
- profile version: 11
- timeline 聚合: relative_median
- prep skew (µs): median=1553 [966, 1677]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 966.0 | 1553.0 | 1677.0 | 0.0 | 1553.0 | [0, 0] |
| dispatch | 4432.0 | 4495.5 | 4519.0 | 1553.0 | 4495.5 | [1553, 1553] |
| swiglu | 12462.0 | 12681.0 | 13272.0 | 22700.5 | 12681.0 | [22379, 23078] |
| swiglu_w1 | 1860.0 | 1890.0 | 1919.0 | 22700.5 | 1890.0 | [22379, 23078] |
| swiglu_w2 | 1123.0 | 1124.0 | 1132.0 | 34316.5 | 1124.0 | [33718, 35003] |
| combine | 3489.0 | 6659.5 | 6900.0 | 36375.5 | 6659.5 | [35720, 37099] |
| unpermute | 1033.0 | 1047.0 | 1074.0 | 52462.5 | 1047.0 | [52460, 52466] |
| gmm1 | 29832.0 | 32391.0 | 34223.0 | 1507.5 | 32391.0 | [1411, 2127] |
| gmm2 | 14615.0 | 19335.0 | 21033.0 | 30937.0 | 19335.0 | [28265, 31931] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
