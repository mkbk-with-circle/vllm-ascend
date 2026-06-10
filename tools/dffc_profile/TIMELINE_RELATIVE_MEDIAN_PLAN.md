# Timeline：relative_median 聚合规格

## 要点

**dispatch 锚定消除 prep skew → 相对偏移/时长取中位 → min/max 须保留 rank 离散度 → prep 单列 skew → 因果 repair 兜底 → 带宽不变、可回退。**

## 算法

1. 每 rank 以 `dispatch.begin` 为锚点，`offset = begin - anchor`。
2. 非 prep 阶段：`timeline_start = median(prep_dur) + median(offset)`，`timeline_dur = median(duration)`。
3. prep：`[0, median(prep_dur)]`，右端须 `[min,max]` prep 时长。
4. 须：每阶段 start `[offset_min, offset_max]`、end `[end_min, end_max]`（含 prep_lead）。
5. focus 版：dispatch=0，须同步平移；不画 prep。

## CLI

```bash
python3 tools/dffc_profile/regen_sweep_axis_timelines.py \
  --sweep-dir results/sweeps/by_hidden --timeline-aggregation relative_median

python3 tools/dffc_profile/regen_sweep_axis_timelines.py \
  --sweep-dir results/sweeps/by_hidden --restore rank0
```

## 备份

切换前自动备份为 `*.<当前aggregation>.*`（如 `breakdown.rank0.json`）。
