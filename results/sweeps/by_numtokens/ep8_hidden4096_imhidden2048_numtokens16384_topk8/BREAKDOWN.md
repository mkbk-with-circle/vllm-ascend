# dispatch_ffn_combine BREAKDOWN

- valid ranks: 8 [0, 1, 2, 3, 4, 5, 6, 7]
- profile version: 7
- timeline 聚合: relative_median
- prep skew (µs): median=1597 [1366, 1688]
- timeline repaired: ['combine']

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 1366.0 | 1597.0 | 1688.0 | 0.0 | 1597.0 | [0, 0] |
| dispatch | 7029.0 | 7054.0 | 7091.0 | 1597.0 | 7054.0 | [1597, 1597] |
| swiglu | 9240.0 | 9352.0 | 9498.0 | 13075.0 | 9352.0 | [12278, 13296] |
| swiglu_w1 | 2066.0 | 2077.5 | 2097.0 | 13075.0 | 2077.5 | [12278, 13296] |
| swiglu_w2 | 1801.0 | 1820.5 | 1832.0 | 20587.0 | 1820.5 | [19949, 20799] |
| combine | 8269.0 | 10953.5 | 11012.0 | 31685.0 | 10953.5 | [31422, 31886] |
| gmm1 | 15021.0 | 15318.5 | 15560.0 | 5282.5 | 15318.5 | [4491, 5602] |
| gmm2 | 9228.0 | 9273.0 | 9288.0 | 22412.0 | 9273.0 | [21776, 22611] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
