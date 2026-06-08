#!/usr/bin/env bash
# 串行跑 S1–S4，每 case 生成 timeline + BREAKDOWN
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "${SCRIPT_DIR}/source_env.sh"

cd "${DFFC_ROOT}"
CASES=(S1 S2 S3 S4)

for c in "${CASES[@]}"; do
  echo "======== case ${c} ========"
  OUT="${DFFC_ROOT}/.dffc_profile/prof_dffc/${c}"
  python "${SCRIPT_DIR}/run_case.py" --case "${c}" --out-dir "${OUT}"
  python "${SCRIPT_DIR}/parse_profile.py" --indir "${OUT}"
  python "${SCRIPT_DIR}/gen_timeline.py" \
    --breakdown "${OUT}/breakdown.json" \
    --out "${OUT}/timeline.png" \
    --title "dispatch_ffn_combine ${c} (EP=8)"
done
echo "[sweep] done -> .dffc_profile/prof_dffc/"
