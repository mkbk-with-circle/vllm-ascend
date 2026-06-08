# Profile constraint audit

- cases: 61
- fail: 4
- pass: 57

## [PASS] ws4_ep4_hidden2048_imhidden1024_numtokens8192_topk8 (e=8, v10, combine_v1=True)

## [PASS] ws4_ep4_hidden4096_imhidden2048_numtokens8192_topk8 (e=8, v10, combine_v1=True)

## [PASS] ws4_ep4_hidden6144_imhidden3072_numtokens8192_topk8 (e=8, v10, combine_v1=True)
### WARN
- prep cross-rank dur ratio 1.46 (min=686 max=1004) > 1.35
- gmm1 cross-rank dur ratio 1.47 (min=16206 max=23775) > 1.35
- gmm2 cross-rank dur ratio 1.71 (min=11591 max=19808) > 1.35

## [PASS] ws4_ep4_hidden7168_imhidden3584_numtokens8192_topk8 (e=8, v10, combine_v1=True)
### WARN
- prep cross-rank dur ratio 1.41 (min=933 max=1312) > 1.35

## [PASS] ws4_ep4_hidden7680_imhidden3840_numtokens8192_topk8 (e=8, v10, combine_v1=True)
### WARN
- gmm2 cross-rank dur ratio 1.79 (min=14742 max=26444) > 1.35

## [PASS] ws4_ep4_hidden7936_imhidden3968_numtokens8192_topk8 (e=8, v10, combine_v1=True)
### WARN
- prep cross-rank dur ratio 1.51 (min=790 max=1189) > 1.35

## [PASS] ws4_ep4_hidden7968_imhidden3984_numtokens8192_topk8 (e=8, v10, combine_v1=True)
### WARN
- gmm2 cross-rank dur ratio 1.81 (min=15465 max=27931) > 1.35

## [PASS] ws4_ep4_hidden8000_imhidden4000_numtokens8192_topk8 (e=8, v10, combine_v1=True)

## [PASS] ws4_ep4_hidden4096_imhidden1024_numtokens8192_topk8 (e=8, v10, combine_v1=True)

## [PASS] ws4_ep4_hidden4096_imhidden2048_numtokens8192_topk8 (e=8, v10, combine_v1=True)

## [PASS] ws4_ep4_hidden4096_imhidden3072_numtokens8192_topk8 (e=8, v10, combine_v1=True)
### WARN
- gmm1 cross-rank dur ratio 1.37 (min=11096 max=15148) > 1.35
- gmm2 cross-rank dur ratio 1.69 (min=7410 max=12529) > 1.35

## [PASS] ws4_ep4_hidden4096_imhidden2048_numtokens1024_topk8 (e=8, v10, combine_v1=True)
### WARN
- combine cross-rank dur ratio 2.29 (min=526 max=1203) > 2.25

## [PASS] ws4_ep4_hidden4096_imhidden2048_numtokens16384_topk8 (e=8, v10, combine_v1=True)

## [PASS] ws4_ep4_hidden4096_imhidden2048_numtokens2048_topk8 (e=8, v10, combine_v1=True)

## [PASS] ws4_ep4_hidden4096_imhidden2048_numtokens4096_topk8 (e=8, v10, combine_v1=True)

## [PASS] ws4_ep4_hidden4096_imhidden2048_numtokens8192_topk8 (e=8, v10, combine_v1=True)
### WARN
- prep cross-rank dur ratio 1.38 (min=593 max=818) > 1.35
- gmm1 cross-rank dur ratio 1.48 (min=7283 max=10751) > 1.35
- gmm2 cross-rank dur ratio 1.85 (min=5113 max=9450) > 1.35

## [PASS] ws4_ep4_hidden4096_imhidden2048_numtokens8192_topk16 (e=8, v10, combine_v1=True)
### WARN
- prep cross-rank dur ratio 1.41 (min=944 max=1327) > 1.35

## [PASS] ws4_ep4_hidden4096_imhidden2048_numtokens8192_topk4 (e=8, v10, combine_v1=True)

## [PASS] ws4_ep4_hidden4096_imhidden2048_numtokens8192_topk8 (e=8, v10, combine_v1=True)
### WARN
- gmm1 cross-rank dur ratio 1.46 (min=7329 max=10718) > 1.35
- gmm2 cross-rank dur ratio 1.62 (min=5137 max=8320) > 1.35

## [PASS] ws8_ep8_hidden2048_imhidden1024_numtokens8192_topk8 (e=8, v10, combine_v1=True)

## [PASS] ws8_ep8_hidden4096_imhidden2048_numtokens8192_topk8 (e=8, v10, combine_v1=True)
### WARN
- gmm2 cross-rank dur ratio 1.37 (min=4253 max=5833) > 1.35

## [FAIL] ws8_ep8_hidden6144_imhidden3072_numtokens32768_topk8 (e=2, v8, combine_v1=True)
### FAIL
- profile version=8 < 10

## [FAIL] ws8_ep8_hidden6144_imhidden3072_numtokens49152_topk8 (e=2, v8, combine_v1=True)
### FAIL
- profile version=8 < 10

## [FAIL] ws8_ep8_hidden6144_imhidden3072_numtokens65536_topk8 (e=2, v8, combine_v1=True)
### FAIL
- profile version=8 < 10

## [PASS] ws8_ep8_hidden6144_imhidden3072_numtokens8192_topk8 (e=8, v10, combine_v1=True)
### WARN
- gmm2 cross-rank dur ratio 1.37 (min=8843 max=12076) > 1.35

## [PASS] ws8_ep8_hidden7168_imhidden3584_numtokens8192_topk8 (e=8, v10, combine_v1=True)
### WARN
- prep cross-rank dur ratio 1.43 (min=948 max=1351) > 1.35
- gmm2 cross-rank dur ratio 1.55 (min=11595 max=17997) > 1.35

## [PASS] ws8_ep8_hidden7680_imhidden3840_numtokens8192_topk8 (e=8, v10, combine_v1=True)
### WARN
- prep cross-rank dur ratio 1.48 (min=1267 max=1872) > 1.35
- rank2: gmm1.begin (1482) < dispatch.begin (1873)
- rank3: gmm1.begin (1412) < dispatch.begin (1726)
- rank7: gmm1.begin (1276) < dispatch.begin (1532)

## [PASS] ws8_ep8_hidden7936_imhidden3968_numtokens8192_topk8 (e=8, v10, combine_v1=True)
### WARN
- prep cross-rank dur ratio 1.48 (min=1076 max=1591) > 1.35
- gmm2 cross-rank dur ratio 1.47 (min=14056 max=20613) > 1.35

## [PASS] ws8_ep8_hidden7968_imhidden3984_numtokens8192_topk8 (e=8, v10, combine_v1=True)
### WARN
- gmm2 cross-rank dur ratio 1.39 (min=13863 max=19211) > 1.35

## [PASS] ws8_ep8_hidden8000_imhidden4000_numtokens8192_topk8 (e=8, v10, combine_v1=True)
### WARN
- prep cross-rank dur ratio 1.68 (min=952 max=1595) > 1.35

## [FAIL] ws8_ep8_hidden8032_imhidden4016_numtokens8192_topk8 (e=2, v8, combine_v1=True)
### FAIL
- profile version=8 < 10

## [PASS] ws8_ep8_hidden4096_imhidden1024_numtokens8192_topk8 (e=8, v10, combine_v1=True)
### WARN
- gmm2 cross-rank dur ratio 1.51 (min=2869 max=4332) > 1.35

## [PASS] ws8_ep8_hidden4096_imhidden2048_numtokens8192_topk8 (e=8, v10, combine_v1=True)
### WARN
- gmm2 cross-rank dur ratio 1.35 (min=4292 max=5805) > 1.35

## [PASS] ws8_ep8_hidden4096_imhidden3072_numtokens8192_topk8 (e=8, v10, combine_v1=True)
### WARN
- gmm2 cross-rank dur ratio 1.47 (min=5963 max=8768) > 1.35

## [PASS] ws8_ep8_hidden4096_imhidden2048_numtokens1024_topk8 (e=8, v10, combine_v1=True)
### WARN
- prep cross-rank dur ratio 1.43 (min=125 max=179) > 1.35
- combine cross-rank dur ratio 2.37 (min=290 max=688) > 2.25

## [PASS] ws8_ep8_hidden4096_imhidden2048_numtokens16384_topk8 (e=8, v10, combine_v1=True)
### WARN
- gmm2 cross-rank dur ratio 1.58 (min=8200 max=12917) > 1.35

## [PASS] ws8_ep8_hidden4096_imhidden2048_numtokens2048_topk8 (e=8, v10, combine_v1=True)
### WARN
- prep cross-rank dur ratio 1.44 (min=200 max=287) > 1.35

## [PASS] ws8_ep8_hidden4096_imhidden2048_numtokens4096_topk8 (e=8, v10, combine_v1=True)

## [PASS] ws8_ep8_hidden4096_imhidden2048_numtokens8192_topk8 (e=8, v10, combine_v1=True)
### WARN
- gmm2 cross-rank dur ratio 1.63 (min=4167 max=6804) > 1.35

## [PASS] ws8_ep8_hidden4096_imhidden2048_numtokens8192_topk16 (e=8, v10, combine_v1=True)
### WARN
- prep cross-rank dur ratio 1.57 (min=1023 max=1604) > 1.35
- gmm2 cross-rank dur ratio 1.59 (min=8214 max=13080) > 1.35

## [PASS] ws8_ep8_hidden4096_imhidden2048_numtokens8192_topk4 (e=8, v10, combine_v1=True)
### WARN
- gmm2 cross-rank dur ratio 1.53 (min=2093 max=3200) > 1.35

## [PASS] ws8_ep8_hidden4096_imhidden2048_numtokens8192_topk8 (e=8, v10, combine_v1=True)
### WARN
- gmm2 cross-rank dur ratio 1.60 (min=4195 max=6729) > 1.35

## [PASS] ws16_ep16_hidden2048_imhidden1024_numtokens8192_topk8 (e=8, v10, combine_v1=True)
### WARN
- prep cross-rank dur ratio 1.35 (min=754 max=1021) > 1.35
- combine cross-rank dur ratio 2.29 (min=1153 max=2640) > 2.25

## [PASS] ws16_ep16_hidden4096_imhidden2048_numtokens8192_topk8 (e=8, v10, combine_v1=True)
### WARN
- combine cross-rank dur ratio 2.68 (min=1387 max=3720) > 2.25

## [PASS] ws16_ep16_hidden6144_imhidden3072_numtokens8192_topk8 (e=8, v10, combine_v1=True)
### WARN
- prep cross-rank dur ratio 1.68 (min=985 max=1658) > 1.35
- combine cross-rank dur ratio 2.99 (min=1766 max=5272) > 2.25
- rank0: gmm1.begin (1224) < dispatch.begin (1659)
- rank10: gmm1.begin (1088) < dispatch.begin (1559)
- rank11: gmm1.begin (1184) < dispatch.begin (1494)
- rank12: gmm1.begin (1175) < dispatch.begin (1467)
- rank13: gmm1.begin (1202) < dispatch.begin (1585)
- rank14: gmm1.begin (1133) < dispatch.begin (1591)
- rank15: gmm1.begin (1224) < dispatch.begin (1603)
- rank1: gmm1.begin (1200) < dispatch.begin (1602)
- rank2: gmm1.begin (1127) < dispatch.begin (1566)
- rank3: gmm1.begin (1160) < dispatch.begin (1488)
- ... +5 more

## [PASS] ws16_ep16_hidden7168_imhidden3584_numtokens8192_topk8 (e=8, v10, combine_v1=True)
### WARN
- prep cross-rank dur ratio 1.40 (min=1340 max=1878) > 1.35
- combine cross-rank dur ratio 3.04 (min=1995 max=6074) > 2.25
- rank0: gmm1.begin (1392) < dispatch.begin (1824)
- rank10: gmm1.begin (1327) < dispatch.begin (1655)
- rank12: gmm1.begin (1318) < dispatch.begin (1534)
- rank13: gmm1.begin (1362) < dispatch.begin (1589)
- rank14: gmm1.begin (1184) < dispatch.begin (1569)
- rank15: gmm1.begin (1294) < dispatch.begin (1790)
- rank1: gmm1.begin (1314) < dispatch.begin (1717)
- rank2: gmm1.begin (1306) < dispatch.begin (1720)
- rank3: gmm1.begin (1154) < dispatch.begin (1579)
- rank4: gmm1.begin (1293) < dispatch.begin (1607)
- ... +5 more

## [PASS] ws16_ep16_hidden7680_imhidden3840_numtokens8192_topk8 (e=8, v10, combine_v1=True)
### WARN
- combine cross-rank dur ratio 3.12 (min=2133 max=6655) > 2.25

## [PASS] ws16_ep16_hidden7936_imhidden3968_numtokens8192_topk8 (e=8, v10, combine_v1=True)
### WARN
- prep cross-rank dur ratio 1.43 (min=1164 max=1659) > 1.35
- combine cross-rank dur ratio 3.14 (min=2150 max=6758) > 2.25
- gmm2 cross-rank dur ratio 1.63 (min=14292 max=23268) > 1.35
- rank10: gmm1.begin (1316) < dispatch.begin (1601)
- rank2: gmm1.begin (1267) < dispatch.begin (1548)

## [PASS] ws16_ep16_hidden7968_imhidden3984_numtokens8192_topk8 (e=8, v10, combine_v1=True)
### WARN
- prep cross-rank dur ratio 1.39 (min=1100 max=1533) > 1.35
- combine cross-rank dur ratio 3.10 (min=2211 max=6860) > 2.25

## [PASS] ws16_ep16_hidden8000_imhidden4000_numtokens8192_topk8 (e=8, v10, combine_v1=True)
### WARN
- prep cross-rank dur ratio 1.39 (min=1045 max=1450) > 1.35
- combine cross-rank dur ratio 3.08 (min=2196 max=6755) > 2.25

## [PASS] ws16_ep16_hidden4096_imhidden1024_numtokens8192_topk8 (e=8, v10, combine_v1=True)
### WARN
- combine cross-rank dur ratio 2.55 (min=1477 max=3759) > 2.25

## [PASS] ws16_ep16_hidden4096_imhidden2048_numtokens8192_topk8 (e=8, v10, combine_v1=True)
### WARN
- prep cross-rank dur ratio 1.37 (min=863 max=1186) > 1.35
- combine cross-rank dur ratio 2.68 (min=1388 max=3717) > 2.25
- rank0: gmm1.begin (959) < dispatch.begin (1163)
- rank11: gmm1.begin (887) < dispatch.begin (1161)
- rank14: gmm1.begin (856) < dispatch.begin (1142)
- rank15: gmm1.begin (828) < dispatch.begin (1134)
- rank1: gmm1.begin (895) < dispatch.begin (1184)
- rank2: gmm1.begin (903) < dispatch.begin (1159)
- rank3: gmm1.begin (910) < dispatch.begin (1174)
- rank4: gmm1.begin (861) < dispatch.begin (1095)
- rank5: gmm1.begin (865) < dispatch.begin (1178)
- rank6: gmm1.begin (893) < dispatch.begin (1151)
- ... +2 more

## [PASS] ws16_ep16_hidden4096_imhidden3072_numtokens8192_topk8 (e=8, v10, combine_v1=True)
### WARN
- combine cross-rank dur ratio 2.84 (min=1309 max=3714) > 2.25

## [PASS] ws16_ep16_hidden4096_imhidden2048_numtokens1024_topk8 (e=8, v10, combine_v1=True)
### WARN
- combine cross-rank dur ratio 2.66 (min=170 max=452) > 2.25

## [PASS] ws16_ep16_hidden4096_imhidden2048_numtokens16384_topk8 (e=8, v10, combine_v1=True)
### WARN
- combine cross-rank dur ratio 2.26 (min=3209 max=7244) > 2.25

## [PASS] ws16_ep16_hidden4096_imhidden2048_numtokens2048_topk8 (e=8, v10, combine_v1=True)
### WARN
- prep cross-rank dur ratio 1.82 (min=374 max=679) > 1.35
- combine cross-rank dur ratio 2.83 (min=321 max=908) > 2.25
- rank10: combine.begin (2755) < swiglu.begin (3925)
- rank11: combine.begin (2700) < swiglu.begin (3922)
- rank12: combine.begin (2706) < swiglu.begin (3897)
- rank13: combine.begin (2657) < swiglu.begin (3865)
- rank14: combine.begin (2705) < swiglu.begin (3877)
- rank15: combine.begin (2737) < swiglu.begin (3931)
- rank1: combine.begin (2701) < swiglu.begin (3903)
- rank2: combine.begin (2781) < swiglu.begin (3945)
- rank3: combine.begin (2471) < swiglu.begin (3882)
- rank4: combine.begin (2695) < swiglu.begin (3896)
- ... +5 more

## [PASS] ws16_ep16_hidden4096_imhidden2048_numtokens4096_topk8 (e=8, v10, combine_v1=True)
### WARN
- combine cross-rank dur ratio 2.68 (min=700 max=1876) > 2.25

## [PASS] ws16_ep16_hidden4096_imhidden2048_numtokens8192_topk8 (e=8, v10, combine_v1=True)
### WARN
- prep cross-rank dur ratio 1.36 (min=633 max=862) > 1.35
- combine cross-rank dur ratio 2.67 (min=1390 max=3707) > 2.25

## [PASS] ws16_ep16_hidden4096_imhidden2048_numtokens8192_topk16 (e=8, v10, combine_v1=True)
### WARN
- combine cross-rank dur ratio 2.26 (min=3249 max=7327) > 2.25

## [PASS] ws16_ep16_hidden4096_imhidden2048_numtokens8192_topk4 (e=8, v10, combine_v1=True)
### WARN
- combine cross-rank dur ratio 2.60 (min=709 max=1840) > 2.25

## [PASS] ws16_ep16_hidden4096_imhidden2048_numtokens8192_topk8 (e=8, v10, combine_v1=True)
### WARN
- prep cross-rank dur ratio 1.43 (min=837 max=1193) > 1.35
- combine cross-rank dur ratio 2.67 (min=1393 max=3713) > 2.25
- rank11: gmm1.begin (811) < dispatch.begin (1054)
