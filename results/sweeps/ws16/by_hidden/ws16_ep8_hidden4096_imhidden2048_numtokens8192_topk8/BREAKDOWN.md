# dispatch_ffn_combine BREAKDOWN

- valid ranks: 16 [0, 10, 11, 12, 13, 14, 15, 1, 2, 3, 4, 5, 6, 7, 8, 9]
- profile version: 10
- timeline 聚合: relative_median
- prep skew (µs): median=736 [667, 810]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 667.0 | 736.0 | 810.0 | 0.0 | 736.0 | [0, 0] |
| dispatch | 2261.0 | 2288.5 | 2316.0 | 736.0 | 2288.5 | [736, 736] |
| swiglu | 3419.0 | 3453.5 | 3491.0 | 5644.0 | 3453.5 | [5492, 5671] |
| swiglu_w1 | 1251.0 | 1259.5 | 1273.0 | 5679.0 | 1259.5 | [5636, 5746] |
| swiglu_w2 | 755.0 | 760.5 | 772.0 | 8369.0 | 760.5 | [8328, 8430] |
| combine | 1387.0 | 3612.5 | 3720.0 | 9145.5 | 3612.5 | [9093, 9206] |
| unpermute | 629.0 | 635.0 | 640.0 | 13554.0 | 635.0 | [13553, 13556] |
| gmm1 | 7291.0 | 7333.0 | 7389.0 | 968.5 | 7333.0 | [886, 1056] |
| gmm2 | 4315.0 | 4494.0 | 4845.0 | 8164.5 | 4494.0 | [7825, 8400] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
