#!/usr/bin/env bash
# Run the Smart Format eval against a real LLM and print pass/fail + latency per case.
#
#   EVAL_MODEL=qwen2.5:1.5b scripts/eval-smart-format.sh                      # local Ollama (default)
#   EVAL_PROVIDER=apple_intelligence EVAL_MODEL=0 scripts/eval-smart-format.sh
#   EVAL_PROVIDER=groq EVAL_MODEL=llama-3.1-8b-instant EVAL_API_KEY=... scripts/eval-smart-format.sh
#
# Cases live in src-tauri/eval/smart_format_cases.json.
set -euo pipefail
cd "$(dirname "$0")/../src-tauri"
: "${EVAL_MODEL:?set EVAL_MODEL}"
export EVAL_PROVIDER="${EVAL_PROVIDER:-custom}"
# Without EVAL_API_KEY, reuse the key saved in Handy Personal's settings for this
# provider, so keys never need to be pasted into a terminal or chat.
if [[ -z "${EVAL_API_KEY:-}" ]]; then
  store="$HOME/Library/Application Support/com.kuda.handy/settings_store.json"
  if [[ -f "$store" ]]; then
    EVAL_API_KEY="$(python3 -c 'import json,sys; s=json.load(open(sys.argv[1])); s=s.get("settings", s); print((s.get("post_process_api_keys") or {}).get(sys.argv[2], ""))' "$store" "$EVAL_PROVIDER")"
    export EVAL_API_KEY
  fi
fi
export CMAKE_POLICY_VERSION_MINIMUM=3.5
exec cargo test --lib smart_format_eval -- --ignored --nocapture --test-threads=1
