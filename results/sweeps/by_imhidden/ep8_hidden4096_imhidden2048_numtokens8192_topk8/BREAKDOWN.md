# dispatch_ffn_combine BREAKDOWN

- valid ranks: 8 [0, 1, 2, 3, 4, 5, 6, 7]
- profile version: 7
- timeline 聚合: relative_median
- prep skew (µs): median=714 [698, 741]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 698.0 | 713.5 | 741.0 | 0.0 | 713.5 | [0, 0] |
| dispatch | 3513.0 | 3533.5 | 3554.0 | 713.5 | 3533.5 | [714, 714] |
| swiglu | 4338.0 | 4374.5 | 4417.0 | 6055.0 | 4374.5 | [6016, 6084] |
| swiglu_w1 | 993.0 | 1003.0 | 1009.0 | 6055.0 | 1003.0 | [6016, 6084] |
| swiglu_w2 | 897.0 | 903.0 | 916.0 | 9539.5 | 903.0 | [9462, 9562] |
| combine | 3856.0 | 5476.0 | 5529.0 | 15046.5 | 5476.0 | [14986, 15150] |
| gmm1 | 7196.0 | 7247.0 | 7277.0 | 2277.5 | 7247.0 | [2258, 2314] |
| gmm2 | 4435.0 | 4467.0 | 4510.0 | 10441.5 | 4467.0 | [10362, 10478] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
