# dispatch_ffn_combine BREAKDOWN

- valid ranks: 8 [0, 1, 2, 3, 4, 5, 6, 7]
- profile version: 10
- timeline 聚合: relative_median
- prep skew (µs): median=1149 [920, 1280]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 920.0 | 1149.0 | 1280.0 | 0.0 | 1149.0 | [0, 0] |
| dispatch | 4397.0 | 4444.5 | 4498.0 | 1149.0 | 4444.5 | [1149, 1149] |
| swiglu | 11964.0 | 12204.5 | 12330.0 | 21770.5 | 12204.5 | [21455, 21878] |
| swiglu_w1 | 1848.0 | 1868.5 | 1906.0 | 21770.5 | 1868.5 | [21455, 21878] |
| swiglu_w2 | 1108.0 | 1122.5 | 1136.0 | 32843.0 | 1122.5 | [32397, 33081] |
| combine | 3394.0 | 6558.5 | 6640.0 | 34853.5 | 6558.5 | [34351, 35070] |
| unpermute | 1011.0 | 1017.0 | 1035.0 | 50289.0 | 1017.0 | [50288, 50289] |
| gmm1 | 28500.0 | 30549.5 | 31854.0 | 1861.0 | 30549.5 | [1377, 2124] |
| gmm2 | 13943.0 | 18590.5 | 20090.0 | 29650.5 | 18590.5 | [29205, 30395] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
