# dispatch_ffn_combine BREAKDOWN

- valid ranks: 16 [0, 10, 11, 12, 13, 14, 15, 1, 2, 3, 4, 5, 6, 7, 8, 9]
- profile version: 10
- timeline 聚合: relative_median
- prep skew (µs): median=774 [658, 841]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 658.0 | 774.5 | 841.0 | 0.0 | 774.5 | [0, 0] |
| dispatch | 2253.0 | 2293.5 | 2346.0 | 774.5 | 2293.5 | [774, 774] |
| swiglu | 2043.0 | 2113.0 | 2156.0 | 3603.5 | 2113.0 | [3376, 3914] |
| swiglu_w1 | 973.0 | 982.5 | 991.0 | 3689.5 | 982.5 | [3620, 3772] |
| swiglu_w2 | 578.0 | 586.0 | 595.0 | 5203.5 | 586.0 | [5128, 5262] |
| combine | 1477.0 | 3635.0 | 3759.0 | 5799.5 | 3635.0 | [5722, 5858] |
| unpermute | 566.0 | 574.5 | 580.0 | 9971.5 | 574.5 | [9968, 9972] |
| gmm1 | 4028.0 | 4092.5 | 4386.0 | 987.0 | 4092.5 | [834, 1076] |
| gmm2 | 2983.0 | 3318.5 | 3772.0 | 5026.5 | 3318.5 | [4602, 5222] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
