#!/usr/bin/env bash
# 从 offline-a3-bundle 本地 wheel 安装 torch/torch-npu 及常用依赖（无外网）
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "${SCRIPT_DIR}/source_env.sh"

# 需要 Python 3.11 + dffc311（与 offline wheel cp311 对齐）
if ! python -c 'import sys; assert sys.version_info[:2]==(3,11)' 2>/dev/null; then
  echo "[install_offline] 请先: conda create -y -n dffc311 python=3.11 && conda activate dffc311" >&2
  exit 1
fi

W="${DFFC_WHEELS_DIR}"
WE="${DFFC_WHEELS_EXTRA}"
if [[ ! -d "${W}" ]]; then
  echo "[install_offline] 未找到 ${W}" >&2
  exit 1
fi

pip install --no-index -f "${W}" -f "${WE}" \
  "${W}/torch-2.10.0+cpu-cp311-cp311-manylinux_2_28_aarch64.whl" \
  "${W}/torch_npu-2.10.0-cp311-cp311-manylinux_2_28_aarch64.whl" \
  "${W}/numpy-1.26.4-cp311-cp311-manylinux_2_17_aarch64.manylinux2014_aarch64.whl" \
  pyyaml decorator packaging pybind11 einops scipy psutil setuptools wheel attrs

echo "[install_offline] torch/torch-npu 已从本地 wheel 安装"
