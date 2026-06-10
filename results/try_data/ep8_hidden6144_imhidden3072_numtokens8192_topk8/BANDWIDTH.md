# dispatch/combine 有效带宽

- hidden (K): 6144, imhidden: 3072, numtokens: 8192, topk: 8
- bytes/token dispatch: 6176, combine: 12288

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 3,238,002,688 | 3586.0 | 902.96 |
| combine | 6,442,450,944 | 6367.0 | 1011.85 |

## Per-rank 带宽 (GB/s)

- dispatch: median=113.21, min=112.79, max=114.31
- combine: median=129.78, min=126.39, max=183.68

## 警告

- 可能触及 max_output_size 截断: ranks [0, 1, 2, 3, 4, 5, 6, 7]
