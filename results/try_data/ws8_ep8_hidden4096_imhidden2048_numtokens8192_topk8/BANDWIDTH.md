# dispatch/combine 有效带宽

- hidden (K): 4096, imhidden: 2048, numtokens: 8192, topk: 8
- bytes/token dispatch: 4128, combine: 8192

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 2,164,260,864 | 3129.0 | 691.68 |
| combine | 4,294,967,296 | 5457.0 | 787.06 |

## Per-rank 带宽 (GB/s)

- dispatch: median=87.04, min=86.01, max=87.69
- combine: median=99.56, min=98.14, max=140.55

## 警告

- 可能触及 max_output_size 截断: ranks [0, 1, 2, 3, 4, 5, 6, 7]
