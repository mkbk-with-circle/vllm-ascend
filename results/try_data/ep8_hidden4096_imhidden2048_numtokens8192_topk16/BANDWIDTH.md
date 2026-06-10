# dispatch/combine 有效带宽

- hidden (K): 4096, imhidden: 2048, numtokens: 8192, topk: 16
- bytes/token dispatch: 4128, combine: 8192

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 4,328,521,728 | 6304.0 | 686.63 |
| combine | 8,589,934,592 | 11016.0 | 779.77 |

## Per-rank 带宽 (GB/s)

- dispatch: median=86.64, min=86.22, max=87.38
- combine: median=99.18, min=97.92, max=140.98

## 警告

- 可能触及 max_output_size 截断: ranks [0, 1, 2, 3, 4, 5, 6, 7]
