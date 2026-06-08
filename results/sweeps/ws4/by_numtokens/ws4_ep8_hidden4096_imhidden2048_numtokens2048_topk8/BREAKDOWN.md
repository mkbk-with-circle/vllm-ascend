# dispatch_ffn_combine BREAKDOWN

- valid ranks: 4 [0, 1, 2, 3]
- profile version: 10
- timeline 聚合: relative_median
- prep skew (µs): median=204 [198, 237]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 198.0 | 204.5 | 237.0 | 0.0 | 204.5 | [0, 0] |
| dispatch | 1676.0 | 1702.5 | 1714.0 | 204.5 | 1702.5 | [204, 204] |
| swiglu | 927.0 | 939.0 | 1011.0 | 1926.5 | 939.0 | [1896, 1934] |
| swiglu_w1 | 334.0 | 335.5 | 343.0 | 1926.5 | 335.5 | [1896, 1934] |
| swiglu_w2 | 193.0 | 195.0 | 198.0 | 2665.5 | 195.0 | [2640, 2748] |
| combine | 1205.0 | 1823.0 | 2435.0 | 2836.5 | 1823.0 | [2802, 2878] |
| unpermute | 143.0 | 144.5 | 149.0 | 5470.5 | 144.5 | [5442, 5496] |
| gmm1 | 1778.0 | 1828.0 | 2321.0 | 416.0 | 1828.0 | [402, 432] |
| gmm2 | 1123.0 | 1128.5 | 1272.0 | 2259.0 | 1128.5 | [2220, 2914] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
