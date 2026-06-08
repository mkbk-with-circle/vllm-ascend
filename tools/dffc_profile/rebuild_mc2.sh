#!/usr/bin/env bash
# 增量重编 dispatch_ffn_combine（可选 DISPATCH_FFN_COMBINE_PROFILE=1）
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "${SCRIPT_DIR}/source_env.sh"

export DISPATCH_FFN_COMBINE_PROFILE="${DISPATCH_FFN_COMBINE_PROFILE:-1}"
cd "${DFFC_ROOT}"

export VLLM_ASCEND_TARGET_DEVICE="ascend910b"
pip install -e .
python -c "import vllm_ascend; print('vllm_ascend import OK')"
echo "[rebuild] DISPATCH_FFN_COMBINE_PROFILE=${DISPATCH_FFN_COMBINE_PROFILE}"
