# dispatch/combine 有效带宽

- hidden (K): 6144, imhidden: 3072, numtokens: 65536, topk: 8
- bytes/token dispatch: 6176, combine: 12288

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 25,904,021,504 | 31590.0 | 820.01 |
| combine | 51,539,607,552 | 50562.0 | 1019.33 |

## Per-rank 带宽 (GB/s)

- dispatch: median=102.97, min=102.45, max=103.43
- combine: median=129.09, min=127.46, max=175.17
