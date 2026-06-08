# dispatch_ffn_combine BREAKDOWN

- valid ranks: 16 [0, 10, 11, 12, 13, 14, 15, 1, 2, 3, 4, 5, 6, 7, 8, 9]
- profile version: 10
- timeline 聚合: relative_median
- prep skew (µs): median=1526 [985, 1658]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 985.0 | 1526.0 | 1658.0 | 0.0 | 1526.0 | [0, 0] |
| dispatch | 3036.0 | 3050.5 | 3091.0 | 1526.0 | 3050.5 | [1526, 1526] |
| swiglu | 7215.0 | 7300.0 | 7403.0 | 11741.5 | 7300.0 | [11633, 12198] |
| swiglu_w1 | 1606.0 | 1628.0 | 1638.0 | 12632.0 | 1628.0 | [12475, 12932] |
| swiglu_w2 | 935.0 | 952.0 | 966.0 | 19057.5 | 952.0 | [18821, 19638] |
| combine | 1766.0 | 5102.0 | 5272.0 | 20196.5 | 5102.0 | [19956, 20863] |
| unpermute | 857.0 | 868.0 | 883.0 | 32090.0 | 868.0 | [32089, 32092] |
| gmm1 | 16764.0 | 16921.5 | 17083.0 | 1169.0 | 16921.5 | [1055, 1689] |
| gmm2 | 9120.0 | 9295.5 | 10085.0 | 18030.0 | 9295.5 | [17335, 18384] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
