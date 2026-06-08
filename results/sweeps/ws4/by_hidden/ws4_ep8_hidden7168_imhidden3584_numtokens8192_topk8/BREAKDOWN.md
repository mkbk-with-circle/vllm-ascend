# dispatch_ffn_combine BREAKDOWN

- valid ranks: 4 [0, 1, 2, 3]
- profile version: 10
- timeline 聚合: relative_median
- prep skew (µs): median=1051 [933, 1312]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 933.0 | 1051.0 | 1312.0 | 0.0 | 1051.0 | [0, 0] |
| dispatch | 7424.0 | 7442.0 | 7463.0 | 1051.0 | 7442.0 | [1051, 1051] |
| swiglu | 12113.0 | 12235.0 | 12403.0 | 22495.5 | 12235.0 | [22422, 22692] |
| swiglu_w1 | 1823.0 | 1829.5 | 1836.0 | 22495.5 | 1829.5 | [22422, 22692] |
| swiglu_w2 | 1041.0 | 1043.5 | 1049.0 | 33764.5 | 1043.5 | [33541, 33844] |
| combine | 6094.0 | 9011.5 | 11922.0 | 35644.0 | 9011.5 | [35473, 35835] |
| unpermute | 935.0 | 938.0 | 973.0 | 52019.5 | 938.0 | [51895, 52175] |
| gmm1 | 24937.0 | 25095.5 | 25352.0 | 1626.5 | 25095.5 | [1508, 1767] |
| gmm2 | 13367.0 | 13608.0 | 13851.0 | 26696.0 | 13608.0 | [26519, 26768] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
