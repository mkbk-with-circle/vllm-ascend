#!/usr/bin/env bash
# 隔离 CANN/HCCL 环境，仅供 dffc_profile 子脚本 source
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
export DFFC_ROOT="${ROOT}"

# 优先 CANN 9.0，失败回退 8.5
if [[ -f /usr/local/Ascend/cann-9.0.0/set_env.sh ]]; then
  # shellcheck disable=SC1091
  source /usr/local/Ascend/cann-9.0.0/set_env.sh
elif [[ -f /usr/local/Ascend/cann-8.5.0/set_env.sh ]]; then
  # shellcheck disable=SC1091
  source /usr/local/Ascend/cann-8.5.0/set_env.sh
else
  echo "[dffc] 未找到 CANN set_env.sh" >&2
  exit 1
fi

export ASCEND_RT_VISIBLE_DEVICES="${ASCEND_RT_VISIBLE_DEVICES:-0,1,2,3,4,5,6,7}"

# 使用项目内 conda 环境（若存在）
if [[ -f "${ROOT}/.dffc_profile/miniconda3/etc/profile.d/conda.sh" ]]; then
  # shellcheck disable=SC1091
  source "${ROOT}/.dffc_profile/miniconda3/etc/profile.d/conda.sh"
  conda activate dffc 2>/dev/null || true
fi

export PYTHONPATH="${ROOT}:${PYTHONPATH:-}"
