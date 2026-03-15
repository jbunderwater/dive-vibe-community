#!/usr/bin/env bash
#
# validate_overnight.sh — Run all remaining validation batches sequentially
#
# Start this before you go to bed and it will work through all batches:
#
#   nohup ./scripts/validate_overnight.sh >> logs/validate.log 2>&1 &
#
# Or to start from a specific batch:
#
#   nohup ./scripts/validate_overnight.sh 3 >> logs/validate.log 2>&1 &
#
# Monitor progress:
#   tail -f logs/validate.log
#   ./scripts/validate_batch.sh status

set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_DIR"

mkdir -p logs

START_BATCH="${1:-$(cat logs/.validate_batch_state 2>/dev/null || echo 1)}"
TOTAL_BATCHES=9

echo "============================================"
echo "OVERNIGHT VALIDATION RUN"
echo "Starting at: $(date)"
echo "Starting from batch: $START_BATCH of $TOTAL_BATCHES"
echo "============================================"
echo ""

for i in $(seq "$START_BATCH" "$TOTAL_BATCHES"); do
  echo ""
  echo ">>> Batch $i starting at $(date)"
  echo ""

  if ./scripts/validate_batch.sh "$i"; then
    echo "$((i + 1))" > logs/.validate_batch_state
    echo ">>> Batch $i completed successfully at $(date)"
  else
    echo ">>> Batch $i FAILED at $(date). Continuing to next batch..."
    echo "$((i + 1))" > logs/.validate_batch_state
  fi

  # Push after each batch
  git push -u origin claude/dive-destinations-planning-5nbOI 2>/dev/null || true

  echo ""
  echo "--- Pausing 30s between batches ---"
  sleep 30
done

echo ""
echo "============================================"
echo "ALL BATCHES COMPLETE at $(date)"
echo "============================================"
./scripts/validate_batch.sh status
