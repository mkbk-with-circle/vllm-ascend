# dispatch_ffn_combine BREAKDOWN

- valid ranks: 8 [0, 1, 2, 3, 4, 5, 6, 7]
- profile version: 10
- timeline 聚合: relative_median
- prep skew (µs): median=908 [733, 923]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 733.0 | 907.5 | 923.0 | 0.0 | 907.5 | [0, 0] |
| dispatch | 3703.0 | 3731.0 | 3747.0 | 907.5 | 3731.0 | [908, 908] |
| swiglu | 5437.0 | 5516.5 | 5667.0 | 9138.0 | 5516.5 | [9058, 9230] |
| swiglu_w1 | 1621.0 | 1628.5 | 1638.0 | 9138.0 | 1628.5 | [9058, 9230] |
| swiglu_w2 | 974.0 | 982.0 | 994.0 | 13649.5 | 982.0 | [13548, 13854] |
| combine | 2558.0 | 5279.0 | 5414.0 | 14643.0 | 5279.0 | [14540, 14852] |
| unpermute | 595.0 | 600.0 | 608.0 | 21795.5 | 600.0 | [21792, 21796] |
| gmm1 | 11060.0 | 12463.5 | 13090.0 | 1088.0 | 12463.5 | [1040, 1160] |
| gmm2 | 5776.0 | 8145.0 | 9159.0 | 12136.5 | 8145.0 | [11928, 12182] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
