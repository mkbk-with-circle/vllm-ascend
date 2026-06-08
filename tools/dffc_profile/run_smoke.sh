#!/usr/bin/env bash
# EP=8 smoke：无 profile 亦可验证算子可跑通
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "${SCRIPT_DIR}/source_env.sh"

cd "${DFFC_ROOT}"
export ASCEND_RT_VISIBLE_DEVICES="${ASCEND_RT_VISIBLE_DEVICES:-0,1,2,3,4,5,6,7}"

python "${SCRIPT_DIR}/run_case.py" --case S1 --world-size 8 "$@"
echo "[smoke] dispatch_ffn_combine EP=8 OK"
