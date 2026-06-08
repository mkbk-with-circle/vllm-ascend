# dispatch_ffn_combine BREAKDOWN

- valid ranks: 4 [0, 1, 2, 3]
- profile version: 10
- timeline 聚合: relative_median
- prep skew (µs): median=310 [296, 340]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 296.0 | 309.5 | 340.0 | 0.0 | 309.5 | [0, 0] |
| dispatch | 3362.0 | 3383.5 | 3430.0 | 309.5 | 3383.5 | [310, 310] |
| swiglu | 2083.0 | 2111.5 | 2146.0 | 3756.0 | 2111.5 | [3686, 3768] |
| swiglu_w1 | 666.0 | 672.0 | 679.0 | 3756.0 | 672.0 | [3686, 3768] |
| swiglu_w2 | 383.0 | 388.0 | 393.0 | 5480.0 | 388.0 | [5390, 5516] |
| combine | 2518.0 | 3683.0 | 4911.0 | 5799.5 | 3683.0 | [5792, 5900] |
| unpermute | 315.0 | 318.0 | 321.0 | 10934.5 | 318.0 | [10930, 10980] |
| gmm1 | 3520.0 | 3592.0 | 3603.0 | 680.0 | 3592.0 | [672, 722] |
| gmm2 | 2443.0 | 2493.0 | 2595.0 | 4332.0 | 2493.0 | [4288, 4404] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
