# dispatch_ffn_combine BREAKDOWN

- valid ranks: 8 [0, 1, 2, 3, 4, 5, 6, 7]
- profile version: 10
- timeline 聚合: relative_median
- prep skew (µs): median=322 [312, 366]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 312.0 | 321.5 | 366.0 | 0.0 | 321.5 | [0, 0] |
| dispatch | 1858.0 | 1889.5 | 1909.0 | 321.5 | 1889.5 | [322, 322] |
| swiglu | 1813.0 | 1844.0 | 1868.0 | 3001.5 | 1844.0 | [2980, 3026] |
| swiglu_w1 | 647.0 | 662.0 | 667.0 | 3021.5 | 662.0 | [2954, 3056] |
| swiglu_w2 | 398.0 | 401.0 | 408.0 | 4476.0 | 401.0 | [4380, 4520] |
| combine | 1357.0 | 2724.0 | 2763.0 | 4887.0 | 2724.0 | [4786, 4934] |
| unpermute | 326.0 | 332.0 | 333.0 | 7889.0 | 332.0 | [7888, 7890] |
| gmm1 | 3516.0 | 3610.0 | 3894.0 | 531.0 | 3610.0 | [514, 568] |
| gmm2 | 2075.0 | 2398.0 | 2798.0 | 4029.5 | 2398.0 | [3958, 4372] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
