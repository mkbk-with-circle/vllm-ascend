# dispatch/combine 有效带宽

- hidden (K): 4096, imhidden: 1024, numtokens: 8192, topk: 8
- bytes/token dispatch: 4128, combine: 8192

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 1,082,130,432 | 6558.0 | 165.01 |
| combine | 2,147,483,648 | 9713.0 | 221.09 |

## Per-rank 带宽 (GB/s)

- dispatch: median=41.56, min=41.31, max=41.63
- combine: median=83.21, min=55.30, max=112.26
