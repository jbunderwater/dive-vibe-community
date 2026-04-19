#!/usr/bin/env python3
"""
Apply research findings from /tmp/roatan_research_findings.json to
data/osm_clean/roatan.json and the corresponding markdown stubs in
divesites/roatan/.

Findings JSON schema (produced by a research agent — see
scripts/import_rmp_kml.py for the import that created the stubs):

    {
      "sources_consulted": [{"url": "...", "name": "...", "sites_listed": N}],
      "matches": [
        {
          "name": "<exact name as in osm_clean>",
          "found_in": ["roatansplashinn.com", "scubaboard.com/threads/123"],
          "site_type": "wall",            # optional; only if source confirms
          "depth_m": 24,                  # optional
          "difficulty": "Intermediate",   # optional
          "entry_type": "boat",           # optional
          "description": "1-3 sentences grounded in cited sources."
        }
      ],
      "no_source_found": ["name1", "name2", ...]
    }

For matches: updates osm_clean fields the source supports, sets
validated=true, sets validation_source to the cited domains, and rewrites
the markdown Overview paragraph + footer source attribution.

For no_source_found entries: leaves osm_clean as-is (validated stays false)
and rewrites only the markdown footer to make the lack of sourcing explicit.

Usage:
    python3 scripts/apply_rmp_research.py [--findings PATH] [--dry-run]
"""

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
OSM_CLEAN_PATH = PROJECT_ROOT / "data" / "osm_clean" / "roatan.json"
DIVESITES_DIR = PROJECT_ROOT / "divesites" / "roatan"
DEFAULT_FINDINGS = Path("/tmp/roatan_research_findings.json")

VALID_SITE_TYPES = {"reef", "wall", "wreck", "cave", "muck", "beach", "drift", "pinnacle"}
VALID_DIFFICULTIES = {"Beginner", "Intermediate", "Advanced"}


def slugify(name: str) -> str:
    s = name.strip().lower()
    s = re.sub(r"[^\w\s-]", "", s, flags=re.UNICODE)
    s = re.sub(r"[\s_]+", "-", s)
    s = re.sub(r"-+", "-", s)
    return s.strip("-")


def update_overview_paragraph(md: str, new_paragraph: str) -> str:
    """Replace the paragraph immediately after the '## <Name>' heading."""
    lines = md.split("\n")
    out = []
    i = 0
    replaced = False
    while i < len(lines):
        out.append(lines[i])
        if (not replaced
                and lines[i].startswith("## ")
                and not lines[i].startswith("## Site Information")):
            # skip the next blank line, then replace the following paragraph
            i += 1
            if i < len(lines) and lines[i].strip() == "":
                out.append(lines[i])
                i += 1
            # consume original paragraph (until blank line)
            while i < len(lines) and lines[i].strip() != "":
                i += 1
            out.append(new_paragraph)
            replaced = True
            continue
        i += 1
    return "\n".join(out)


def replace_footer(md: str, new_footer: str) -> str:
    """Replace the trailing '*Source(s)…*' footer (or append if missing)."""
    pattern = re.compile(r"^---\s*\n\*[^*]+\*\s*$", re.MULTILINE)
    if pattern.search(md):
        return pattern.sub(new_footer.rstrip() + "\n", md.rstrip()) + "\n"
    return md.rstrip() + "\n\n---\n" + new_footer.rstrip() + "\n"


def domain_of(found_entry: str) -> str:
    """Reduce a 'roatansplashinn.com/page' or full URL to a domain."""
    s = re.sub(r"^https?://", "", found_entry)
    return s.split("/", 1)[0]


def apply_match(entry: dict, match: dict, today: str) -> tuple[bool, list[str]]:
    """Mutate osm_clean entry in place from a research match. Returns
    (changed, list of human-readable change descriptions)."""
    changes = []
    if (st := match.get("site_type")) and st in VALID_SITE_TYPES and st != entry.get("site_type"):
        changes.append(f"site_type {entry.get('site_type')!r} → {st!r}")
        entry["site_type"] = st
    if (d := match.get("depth_m")) and isinstance(d, (int, float)) and int(d) != entry.get("depth"):
        changes.append(f"depth {entry.get('depth')} → {int(d)}m")
        entry["depth"] = int(d)
    if (diff := match.get("difficulty")) and diff in VALID_DIFFICULTIES and diff != entry.get("difficulty"):
        changes.append(f"difficulty {entry.get('difficulty')!r} → {diff!r}")
        entry["difficulty"] = diff
    if (et := match.get("entry_type")) and et in {"shore", "boat", "both"} and et != entry.get("entry_type"):
        changes.append(f"entry_type {entry.get('entry_type')!r} → {et!r}")
        entry["entry_type"] = et

    sources = sorted({domain_of(f) for f in match.get("found_in", [])})
    tags = entry.setdefault("tags", {})
    tags["validated"] = True
    tags["validation_source"] = ",".join(sources) if sources else tags.get("validation_source", "")
    tags["validated_at"] = today
    return bool(changes), changes


def render_match_overview(name: str, description: str, site_type: str) -> str:
    desc = description.strip()
    if not desc:
        return ""
    if not desc.endswith("."):
        desc += "."
    return desc


def render_footer(found_in: list[str], today: str) -> str:
    parts = []
    for f in found_in:
        if f.startswith("http"):
            domain = domain_of(f)
            parts.append(f"[{domain}]({f})")
        else:
            parts.append(f"[{f}](https://{f})" if "." in f and "/" not in f else f)
    if not parts:
        return f"*Description based on regional diving characteristics. No site-specific sources found. Last updated {today}.*"
    return f"*Sources: {', '.join(parts)}. Last updated {today}.*"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--findings", type=Path, default=DEFAULT_FINDINGS)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not args.findings.exists():
        print(f"findings file not found: {args.findings}", file=sys.stderr)
        return 1

    findings = json.loads(args.findings.read_text())
    matches = findings.get("matches", [])
    no_source = findings.get("no_source_found", [])
    print(f"Loaded findings: {len(matches)} matches, {len(no_source)} no-source.")

    osm = json.loads(OSM_CLEAN_PATH.read_text())
    by_name = {s["name"]: s for s in osm}
    today = date.today().isoformat()

    updated_json = 0
    rewrote_md = 0
    footer_only = 0
    missing_in_osm = []

    for match in matches:
        name = match["name"]
        entry = by_name.get(name)
        if entry is None:
            missing_in_osm.append(name)
            continue
        changed, changes = apply_match(entry, match, today)
        if changed:
            updated_json += 1
            print(f"  json: {name}: {'; '.join(changes)}")

        md_path = DIVESITES_DIR / f"{slugify(name)}.md"
        if not md_path.exists():
            continue
        md = md_path.read_text()
        if (desc := render_match_overview(name, match.get("description", ""), entry["site_type"])):
            md = update_overview_paragraph(md, desc)
            rewrote_md += 1
        md = replace_footer(md, render_footer(match.get("found_in", []), today))
        if not args.dry_run:
            md_path.write_text(md)

    for name in no_source:
        md_path = DIVESITES_DIR / f"{slugify(name)}.md"
        if not md_path.exists():
            continue
        md = md_path.read_text()
        md = replace_footer(md, render_footer([], today))
        if not args.dry_run:
            md_path.write_text(md)
        footer_only += 1

    if not args.dry_run:
        OSM_CLEAN_PATH.write_text(
            json.dumps(osm, indent=2, ensure_ascii=False) + "\n"
        )

    print(f"\n=== Apply summary ===")
    print(f"  osm_clean entries updated:   {updated_json}")
    print(f"  markdown overviews rewritten: {rewrote_md}")
    print(f"  markdown footers only updated: {footer_only}")
    if missing_in_osm:
        print(f"  matches not found in osm_clean ({len(missing_in_osm)}):")
        for n in missing_in_osm[:10]:
            print(f"    - {n}")
    if args.dry_run:
        print("(dry-run — no files written)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
