#!/usr/bin/env bash
#
# validate_batch.sh — Run /validate-sites on a batch of destinations via Claude Code CLI
#
# Usage:
#   ./scripts/validate_batch.sh <batch_number>
#   ./scripts/validate_batch.sh all        # Run all batches sequentially
#   ./scripts/validate_batch.sh status     # Show validation progress
#
# Batches are ordered by priority:
#   Batch 1: Specialty sites (wrecks, muck, pelagic) — highest misclassification risk
#   Batch 2: Caribbean — popular destinations, many need wall/drift corrections
#   Batch 3: Southeast Asia — large region, heavy reef-default bias
#   Batch 4: Pacific — remote destinations, pelagic/pinnacle corrections
#   Batch 5: Europe & Middle East — wrecks, walls, cold water
#   Batch 6: Africa & Indian Ocean — mixed types
#   Batch 7: North America (East) — wrecks, cold water
#   Batch 8: North America (West) & Central America — kelp, walls, varied
#
# Each batch processes ~12-15 destinations. Estimated time: 30-60 min per batch.
#
# Schedule overnight with cron:
#   crontab -e
#   1 0 * * * cd /home/user/dive-vibe-community && ./scripts/validate_batch.sh next >> logs/validate.log 2>&1

set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_DIR"

LOG_DIR="$REPO_DIR/logs"
mkdir -p "$LOG_DIR"

BATCH_STATE_FILE="$LOG_DIR/.validate_batch_state"
LOG_FILE="$LOG_DIR/validate_$(date +%Y%m%d_%H%M%S).log"

# Define batches — destinations grouped by priority and region
declare -a BATCH_1=(
  chuuk-lagoon silfra-fissure lembeh-strait galapagos-islands socorro-islands
  cocos-island manado-bunaken california-channel-islands newfoundland
  great-lakes new-jersey north-carolina bermuda
)

declare -a BATCH_2=(
  bahamas cayman-islands turks-and-caicos cozumel british-virgin-islands
  utila roatan grenada dominica st-lucia us-virgin-islands tobago aruba
)

declare -a BATCH_3=(
  guadeloupe barbados dominican-republic puerto-rico jamaica
  martinique st-kitts-and-nevis st-vincent-grenadines sint-eustatius
  antigua-and-barbuda providencia-island bocas-del-toro
)

declare -a BATCH_4=(
  raja-ampat sipadan komodo-national-park thailand-similan-islands
  bali gili-islands koh-tao philippines-palawan philippines-tubbataha-reefs
  philippines-donsol philippines-anilao philippines-malapascua
)

declare -a BATCH_5=(
  palau fiji french-polynesia papua-new-guinea solomon-islands
  vanuatu tonga micronesia-yap marshall-islands okinawa
  andaman-islands sri-lanka lombok alor-archipelago ambon triton-bay
)

declare -a BATCH_6=(
  malta-and-gozo sardinia croatia greece turkey norway-lofoten-islands
  azores port-cros ustica svalbard greenland
  red-sea jordan-aqaba oman uae-fujairah
)

declare -a BATCH_7=(
  mozambique tanzania south-africa madagascar zanzibar
  kenya-coast cape-town djibouti seychelles mauritius
  maldives christmas-island ningaloo-reef
)

declare -a BATCH_8=(
  florida-keys dry-tortugas south-florida flower-garden-banks
  new-england nova-scotia great-barrier-reef lord-howe-island
  south-australia-neptune-islands poor-knights-islands
  alaska puget-sound
)

declare -a BATCH_9=(
  monterey-bay san-diego-la-jolla vancouver-island british-columbia
  la-paz-sea-of-cortez hawaii-big-island hawaii-oahu hawaii-kauai
  hawaii-maui coiba-national-park curacao bonaire
  sudan-red-sea
)

get_batch() {
  local batch_num=$1
  local -n batch_ref="BATCH_${batch_num}"
  echo "${batch_ref[@]}"
}

get_total_batches() {
  echo 9
}

get_current_batch() {
  if [[ -f "$BATCH_STATE_FILE" ]]; then
    cat "$BATCH_STATE_FILE"
  else
    echo 1
  fi
}

set_current_batch() {
  echo "$1" > "$BATCH_STATE_FILE"
}

filter_unvalidated() {
  local slugs=("$@")
  local unvalidated=()
  for slug in "${slugs[@]}"; do
    local json_file="data/osm_clean/${slug}.json"
    if [[ ! -f "$json_file" ]]; then
      continue
    fi
    local total validated
    total=$(python3 -c "import json; print(len(json.load(open('$json_file'))))" 2>/dev/null || echo 0)
    validated=$(python3 -c "import json; print(sum(1 for s in json.load(open('$json_file')) if s.get('tags',{}).get('validated')=='true'))" 2>/dev/null || echo 0)
    if [[ "$validated" -lt "$total" ]]; then
      unvalidated+=("$slug")
    fi
  done
  echo "${unvalidated[@]}"
}

show_status() {
  echo "=== VALIDATION PROGRESS ==="
  echo ""
  local total_batches
  total_batches=$(get_total_batches)
  local current
  current=$(get_current_batch)

  for i in $(seq 1 "$total_batches"); do
    local slugs
    slugs=($(get_batch "$i"))
    local done_count=0
    local total_count=${#slugs[@]}

    for slug in "${slugs[@]}"; do
      local json_file="data/osm_clean/${slug}.json"
      if [[ -f "$json_file" ]]; then
        local total validated
        total=$(python3 -c "import json; print(len(json.load(open('$json_file'))))" 2>/dev/null || echo 0)
        validated=$(python3 -c "import json; print(sum(1 for s in json.load(open('$json_file')) if s.get('tags',{}).get('validated')=='true'))" 2>/dev/null || echo 0)
        if [[ "$validated" -ge "$total" && "$total" -gt 0 ]]; then
          ((done_count++))
        fi
      fi
    done

    local status_marker=""
    if [[ "$done_count" -eq "$total_count" ]]; then
      status_marker="[DONE]"
    elif [[ "$i" -eq "$current" ]]; then
      status_marker="[NEXT]"
    else
      status_marker="[    ]"
    fi

    echo "  Batch $i: $status_marker $done_count/$total_count destinations validated"
  done

  echo ""
  echo "Next batch to run: $current"
  echo "Run: ./scripts/validate_batch.sh next"
}

run_batch() {
  local batch_num=$1
  local slugs
  slugs=($(get_batch "$batch_num"))

  # Filter to only unvalidated destinations
  local unvalidated
  unvalidated=($(filter_unvalidated "${slugs[@]}"))

  if [[ ${#unvalidated[@]} -eq 0 ]]; then
    echo "Batch $batch_num: All destinations already validated. Skipping."
    return 0
  fi

  local slug_list="${unvalidated[*]}"
  echo "=== BATCH $batch_num: Validating ${#unvalidated[@]} destinations ==="
  echo "Destinations: $slug_list"
  echo "Start time: $(date)"
  echo ""

  # Run Claude Code with the validate-sites command
  claude -p "/validate-sites $slug_list" \
    --verbose \
    2>&1 | tee -a "$LOG_FILE"

  local exit_code=${PIPESTATUS[0]}

  echo ""
  echo "Batch $batch_num completed at $(date) with exit code $exit_code"

  # Auto-commit if there are changes
  if [[ -n $(git status --porcelain) ]]; then
    git add data/osm_clean/ divesites/
    git commit -m "Validate batch $batch_num: $slug_list

Automated validation via validate_batch.sh"
    echo "Changes committed."
  fi

  return $exit_code
}

# Main dispatch
case "${1:-}" in
  status)
    show_status
    ;;
  next)
    current=$(get_current_batch)
    total=$(get_total_batches)
    if [[ "$current" -gt "$total" ]]; then
      echo "All batches complete!"
      show_status
      exit 0
    fi
    echo "Running batch $current of $total..."
    run_batch "$current"
    set_current_batch $((current + 1))
    ;;
  all)
    total=$(get_total_batches)
    for i in $(seq 1 "$total"); do
      run_batch "$i"
    done
    ;;
  [1-9])
    run_batch "$1"
    ;;
  *)
    echo "Usage: $0 <batch_number|next|all|status>"
    echo ""
    echo "  $0 1        Run batch 1"
    echo "  $0 next     Run the next unprocessed batch"
    echo "  $0 all      Run all batches sequentially"
    echo "  $0 status   Show validation progress"
    echo ""
    echo "Schedule overnight:"
    echo "  crontab -e"
    echo "  1 0 * * * cd $REPO_DIR && ./scripts/validate_batch.sh next >> logs/validate.log 2>&1"
    exit 1
    ;;
esac
