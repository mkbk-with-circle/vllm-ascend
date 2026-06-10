# dispatch_ffn_combine BREAKDOWN

- valid ranks: 8 [0, 1, 2, 3, 4, 5, 6, 7]
- profile version: 7
- timeline 聚合: relative_median
- prep skew (µs): median=1291 [965, 1360]
- timeline repaired: ['combine']

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 965.0 | 1291.0 | 1360.0 | 0.0 | 1291.0 | [0, 0] |
| dispatch | 4281.0 | 4295.0 | 4335.0 | 1291.0 | 4295.0 | [1291, 1291] |
| swiglu | 16822.0 | 16982.0 | 17002.0 | 18906.0 | 16982.0 | [18690, 19142] |
| swiglu_w1 | 1519.0 | 1543.0 | 1553.0 | 18906.0 | 1543.0 | [18690, 19142] |
| swiglu_w2 | 1257.0 | 1267.0 | 1274.0 | 34585.0 | 1267.0 | [34401, 34815] |
| combine | 5112.0 | 7225.0 | 7281.0 | 49972.0 | 7225.0 | [49750, 50278] |
| gmm1 | 30806.0 | 30995.0 | 31241.0 | 3597.5 | 30995.0 | [3162, 3926] |
| gmm2 | 13926.0 | 14119.5 | 14400.0 | 35852.5 | 14119.5 | [35666, 36084] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
