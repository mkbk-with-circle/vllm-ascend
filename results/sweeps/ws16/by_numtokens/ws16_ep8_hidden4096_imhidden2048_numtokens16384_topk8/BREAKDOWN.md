# dispatch_ffn_combine BREAKDOWN

- valid ranks: 16 [0, 10, 11, 12, 13, 14, 15, 1, 2, 3, 4, 5, 6, 7, 8, 9]
- profile version: 10
- timeline 聚合: relative_median
- prep skew (µs): median=1452 [1301, 1584]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 1301.0 | 1452.0 | 1584.0 | 0.0 | 1452.0 | [0, 0] |
| dispatch | 4418.0 | 4465.5 | 4522.0 | 1452.0 | 4465.5 | [1452, 1452] |
| swiglu | 6948.0 | 7008.5 | 7073.0 | 10628.5 | 7008.5 | [10360, 10990] |
| swiglu_w1 | 2526.0 | 2545.0 | 2597.0 | 10927.0 | 2545.0 | [10816, 11291] |
| swiglu_w2 | 1542.0 | 1556.0 | 1579.0 | 16396.5 | 1556.0 | [16275, 16810] |
| combine | 3209.0 | 7118.5 | 7244.0 | 17966.5 | 7118.5 | [17835, 18398] |
| unpermute | 1121.0 | 1133.0 | 1142.0 | 27861.0 | 1133.0 | [27860, 27864] |
| gmm1 | 14218.0 | 14327.5 | 14805.0 | 1693.5 | 14327.5 | [1524, 1801] |
| gmm2 | 8144.0 | 8214.5 | 9735.0 | 16043.5 | 8214.5 | [15837, 16456] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
