# dispatch_ffn_combine BREAKDOWN

- valid ranks: 8 [0, 1, 2, 3, 4, 5, 6, 7]
- profile version: 7
- timeline 聚合: relative_median
- prep skew (µs): median=901 [624, 920]

| phase | min dur (>0) | median dur | max dur | timeline start | block | start whisker [min,max] |
|-------|--------------|------------|---------|----------------|-------|---------------------------|
| prep | 624.0 | 901.0 | 920.0 | 0.0 | 901.0 | [0, 0] |
| dispatch | 3506.0 | 3533.0 | 3551.0 | 901.0 | 3533.0 | [901, 901] |
| swiglu | 4344.0 | 4373.0 | 4424.0 | 6200.0 | 4373.0 | [6095, 6281] |
| swiglu_w1 | 992.0 | 1005.0 | 1009.0 | 6200.0 | 1005.0 | [6095, 6281] |
| swiglu_w2 | 897.0 | 904.5 | 916.0 | 9666.5 | 904.5 | [9551, 9763] |
| combine | 3857.0 | 5472.0 | 5526.0 | 15239.0 | 5472.0 | [15180, 15323] |
| gmm1 | 7175.0 | 7244.0 | 7303.0 | 2391.5 | 7244.0 | [2330, 2522] |
| gmm2 | 4435.0 | 4469.0 | 4506.0 | 10569.5 | 4469.0 | [10451, 10669] |

## 列说明

- **min dur (>0)**：8 个 rank 中 `duration_us ≥ 1` 的最小值（忽略零时长 rank）。
- **timeline start / block**：`relative_median` 聚合后的条块起点与宽度（median offset + median duration）。
- **start whisker [min,max]**：各 rank 该阶段**绝对起点**（prep=0 时间轴）的跨 rank 最小/最大值； 即 `prep_median + min/max(phase.begin − dispatch.begin)`。 反映 EP 间阶段启动时间的散布；timeline 图上对应条块左端的水平误差须。
- **prep** 的 start whisker 恒为 `[0,0]`（各 rank 已对齐到 prep=0）；prep 右端散布见上方 prep skew。
