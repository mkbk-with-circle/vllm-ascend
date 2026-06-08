# dispatch_ffn_combine BREAKDOWN

- valid ranks: 4 [0, 1, 2, 3]
- profile version: 10
- timeline 聚合: relative_median
- prep skew (µs): median=1090 [990, 1164]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 990.0 | 1090.5 | 1164.0 | 0.0 | 1090.5 | [0, 0] |
| dispatch | 7447.0 | 7495.0 | 7586.0 | 1090.5 | 7495.0 | [1090, 1090] |
| swiglu | 14105.0 | 14297.5 | 14432.0 | 26353.5 | 14297.5 | [26044, 26558] |
| swiglu_w1 | 1954.0 | 1965.0 | 1971.0 | 26353.5 | 1965.0 | [26044, 26558] |
| swiglu_w2 | 1125.0 | 1126.5 | 1134.0 | 39479.0 | 1126.5 | [39140, 39832] |
| combine | 6599.0 | 9643.5 | 12721.0 | 41794.0 | 9643.5 | [41394, 41970] |
| unpermute | 1033.0 | 1051.5 | 1082.0 | 60824.5 | 1051.5 | [60722, 60962] |
| gmm1 | 29562.0 | 29768.5 | 29823.0 | 1698.5 | 29768.5 | [1574, 1848] |
| gmm2 | 15563.0 | 15880.0 | 16105.0 | 31320.5 | 15880.0 | [31006, 31554] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
