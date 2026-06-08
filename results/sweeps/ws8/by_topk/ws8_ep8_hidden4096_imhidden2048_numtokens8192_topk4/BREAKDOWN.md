# dispatch_ffn_combine BREAKDOWN

- valid ranks: 8 [0, 1, 2, 3, 4, 5, 6, 7]
- profile version: 10
- timeline 聚合: relative_median
- prep skew (µs): median=456 [399, 477]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 399.0 | 455.5 | 477.0 | 0.0 | 455.5 | [0, 0] |
| dispatch | 1859.0 | 1887.0 | 1907.0 | 455.5 | 1887.0 | [456, 456] |
| swiglu | 1806.0 | 1844.5 | 1925.0 | 3131.0 | 1844.5 | [3070, 3184] |
| swiglu_w1 | 646.0 | 664.5 | 668.0 | 3152.0 | 664.5 | [3090, 3188] |
| swiglu_w2 | 393.0 | 400.0 | 412.0 | 4595.0 | 400.0 | [4508, 4664] |
| combine | 1374.0 | 2706.0 | 2747.0 | 5003.0 | 2706.0 | [4910, 5086] |
| unpermute | 336.0 | 343.0 | 349.0 | 8029.5 | 343.0 | [8028, 8030] |
| gmm1 | 3529.0 | 3583.0 | 3935.0 | 667.0 | 3583.0 | [620, 676] |
| gmm2 | 2093.0 | 2394.5 | 3200.0 | 4153.5 | 2394.5 | [4078, 4204] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
