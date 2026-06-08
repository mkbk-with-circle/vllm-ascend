# dispatch_ffn_combine BREAKDOWN

- valid ranks: 16 [0, 10, 11, 12, 13, 14, 15, 1, 2, 3, 4, 5, 6, 7, 8, 9]
- profile version: 10
- timeline 聚合: relative_median
- prep skew (µs): median=812 [633, 862]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 633.0 | 812.5 | 862.0 | 0.0 | 812.5 | [0, 0] |
| dispatch | 2257.0 | 2285.5 | 2316.0 | 812.5 | 2285.5 | [812, 812] |
| swiglu | 3421.0 | 3457.0 | 3488.0 | 5550.0 | 3457.0 | [5468, 5660] |
| swiglu_w1 | 1252.0 | 1260.0 | 1273.0 | 5763.0 | 1260.0 | [5712, 5810] |
| swiglu_w2 | 758.0 | 762.5 | 771.0 | 8454.5 | 762.5 | [8406, 8496] |
| combine | 1390.0 | 3613.0 | 3707.0 | 9223.5 | 3613.0 | [9174, 9272] |
| unpermute | 632.0 | 637.0 | 640.0 | 13629.5 | 637.0 | [13628, 13632] |
| gmm1 | 7277.0 | 7331.0 | 7399.0 | 880.5 | 7331.0 | [822, 1086] |
| gmm2 | 4549.0 | 4613.5 | 4756.0 | 8173.0 | 4613.5 | [7976, 8280] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
