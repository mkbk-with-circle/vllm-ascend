# Combine barrier stitch 审计

- 期望 profile version: **v11**
- `tail_gap = barrier_begin[e+1] - wall_end[e]`，pass 阈值 ≤ **2.0 µs**
- cases: 54，pass: **54**，fail: **0**，缺 barrier/错误: **0**

## 汇总表

| case | ws | ver | ranks | tail_med | tail_max | barrier_med | pass |
|------|----|----|-------|----------|----------|-------------|------|
| `ws16_ep8_hidden2048_imhidden1024_numtokens8192_t` | 16 | 11 | 16/16 | 1.0 | 1.0 | 231 | Y |
| `ws16_ep8_hidden4096_imhidden2048_numtokens8192_t` | 16 | 11 | 16/16 | 1.0 | 1.0 | 443 | Y |
| `ws16_ep8_hidden6144_imhidden3072_numtokens8192_t` | 16 | 11 | 16/16 | 1.0 | 1.0 | 1022 | Y |
| `ws16_ep8_hidden7168_imhidden3584_numtokens8192_t` | 16 | 11 | 16/16 | 0.0 | 1.0 | 1376 | Y |
| `ws16_ep8_hidden7680_imhidden3840_numtokens8192_t` | 16 | 11 | 16/16 | 1.0 | 1.0 | 1596 | Y |
| `ws16_ep8_hidden7936_imhidden3968_numtokens8192_t` | 16 | 11 | 16/16 | 1.0 | 1.0 | 1675 | Y |
| `ws16_ep8_hidden7968_imhidden3984_numtokens8192_t` | 16 | 11 | 16/16 | 1.0 | 1.0 | 1723 | Y |
| `ws16_ep8_hidden8000_imhidden4000_numtokens8192_t` | 16 | 11 | 16/16 | 1.0 | 1.0 | 1689 | Y |
| `ws16_ep8_hidden4096_imhidden1024_numtokens8192_t` | 16 | 11 | 16/16 | 1.0 | 1.0 | 351 | Y |
| `ws16_ep8_hidden4096_imhidden2048_numtokens8192_t` | 16 | 11 | 16/16 | 1.0 | 1.0 | 447 | Y |
| `ws16_ep8_hidden4096_imhidden3072_numtokens8192_t` | 16 | 11 | 16/16 | 1.0 | 1.0 | 594 | Y |
| `ws16_ep8_hidden4096_imhidden2048_numtokens1024_t` | 16 | 11 | 16/16 | 1.0 | 1.0 | 55 | Y |
| `ws16_ep8_hidden4096_imhidden2048_numtokens16384_` | 16 | 11 | 16/16 | 1.0 | 1.0 | 864 | Y |
| `ws16_ep8_hidden4096_imhidden2048_numtokens2048_t` | 16 | 11 | 16/16 | 0.5 | 1.0 | 112 | Y |
| `ws16_ep8_hidden4096_imhidden2048_numtokens4096_t` | 16 | 11 | 16/16 | 1.0 | 1.0 | 212 | Y |
| `ws16_ep8_hidden4096_imhidden2048_numtokens8192_t` | 16 | 11 | 16/16 | 1.0 | 1.0 | 435 | Y |
| `ws16_ep8_hidden4096_imhidden2048_numtokens8192_t` | 16 | 11 | 16/16 | 1.0 | 1.0 | 864 | Y |
| `ws16_ep8_hidden4096_imhidden2048_numtokens8192_t` | 16 | 11 | 16/16 | 1.0 | 1.0 | 216 | Y |
| `ws16_ep8_hidden4096_imhidden2048_numtokens8192_t` | 16 | 11 | 16/16 | 1.0 | 1.0 | 443 | Y |
| `ws4_ep8_hidden2048_imhidden1024_numtokens8192_to` | 4 | 11 | 4/4 | 0.5 | 1.0 | 669 | Y |
| `ws4_ep8_hidden4096_imhidden2048_numtokens8192_to` | 4 | 11 | 4/4 | 1.0 | 1.0 | 745 | Y |
| `ws4_ep8_hidden6144_imhidden3072_numtokens8192_to` | 4 | 11 | 4/4 | 1.0 | 1.0 | 948 | Y |
| `ws4_ep8_hidden7168_imhidden3584_numtokens8192_to` | 4 | 11 | 4/4 | 0.5 | 1.0 | 1422 | Y |
| `ws4_ep8_hidden7680_imhidden3840_numtokens8192_to` | 4 | 11 | 4/4 | 1.0 | 1.0 | 1589 | Y |
| `ws4_ep8_hidden7936_imhidden3968_numtokens8192_to` | 4 | 11 | 4/4 | 1.0 | 2.0 | 1718 | Y |
| `ws4_ep8_hidden7968_imhidden3984_numtokens8192_to` | 4 | 11 | 4/4 | 1.0 | 1.0 | 1684 | Y |
| `ws4_ep8_hidden8000_imhidden4000_numtokens8192_to` | 4 | 11 | 4/4 | 1.0 | 1.0 | 1667 | Y |
| `ws4_ep8_hidden4096_imhidden1024_numtokens8192_to` | 4 | 11 | 4/4 | 1.0 | 1.0 | 718 | Y |
| `ws4_ep8_hidden4096_imhidden2048_numtokens8192_to` | 4 | 11 | 4/4 | 1.0 | 1.0 | 745 | Y |
| `ws4_ep8_hidden4096_imhidden3072_numtokens8192_to` | 4 | 11 | 4/4 | 1.0 | 1.0 | 692 | Y |
| `ws4_ep8_hidden4096_imhidden2048_numtokens1024_to` | 4 | 11 | 4/4 | 1.0 | 1.0 | 102 | Y |
| `ws4_ep8_hidden4096_imhidden2048_numtokens16384_t` | 4 | 11 | 4/4 | 1.0 | 1.0 | 1342 | Y |
| `ws4_ep8_hidden4096_imhidden2048_numtokens2048_to` | 4 | 11 | 4/4 | 0.5 | 1.0 | 197 | Y |
| `ws4_ep8_hidden4096_imhidden2048_numtokens4096_to` | 4 | 11 | 4/4 | 0.5 | 1.0 | 345 | Y |
| `ws4_ep8_hidden4096_imhidden2048_numtokens8192_to` | 4 | 11 | 4/4 | 1.0 | 2.0 | 1396 | Y |
| `ws4_ep8_hidden4096_imhidden2048_numtokens8192_to` | 4 | 11 | 4/4 | 0.0 | 1.0 | 354 | Y |
| `ws4_ep8_hidden4096_imhidden2048_numtokens8192_to` | 4 | 11 | 4/4 | 1.0 | 1.0 | 741 | Y |
| `ws8_ep8_hidden2048_imhidden1024_numtokens8192_to` | 8 | 11 | 8/8 | 0.0 | 1.0 | 376 | Y |
| `ws8_ep8_hidden4096_imhidden2048_numtokens8192_to` | 8 | 11 | 8/8 | 1.0 | 1.0 | 475 | Y |
| `ws8_ep8_hidden6144_imhidden3072_numtokens8192_to` | 8 | 11 | 8/8 | 1.0 | 1.0 | 967 | Y |
| `ws8_ep8_hidden7168_imhidden3584_numtokens8192_to` | 8 | 11 | 8/8 | 1.0 | 1.0 | 1318 | Y |
| `ws8_ep8_hidden7680_imhidden3840_numtokens8192_to` | 8 | 11 | 8/8 | 0.5 | 1.0 | 1536 | Y |
| `ws8_ep8_hidden7936_imhidden3968_numtokens8192_to` | 8 | 11 | 8/8 | 1.0 | 1.0 | 1659 | Y |
| `ws8_ep8_hidden4096_imhidden1024_numtokens8192_to` | 8 | 11 | 8/8 | 0.0 | 1.0 | 454 | Y |
| `ws8_ep8_hidden4096_imhidden2048_numtokens8192_to` | 8 | 11 | 8/8 | 1.0 | 1.0 | 474 | Y |
| `ws8_ep8_hidden4096_imhidden3072_numtokens8192_to` | 8 | 11 | 8/8 | 0.0 | 1.0 | 550 | Y |
| `ws8_ep8_hidden4096_imhidden2048_numtokens1024_to` | 8 | 11 | 8/8 | 0.0 | 1.0 | 71 | Y |
| `ws8_ep8_hidden4096_imhidden2048_numtokens16384_t` | 8 | 11 | 8/8 | 1.0 | 1.0 | 743 | Y |
| `ws8_ep8_hidden4096_imhidden2048_numtokens2048_to` | 8 | 11 | 8/8 | 1.0 | 1.0 | 126 | Y |
| `ws8_ep8_hidden4096_imhidden2048_numtokens4096_to` | 8 | 11 | 8/8 | 0.0 | 1.0 | 215 | Y |
| `ws8_ep8_hidden4096_imhidden2048_numtokens8192_to` | 8 | 11 | 8/8 | 1.0 | 2.0 | 466 | Y |
| `ws8_ep8_hidden4096_imhidden2048_numtokens8192_to` | 8 | 11 | 8/8 | 1.0 | 1.0 | 749 | Y |
| `ws8_ep8_hidden4096_imhidden2048_numtokens8192_to` | 8 | 11 | 8/8 | 1.0 | 1.0 | 213 | Y |
| `ws8_ep8_hidden4096_imhidden2048_numtokens8192_to` | 8 | 11 | 8/8 | 0.5 | 1.0 | 418 | Y |

## 解读

- `tail_gap ≈ 0–1 µs`：writer 串行循环拼接正常，计时逻辑未在 expert 间造缝。
- `barrier_med`：expert 间真实等待（CrossCoreWait+SyncAll），与旧 timeline gap 同量级。
- `pass=N` 且 `ver<11`：需 `rerun_sweep_barrier_profile.py` 重跑 profile。
