# dispatch/combine 有效带宽

- hidden (K): 4096, imhidden: 2048, numtokens: 8192, topk: 8
- bytes/token dispatch: 4128, combine: 8192

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 2,164,260,864 | 3554.0 | 608.96 |
| combine | 4,294,967,296 | 5529.0 | 776.81 |

## Per-rank 带宽 (GB/s)

- dispatch: median=76.59, min=76.26, max=76.65
- combine: median=97.82, min=97.30, max=138.84
