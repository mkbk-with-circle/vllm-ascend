# dispatch_ffn_combine BREAKDOWN

- valid ranks: 8 [0, 1, 2, 3, 4, 5, 6, 7]
- profile version: 7
- timeline 聚合: relative_median
- prep skew (µs): median=1192 [859, 1240]
- timeline repaired: ['combine']

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 859.0 | 1192.0 | 1240.0 | 0.0 | 1192.0 | [0, 0] |
| dispatch | 4295.0 | 4330.0 | 4352.0 | 1192.0 | 4330.0 | [1192, 1192] |
| swiglu | 15957.0 | 17564.0 | 18434.0 | 19412.5 | 17564.0 | [18693, 19947] |
| swiglu_w1 | 1540.0 | 1554.0 | 1568.0 | 19412.5 | 1554.0 | [18693, 19947] |
| swiglu_w2 | 1327.0 | 1340.0 | 1352.0 | 35943.0 | 1340.0 | [34049, 36629] |
| combine | 5183.0 | 7326.0 | 7480.0 | 51763.5 | 7326.0 | [50672, 52508] |
| gmm1 | 30690.0 | 32792.0 | 33472.0 | 3075.5 | 32792.0 | [2949, 3354] |
| gmm2 | 14366.0 | 14486.5 | 14589.0 | 37277.0 | 14486.5 | [35389, 37969] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
