# dispatch_ffn_combine BREAKDOWN

- valid ranks: 4 [0, 1, 2, 3]
- profile version: 10
- timeline 聚合: relative_median
- prep skew (µs): median=986 [686, 1004]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 686.0 | 986.0 | 1004.0 | 0.0 | 986.0 | [0, 0] |
| dispatch | 7175.0 | 7197.5 | 7221.0 | 986.0 | 7197.5 | [986, 986] |
| swiglu | 8617.0 | 8857.0 | 9030.0 | 17039.0 | 8857.0 | [16630, 17220] |
| swiglu_w1 | 1625.0 | 1637.0 | 1656.0 | 17039.0 | 1637.0 | [16630, 17220] |
| swiglu_w2 | 941.0 | 944.0 | 950.0 | 24952.0 | 944.0 | [24306, 25300] |
| combine | 5495.0 | 8105.5 | 10769.0 | 26361.0 | 8105.5 | [26331, 26462] |
| unpermute | 808.0 | 822.0 | 847.0 | 39242.5 | 822.0 | [39167, 39521] |
| gmm1 | 16206.0 | 16517.0 | 23775.0 | 1536.0 | 16517.0 | [1462, 1797] |
| gmm2 | 11591.0 | 12152.0 | 19808.0 | 18273.5 | 12152.0 | [18165, 18596] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
