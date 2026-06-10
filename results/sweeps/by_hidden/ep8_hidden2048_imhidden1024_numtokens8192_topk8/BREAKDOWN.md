# dispatch_ffn_combine BREAKDOWN

- valid ranks: 8 [0, 1, 2, 3, 4, 5, 6, 7]
- profile version: 7
- timeline 聚合: relative_median
- prep skew (µs): median=584 [506, 631]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 506.0 | 584.5 | 631.0 | 0.0 | 584.5 | [0, 0] |
| dispatch | 3067.0 | 3116.0 | 3129.0 | 584.5 | 3116.0 | [584, 584] |
| swiglu | 1723.0 | 1739.0 | 1756.0 | 3582.0 | 1739.0 | [3530, 3646] |
| swiglu_w1 | 762.0 | 773.0 | 779.0 | 3582.0 | 773.0 | [3530, 3646] |
| swiglu_w2 | 689.0 | 694.0 | 701.0 | 4632.0 | 694.0 | [4586, 4696] |
| combine | 3238.0 | 4609.5 | 4706.0 | 6185.0 | 4609.5 | [6120, 6944] |
| gmm1 | 2634.0 | 2646.5 | 2680.0 | 1979.5 | 2646.5 | [1900, 2036] |
| gmm2 | 782.0 | 848.0 | 1459.0 | 5327.0 | 848.0 | [5278, 5396] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
