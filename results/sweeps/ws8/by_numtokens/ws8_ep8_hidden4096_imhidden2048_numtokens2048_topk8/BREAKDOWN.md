# dispatch_ffn_combine BREAKDOWN

- valid ranks: 8 [0, 1, 2, 3, 4, 5, 6, 7]
- profile version: 10
- timeline 聚合: relative_median
- prep skew (µs): median=228 [200, 287]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 200.0 | 227.5 | 287.0 | 0.0 | 227.5 | [0, 0] |
| dispatch | 944.0 | 961.5 | 978.0 | 227.5 | 961.5 | [228, 228] |
| swiglu | 861.0 | 887.5 | 922.0 | 1586.5 | 887.5 | [1524, 1606] |
| swiglu_w1 | 315.0 | 323.0 | 330.0 | 1577.5 | 323.0 | [1552, 1604] |
| swiglu_w2 | 186.0 | 189.0 | 195.0 | 2278.5 | 189.0 | [2244, 2306] |
| combine | 631.0 | 1337.0 | 1402.0 | 2474.0 | 1337.0 | [2438, 2504] |
| unpermute | 154.0 | 158.0 | 160.0 | 4009.5 | 158.0 | [4006, 4012] |
| gmm1 | 1785.0 | 1884.0 | 1962.0 | 340.5 | 1884.0 | [318, 362] |
| gmm2 | 1063.0 | 1240.5 | 1294.0 | 2203.0 | 1240.5 | [1932, 2290] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
