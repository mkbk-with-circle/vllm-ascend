# dispatch_ffn_combine BREAKDOWN

- valid ranks: 8 [0, 1, 2, 3, 4, 5, 6, 7]
- profile version: 10
- timeline 聚合: relative_median
- prep skew (µs): median=714 [659, 742]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 659.0 | 713.5 | 742.0 | 0.0 | 713.5 | [0, 0] |
| dispatch | 3694.0 | 3710.0 | 3770.0 | 713.5 | 3710.0 | [714, 714] |
| swiglu | 1934.0 | 2021.0 | 2166.0 | 4286.0 | 2021.0 | [4230, 4346] |
| swiglu_w1 | 974.0 | 985.0 | 991.0 | 4425.0 | 985.0 | [4410, 4486] |
| swiglu_w2 | 596.0 | 599.5 | 606.0 | 5840.0 | 599.5 | [5766, 5894] |
| combine | 2551.0 | 5443.0 | 5521.0 | 6450.0 | 5443.0 | [6372, 6508] |
| unpermute | 572.0 | 577.0 | 581.0 | 12388.5 | 577.0 | [12386, 12390] |
| gmm1 | 3792.0 | 4246.5 | 4871.0 | 1005.0 | 4246.5 | [948, 1042] |
| gmm2 | 2869.0 | 3262.0 | 4332.0 | 5237.5 | 3262.0 | [5200, 5288] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
