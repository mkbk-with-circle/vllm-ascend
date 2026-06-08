# dispatch/combine 有效带宽

- hidden (K): 4096, imhidden: 2048, numtokens: 8192, topk: 16
- bytes/token dispatch: 4128, combine: 8192

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 8,657,043,456 | 4531.0 | 1910.63 |
| combine | 17,179,869,184 | 7327.0 | 2344.73 |

## Per-rank 带宽 (GB/s)

- dispatch: median=120.95, min=119.78, max=122.28
- combine: median=152.04, min=146.22, max=331.90
