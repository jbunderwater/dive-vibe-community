#!/usr/bin/env python3
"""Move the prepared Elba destination from staging/elba into the live repo layout.

Run from the repository root AFTER the data has been approved:

    python3 staging/elba/apply.py            # add Elba, keep staging/ folder
    python3 staging/elba/apply.py --cleanup  # add Elba and delete staging/elba

What it does:
  1. inserts destinations-entry.json into destinations.json (after czech-republic)
  2. copies data/osm_clean/elba.json and divesites/elba/ into place
  3. runs scripts/sync_sites.py elba
Refuses to run if an "elba" destination or its files already exist.
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

STAGING = Path(__file__).resolve().parent
ROOT = STAGING.parent.parent
SLUG = "elba"


def main():
    dest_path = ROOT / "destinations.json"
    destinations = json.loads(dest_path.read_text(encoding="utf-8"))
    if any(d["slug"] == SLUG for d in destinations):
        sys.exit(f"'{SLUG}' already exists in destinations.json — nothing done.")
    osm_target = ROOT / "data" / "osm_clean" / f"{SLUG}.json"
    md_target = ROOT / "divesites" / SLUG
    if osm_target.exists() or md_target.exists():
        sys.exit(f"{osm_target} or {md_target} already exists — nothing done.")

    entry = json.loads((STAGING / "destinations-entry.json").read_text(encoding="utf-8"))
    slugs = [d["slug"] for d in destinations]
    pos = slugs.index("czech-republic") + 1 if "czech-republic" in slugs else len(destinations)
    destinations.insert(pos, entry)
    dest_path.write_text(json.dumps(destinations, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    shutil.copy2(STAGING / "data" / "osm_clean" / f"{SLUG}.json", osm_target)
    shutil.copytree(STAGING / "divesites" / SLUG, md_target)

    subprocess.run([sys.executable, str(ROOT / "scripts" / "sync_sites.py"), SLUG], check=True, cwd=ROOT)

    if "--cleanup" in sys.argv:
        shutil.rmtree(STAGING)
        staging_root = STAGING.parent
        if staging_root.exists() and not any(staging_root.iterdir()):
            staging_root.rmdir()
    print(f"Added '{SLUG}' with {len(json.loads(osm_target.read_text(encoding='utf-8')))} sites.")


if __name__ == "__main__":
    main()
