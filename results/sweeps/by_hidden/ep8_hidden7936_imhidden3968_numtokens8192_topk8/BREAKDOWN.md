# dispatch_ffn_combine BREAKDOWN

- valid ranks: 8 [0, 1, 2, 3, 4, 5, 6, 7]
- profile version: 7
- timeline 聚合: relative_median
- prep skew (µs): median=1628 [1190, 1699]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 1190.0 | 1628.5 | 1699.0 | 0.0 | 1628.5 | [0, 0] |
| dispatch | 4242.0 | 4302.5 | 4382.0 | 1628.5 | 4302.5 | [1628, 1628] |
| swiglu | 16929.0 | 17022.5 | 17223.0 | 18562.0 | 17022.5 | [18324, 19236] |
| swiglu_w1 | 1506.0 | 1512.5 | 1528.0 | 18562.0 | 1512.5 | [18324, 19236] |
| swiglu_w2 | 1281.0 | 1292.0 | 1298.0 | 34321.5 | 1292.0 | [34010, 34884] |
| combine | 5149.0 | 7217.0 | 7329.0 | 51755.5 | 7217.0 | [51298, 52140] |
| gmm1 | 31199.0 | 31315.0 | 31612.0 | 3002.5 | 31315.0 | [2804, 3502] |
| gmm2 | 14592.0 | 14832.5 | 14959.0 | 35611.0 | 14832.5 | [35290, 36176] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
