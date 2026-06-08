# dispatch_ffn_combine BREAKDOWN

- valid ranks: 8 [0, 1, 2, 3, 4, 5, 6, 7]
- profile version: 5
- timeline 起点: prep=0；AIC 阶段用 min(begin)/max(end) 墙钟

| phase | median dur (µs) | max dur (µs) | timeline start (µs) | timeline block (µs) |
|-------|-----------------|--------------|---------------------|---------------------|
| prep | 21413.0 | 45259.0 | 0.0 | 45259.0 |
| dispatch | 6240.0 | 6304.0 | 21413.0 | 6304.0 |
| swiglu | 3777.0 | 3798.0 | 29157.0 | 3798.0 |
| combine | 10805.5 | 11016.0 | 64328.0 | 11016.0 |
| gmm1 | 7914.5 | 7937.0 | 7109.0 | 52297.0 |
| gmm2 | 4923.0 | 4930.0 | 15046.0 | 49282.0 |
