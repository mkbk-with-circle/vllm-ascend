# dispatch/combine 有效带宽

- hidden (K): 4096, imhidden: 2048, numtokens: 2048, topk: 8
- bytes/token dispatch: 4128, combine: 8192

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 270,532,608 | 1714.0 | 157.84 |
| combine | 536,870,912 | 2435.0 | 220.48 |

## Per-rank 带宽 (GB/s)

- dispatch: median=39.71, min=39.58, max=40.25
- combine: median=82.53, min=55.18, max=111.15
