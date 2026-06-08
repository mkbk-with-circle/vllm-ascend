# dispatch_ffn_combine BREAKDOWN

- valid ranks: 4 [0, 1, 2, 3]
- profile version: 10
- timeline 聚合: relative_median
- prep skew (µs): median=686 [641, 769]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 641.0 | 685.5 | 769.0 | 0.0 | 685.5 | [0, 0] |
| dispatch | 6792.0 | 6816.0 | 6884.0 | 685.5 | 6816.0 | [686, 686] |
| swiglu | 4258.0 | 4314.5 | 4362.0 | 8285.0 | 4314.5 | [8240, 8404] |
| swiglu_w1 | 1272.0 | 1279.0 | 1294.0 | 8285.0 | 1279.0 | [8240, 8404] |
| swiglu_w2 | 753.0 | 756.0 | 763.0 | 11844.0 | 756.0 | [11750, 11996] |
| combine | 4813.0 | 7262.5 | 9756.0 | 12620.5 | 7262.5 | [12538, 12712] |
| unpermute | 581.0 | 589.5 | 593.0 | 22803.5 | 589.5 | [22772, 22814] |
| gmm1 | 7152.0 | 7217.5 | 7510.0 | 1338.0 | 7217.5 | [1316, 1346] |
| gmm2 | 5084.0 | 5253.5 | 5467.0 | 9386.5 | 5253.5 | [9272, 9518] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
