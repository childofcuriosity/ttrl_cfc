#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <accuracy|format_only> <experiment-script> [extra Hydra overrides...]" >&2
  exit 2
fi

reward_mode=$1
experiment_script=$2
shift 2

case "$reward_mode" in
  accuracy|format_only) ;;
  *) echo "Unknown reward mode: $reward_mode" >&2; exit 2 ;;
esac

exec bash "$experiment_script" \
  "custom_reward_function.reward_kwargs.reward_mode=$reward_mode" \
  "$@"
