# dispatch/combine 有效带宽

- hidden (K): 2048, imhidden: 1024, numtokens: 8192, topk: 8
- bytes/token dispatch: 2080, combine: 4096

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 1,090,519,040 | 3303.0 | 330.16 |
| combine | 2,147,483,648 | 4657.0 | 461.13 |

## Per-rank 带宽 (GB/s)

- dispatch: median=41.77, min=41.68, max=42.35
- combine: median=58.69, min=57.67, max=127.02
