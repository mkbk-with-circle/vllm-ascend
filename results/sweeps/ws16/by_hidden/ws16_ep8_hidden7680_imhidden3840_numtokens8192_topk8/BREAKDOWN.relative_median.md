# dispatch_ffn_combine BREAKDOWN

- valid ranks: 16 [0, 10, 11, 12, 13, 14, 15, 1, 2, 3, 4, 5, 6, 7, 8, 9]
- profile version: 10
- timeline 聚合: relative_median
- prep skew (µs): median=1402 [1146, 1497]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 1146.0 | 1402.0 | 1497.0 | 0.0 | 1402.0 | [0, 0] |
| dispatch | 3689.0 | 3703.0 | 3734.0 | 1402.0 | 3703.0 | [1402, 1402] |
| swiglu | 11817.0 | 11951.0 | 12083.0 | 18980.5 | 11951.0 | [18813, 19381] |
| swiglu_w1 | 1912.0 | 1928.0 | 1939.0 | 19472.5 | 1928.0 | [19351, 19747] |
| swiglu_w2 | 1075.0 | 1084.0 | 1099.0 | 30384.5 | 1084.0 | [30169, 30556] |
| combine | 2133.0 | 6452.0 | 6655.0 | 32094.0 | 6452.0 | [31873, 32324] |
| unpermute | 1024.0 | 1034.0 | 1055.0 | 47694.0 | 1034.0 | [47693, 47695] |
| gmm1 | 28206.0 | 28389.5 | 28627.0 | 1401.0 | 28389.5 | [1285, 1889] |
| gmm2 | 13694.0 | 13989.0 | 14676.0 | 29706.5 | 13989.0 | [29457, 30055] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
