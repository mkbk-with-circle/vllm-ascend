# dispatch/combine 有效带宽

- hidden (K): 4096, imhidden: 2048, numtokens: 1024, topk: 8
- bytes/token dispatch: 4128, combine: 8192

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 135,266,304 | 792.0 | 170.79 |
| combine | 268,435,456 | 1203.0 | 223.14 |

## Per-rank 带宽 (GB/s)

- dispatch: median=43.26, min=42.85, max=44.18
- combine: median=88.59, min=55.97, max=125.95
