# dispatch_ffn_combine BREAKDOWN

- valid ranks: 8 [0, 1, 2, 3, 4, 5, 6, 7]
- profile version: 10
- timeline 聚合: relative_median
- prep skew (µs): median=664 [605, 688]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 605.0 | 663.5 | 688.0 | 0.0 | 663.5 | [0, 0] |
| dispatch | 3691.0 | 3726.5 | 3757.0 | 663.5 | 3726.5 | [664, 664] |
| swiglu | 3837.0 | 3902.0 | 4225.0 | 6542.5 | 3902.0 | [6370, 6872] |
| swiglu_w1 | 1299.0 | 1306.5 | 1313.0 | 6629.5 | 1306.5 | [6602, 6724] |
| swiglu_w2 | 779.0 | 794.5 | 802.0 | 9734.5 | 794.5 | [9684, 9886] |
| combine | 2584.0 | 5394.0 | 5470.0 | 10543.0 | 5394.0 | [10488, 10686] |
| unpermute | 581.0 | 586.0 | 592.0 | 16646.0 | 586.0 | [16642, 16646] |
| gmm1 | 7491.0 | 7552.0 | 8562.0 | 999.5 | 7552.0 | [992, 1100] |
| gmm2 | 4292.0 | 4739.5 | 5805.0 | 8448.0 | 4739.5 | [7426, 9628] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
