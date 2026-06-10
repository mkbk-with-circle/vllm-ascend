# dispatch/combine 有效带宽

- hidden (K): 4096, imhidden: 2048, numtokens: 8192, topk: 4
- bytes/token dispatch: 4128, combine: 8192

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 1,082,130,432 | 1791.0 | 604.20 |
| combine | 2,147,483,648 | 2797.0 | 767.78 |

## Per-rank 带宽 (GB/s)

- dispatch: median=76.69, min=76.35, max=76.86
- combine: median=98.22, min=95.99, max=134.38
