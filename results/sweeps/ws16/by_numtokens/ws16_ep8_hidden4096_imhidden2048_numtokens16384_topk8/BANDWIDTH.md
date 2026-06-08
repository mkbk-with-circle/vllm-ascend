# dispatch/combine 有效带宽

- hidden (K): 4096, imhidden: 2048, numtokens: 16384, topk: 8
- bytes/token dispatch: 4128, combine: 8192

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 8,657,043,456 | 4522.0 | 1914.43 |
| combine | 17,179,869,184 | 7244.0 | 2371.60 |

## Per-rank 带宽 (GB/s)

- dispatch: median=121.03, min=119.62, max=122.39
- combine: median=150.89, min=147.47, max=336.32
