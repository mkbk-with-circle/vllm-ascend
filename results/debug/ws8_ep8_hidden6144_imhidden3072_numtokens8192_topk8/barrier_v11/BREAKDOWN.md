# dispatch_ffn_combine BREAKDOWN

- valid ranks: 8 [0, 1, 2, 3, 4, 5, 6, 7]
- profile version: 11
- timeline 聚合: relative_median
- prep skew (µs): median=1006 [702, 1089]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 702.0 | 1006.5 | 1089.0 | 0.0 | 1006.5 | [0, 0] |
| dispatch | 4092.0 | 4133.0 | 4184.0 | 1006.5 | 4133.0 | [1006, 1006] |
| swiglu | 7964.0 | 8156.5 | 8304.0 | 14010.5 | 8156.5 | [13842, 14166] |
| swiglu_w1 | 1637.0 | 1650.0 | 1659.0 | 14010.5 | 1650.0 | [13842, 14166] |
| swiglu_w2 | 962.0 | 978.0 | 995.0 | 21172.5 | 978.0 | [20830, 21496] |
| combine | 2874.0 | 5892.5 | 5961.0 | 22458.0 | 5892.5 | [22136, 22740] |
| unpermute | 832.0 | 837.5 | 845.0 | 33086.5 | 837.5 | [33084, 33090] |
| gmm1 | 17345.0 | 18283.0 | 18421.0 | 1221.0 | 18283.0 | [1142, 1506] |
| gmm2 | 10042.0 | 11907.0 | 12054.0 | 18090.5 | 11907.0 | [17802, 18426] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
