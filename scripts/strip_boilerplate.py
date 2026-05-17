#!/usr/bin/env python3
"""
Strip auto-generated boilerplate sections from dive site markdown files.

generate_sites.py produces fixed-template sections for Marine Life, Dive Profile,
Entry and Exit, Tips and Recommendations, Safety Considerations, and Photography.
The Marine Life template uses a regional species list keyed by `dest.region`, but
the "North America" key uses Pacific Northwest species — which is wrong for
tropical (Florida, Dry Tortugas, Flower Garden Banks), cold-Atlantic (NJ, NC,
Newfoundland), and freshwater (Great Lakes) destinations under that region.
The Photography, Dive Profile, and Safety templates make site-specific
authoritative claims that no source supports.

This script detects each boilerplate section by matching the exact template
phrases from generate_sites.py and removes the section. Hand-curated content
that doesn't match the templates is left untouched.

Run with --dry-run to preview, --verbose to see per-file changes.
"""

import argparse
import re
import sys
from pathlib import Path


# Exact phrases from scripts/generate_sites.py templates. Each is a reliable
# fingerprint for an auto-generated section. Detection is conservative:
# if the section contains the phrase, the section is treated as boilerplate.

MARINE_LIFE_FINGERPRINT = "Divers at this site can expect to encounter"

DIVE_PROFILE_FINGERPRINTS = (
    "Begin your dive in the shallower sections and gradually work deeper",
    "The dive typically begins with a descent to the top of the wreck structure",
    "Begin along the reef top at shallower depths before descending along the wall",
)

ENTRY_EXIT_FINGERPRINTS = (
    "Enter from the shore following established entry points",
    "Access is by dive boat from local operators. Entry is typically via giant stride or back roll",
    "This site can be accessed from shore or by boat. Shore entry follows established paths",
)

TIPS_FINGERPRINT = "Bring an underwater camera — this site offers excellent photography opportunities"

SAFETY_FINGERPRINTS = (
    "Dive within your certification limits and experience level.",
    "Always dive with a buddy and carry a safety sausage (SMB)",
)

PHOTOGRAPHY_FINGERPRINTS = (
    "This site offers excellent opportunities for both wide-angle and macro photography",
    "The wreck structure provides dramatic wide-angle subjects with natural light filtering through openings",
    "Wall dives offer stunning wide-angle opportunities with dramatic depth perspectives",
)

# Overview tail appended by the generator
OVERVIEW_TAIL_RE = re.compile(
    r"\s*Located in the [^.]+ region, this site offers [^.]+of visibility "
    r"with water temperatures averaging [^.]+\.\s*$"
)

# Site Information bullets that come from regional defaults (not site-specific)
REGIONAL_DEFAULT_BULLETS = (
    "**Typical Visibility**",
    "**Current**",
    "**Best Time**",
)

# The generator's exact footer (no markdown links). Hand-curated source footers
# use bracketed [Name](URL) links and are preserved.
GENERATOR_FOOTER_RE = re.compile(
    r"\*This dive site information was compiled from OpenStreetMap data "
    r"and regional diving knowledge\. Last updated \d{4}-\d{2}-\d{2}\.\*"
)


def split_frontmatter(text):
    """Return (frontmatter_block_with_fences, body) or (None, text) if no frontmatter."""
    if not text.startswith("---\n"):
        return None, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return None, text
    return text[: end + 5], text[end + 5 :]


def split_footer(body):
    """Split a trailing footer (e.g. '---\\n*Sources: ...*') off the body.

    Returns (body_without_footer, footer_text). If no footer is found,
    footer_text is "".
    """
    # Find the LAST occurrence of a '---' separator line, where everything
    # after it is just a single italic-line footer (no other ## headings).
    lines = body.splitlines(keepends=True)
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip() == "---":
            tail = "".join(lines[i + 1 :])
            # Footer should be one italic block, no more ## headings
            if "## " in tail:
                break
            stripped = tail.strip()
            if stripped.startswith("*") and stripped.endswith("*"):
                return "".join(lines[:i]), "".join(lines[i:])
            break
    return body, ""


def split_sections(body):
    """Split body into [(heading_line_or_None, content), ...].

    The first chunk (before any ## heading) has heading=None.
    """
    lines = body.splitlines(keepends=True)
    sections = []
    current_heading = None
    current_lines = []
    for line in lines:
        if line.startswith("## "):
            sections.append((current_heading, "".join(current_lines)))
            current_heading = line
            current_lines = []
        else:
            current_lines.append(line)
    sections.append((current_heading, "".join(current_lines)))
    return sections


def is_boilerplate(heading_line, content):
    """Return True if this section matches a generator template."""
    if heading_line is None:
        return False
    heading = heading_line.strip().lstrip("#").strip().lower()

    if heading == "marine life":
        return MARINE_LIFE_FINGERPRINT in content
    if heading == "dive profile":
        return any(fp in content for fp in DIVE_PROFILE_FINGERPRINTS)
    if heading == "entry and exit":
        return any(fp in content for fp in ENTRY_EXIT_FINGERPRINTS)
    if heading == "tips and recommendations":
        return TIPS_FINGERPRINT in content
    if heading == "safety considerations":
        return all(fp in content for fp in SAFETY_FINGERPRINTS)
    if heading == "photography":
        return any(fp in content for fp in PHOTOGRAPHY_FINGERPRINTS)
    return False


def clean_site_information(content):
    """Remove regional-default bullets ('Typical Visibility', 'Current', 'Best Time')."""
    new_lines = []
    changed = False
    for line in content.splitlines(keepends=True):
        stripped = line.lstrip()
        if stripped.startswith("- ") and any(b in stripped for b in REGIONAL_DEFAULT_BULLETS):
            changed = True
            continue
        new_lines.append(line)
    return "".join(new_lines), changed


OVERVIEW_BOILERPLATE_BODY_RE = re.compile(
    r"^.*\b("
    r"offering excellent diving on healthy coral reef structures"
    r"|offering rewarding diving on healthy coral reef structures"
    r"|featuring the wreck of the [^.]+"
    r"|featuring a historic wreck"
    r"|featuring a dramatic vertical wall that drops into the deep blue"
    r"|featuring underwater cave and cavern formations"
    r")\b.*$",
    re.MULTILINE | re.IGNORECASE,
)


def clean_overview(content):
    """Strip auto-generated overview content.

    Removes both the regional 'Located in the X region...' tail and the
    short boilerplate overview body sentence(s) produced by
    generate_sites.py (e.g. 'X is a dive site in Y offering rewarding
    diving on healthy coral reef structures.'). When the body is fully
    boilerplate, replace it with an explicit placeholder.
    """
    changed = False
    new_content = content

    # Strip the auto-generated tail (with leading whitespace or newlines)
    less_strict = re.compile(
        r"\s+Located in the [^.]+ region, this site offers [^.]+of visibility "
        r"with water temperatures averaging [^.]+\."
    )
    new_content, n = less_strict.subn("", new_content)
    if n > 0:
        changed = True

    # Detect boilerplate body sentences
    matches = OVERVIEW_BOILERPLATE_BODY_RE.findall(new_content)
    if matches:
        # Remove the entire matching line(s), then collapse extra blanks
        new_content = OVERVIEW_BOILERPLATE_BODY_RE.sub("", new_content)
        new_content = re.sub(r"\n{3,}", "\n\n", new_content)
        # If the overview is now effectively empty, insert a placeholder
        if not new_content.strip():
            new_content = (
                "\nNo site-specific dive sources have been validated for this entry yet — "
                "marine life, typical dive profile, currents, visibility, and photography "
                "conditions are not documented.\n\n"
            )
        changed = True

    if not changed:
        return content, False

    # Restore trailing newline if original had one
    if content.endswith("\n") and not new_content.endswith("\n"):
        new_content += "\n"
    return new_content, True


def replace_generator_footer(footer):
    """Replace the auto-generated footer with a 'no site-specific sources' disclaimer.

    Operates on the trailing footer block (including the leading '---' separator).
    """
    if not footer:
        return footer, False
    match = GENERATOR_FOOTER_RE.search(footer)
    if not match:
        return footer, False
    date = match.group(0).split("Last updated ")[1].rstrip(".*")
    replacement = (
        "*Description based on OpenStreetMap-recorded data. "
        f"No site-specific dive sources were located. Last updated {date}.*"
    )
    return footer[: match.start()] + replacement + footer[match.end() :], True


def process_file(path: Path, dry_run: bool):
    text = path.read_text(encoding="utf-8")
    fm, body = split_frontmatter(text)
    if fm is None:
        return None  # not a site markdown

    body_no_footer, footer = split_footer(body)
    sections = split_sections(body_no_footer)

    # First pass: detect boilerplate sections (don't mutate yet)
    boilerplate_headings = set()
    for heading_line, content in sections:
        if heading_line is None:
            continue
        if is_boilerplate(heading_line, content):
            boilerplate_headings.add(heading_line.strip().lstrip("#").strip().lower())
            continue
        # An auto-generated Overview body is also a boilerplate signal
        if (
            heading_line.strip().lstrip("#").strip().lower() == "overview"
            and OVERVIEW_BOILERPLATE_BODY_RE.search(content)
        ):
            boilerplate_headings.add("overview")

    # Only trim regional-default Site Info bullets and the auto-generated
    # overview tail if the file is otherwise still boilerplate. Hand-curated
    # files (no boilerplate sections detected) keep their tuned values.
    file_is_boilerplate = len(boilerplate_headings) > 0

    new_sections = []
    removed = []
    site_info_changed = False
    overview_changed = False

    for heading_line, content in sections:
        if heading_line is None:
            new_sections.append((heading_line, content))
            continue

        heading_text = heading_line.strip().lstrip("#").strip()

        if is_boilerplate(heading_line, content):
            removed.append(heading_text)
            continue

        if file_is_boilerplate and heading_text.lower() == "site information":
            cleaned, changed = clean_site_information(content)
            if changed:
                site_info_changed = True
                content = cleaned

        if file_is_boilerplate and heading_text.lower() == "overview":
            cleaned, changed = clean_overview(content)
            if changed:
                overview_changed = True
                content = cleaned

        new_sections.append((heading_line, content))

    # Rebuild body
    new_body_parts = []
    for heading_line, content in new_sections:
        if heading_line is not None:
            new_body_parts.append(heading_line)
        new_body_parts.append(content)
    new_body = "".join(new_body_parts)

    # Replace generator footer if present (and re-attach)
    new_footer, footer_replaced = replace_generator_footer(footer)
    new_body = new_body.rstrip("\n") + ("\n\n" + new_footer if new_footer else "")
    if not new_body.endswith("\n"):
        new_body += "\n"

    # Collapse 3+ consecutive blank lines
    new_body = re.sub(r"\n{3,}", "\n\n", new_body)

    new_text = fm + new_body

    if new_text == text:
        return None

    if not dry_run:
        path.write_text(new_text, encoding="utf-8")

    return {
        "removed_sections": removed,
        "site_info_changed": site_info_changed,
        "overview_changed": overview_changed,
        "footer_replaced": footer_replaced,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Report only; don't modify files")
    parser.add_argument("--verbose", action="store_true", help="Show per-file changes")
    parser.add_argument(
        "--root", default="divesites", help="Root directory to scan (default: divesites)"
    )
    parser.add_argument(
        "--destination",
        help="Limit to a single destination slug (e.g., 'south-florida')",
    )
    args = parser.parse_args()

    root = Path(args.root)
    if not root.exists():
        print(f"ERROR: {root} does not exist", file=sys.stderr)
        return 2

    paths = []
    if args.destination:
        dest_dir = root / args.destination
        if not dest_dir.exists():
            print(f"ERROR: {dest_dir} does not exist", file=sys.stderr)
            return 2
        paths = sorted(p for p in dest_dir.glob("*.md") if p.name not in ("overview.md",))
    else:
        for dest_dir in sorted(root.iterdir()):
            if not dest_dir.is_dir():
                continue
            paths.extend(sorted(p for p in dest_dir.glob("*.md") if p.name not in ("overview.md",)))

    total = 0
    changed = 0
    section_counts = {}
    site_info_changes = 0
    overview_changes = 0
    footer_changes = 0

    for path in paths:
        total += 1
        result = process_file(path, args.dry_run)
        if result is None:
            continue
        changed += 1
        for sec in result["removed_sections"]:
            section_counts[sec] = section_counts.get(sec, 0) + 1
        if result["site_info_changed"]:
            site_info_changes += 1
        if result["overview_changed"]:
            overview_changes += 1
        if result["footer_replaced"]:
            footer_changes += 1
        if args.verbose:
            rel = path.relative_to(root)
            bits = []
            if result["removed_sections"]:
                bits.append("removed: " + ", ".join(result["removed_sections"]))
            if result["site_info_changed"]:
                bits.append("site-info-trimmed")
            if result["overview_changed"]:
                bits.append("overview-tail-stripped")
            if result["footer_replaced"]:
                bits.append("footer-replaced")
            print(f"  {rel}: {'; '.join(bits)}")

    print()
    print("=" * 60)
    print(f"Scanned:           {total} files")
    print(f"Modified:          {changed} files{' (dry-run, not written)' if args.dry_run else ''}")
    print(f"Site Info trimmed: {site_info_changes}")
    print(f"Overview tails:    {overview_changes}")
    print(f"Footers replaced:  {footer_changes}")
    if section_counts:
        print("Sections removed:")
        for sec, count in sorted(section_counts.items(), key=lambda x: -x[1]):
            print(f"  {sec:30s} {count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
