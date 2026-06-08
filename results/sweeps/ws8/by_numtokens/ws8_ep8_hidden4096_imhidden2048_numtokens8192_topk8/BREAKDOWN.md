# dispatch_ffn_combine BREAKDOWN

- valid ranks: 8 [0, 1, 2, 3, 4, 5, 6, 7]
- profile version: 10
- timeline 聚合: relative_median
- prep skew (µs): median=656 [643, 740]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 643.0 | 656.0 | 740.0 | 0.0 | 656.0 | [0, 0] |
| dispatch | 3685.0 | 3726.5 | 3757.0 | 656.0 | 3726.5 | [656, 656] |
| swiglu | 3867.0 | 3914.0 | 3946.0 | 6637.0 | 3914.0 | [6538, 6686] |
| swiglu_w1 | 1299.0 | 1307.5 | 1316.0 | 6637.0 | 1307.5 | [6538, 6686] |
| swiglu_w2 | 780.0 | 794.5 | 802.0 | 9759.5 | 794.5 | [9626, 9840] |
| combine | 2574.0 | 5393.0 | 5483.0 | 10566.5 | 5393.0 | [10436, 10641] |
| unpermute | 579.0 | 586.5 | 595.0 | 16565.0 | 586.5 | [16563, 16568] |
| gmm1 | 7479.0 | 7596.0 | 8697.0 | 997.0 | 7596.0 | [953, 1054] |
| gmm2 | 4240.0 | 4402.5 | 5729.0 | 8420.5 | 4402.5 | [8360, 10354] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
