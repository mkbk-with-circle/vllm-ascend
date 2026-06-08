# dispatch/combine 有效带宽

- hidden (K): 4096, imhidden: 2048, numtokens: 8192, topk: 4
- bytes/token dispatch: 4128, combine: 8192

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 1,082,130,432 | 1907.0 | 567.45 |
| combine | 2,147,483,648 | 2747.0 | 781.76 |

## Per-rank 带宽 (GB/s)

- dispatch: median=71.78, min=71.17, max=72.24
- combine: median=98.86, min=97.58, max=195.52
