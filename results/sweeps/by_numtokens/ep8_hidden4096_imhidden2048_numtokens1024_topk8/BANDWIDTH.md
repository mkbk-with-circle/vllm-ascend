# dispatch/combine 有效带宽

- hidden (K): 4096, imhidden: 2048, numtokens: 1024, topk: 8
- bytes/token dispatch: 4128, combine: 8192

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 270,532,608 | 410.0 | 659.84 |
| combine | 536,870,912 | 704.0 | 762.60 |

## Per-rank 带宽 (GB/s)

- dispatch: median=84.57, min=82.50, max=86.48
- combine: median=97.19, min=94.79, max=144.84
