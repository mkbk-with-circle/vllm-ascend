# dispatch/combine 有效带宽

- hidden (K): 4096, imhidden: 3072, numtokens: 8192, topk: 8
- bytes/token dispatch: 4128, combine: 8192

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 1,082,130,432 | 6840.0 | 158.21 |
| combine | 2,147,483,648 | 9793.0 | 219.29 |

## Per-rank 带宽 (GB/s)

- dispatch: median=39.61, min=39.48, max=39.90
- combine: median=80.56, min=54.79, max=106.49
