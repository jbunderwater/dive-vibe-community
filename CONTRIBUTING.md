# Contributing to Dive Vibe Community Data

Thank you for your interest in contributing! We welcome contributions from divers, travelers, and anyone who wants to improve this dive site database.

## How we accept contributions

**All changes go through GitHub:** fork this repository, push your work to a branch on your fork, and open a **pull request (PR)** against `main` here so changes are reviewable, attributable, and licensed consistently.

### Workflow

1. **Fork** this repository on GitHub (your own copy under your account).
2. **Clone your fork** and add this repo as `upstream` if you want to stay in sync:
   - `git clone https://github.com/<your-username>/dive-vibe-community.git`
   - `git remote add upstream https://github.com/jbunderwater/dive-vibe-community.git`
3. **Create a branch** for your change: `git checkout -b short-description-of-change`
4. **Make your edits** following [Data quality standards](#data-quality-standards) and the structure in `README.md` / `CLAUDE.md`.
5. **Commit** with clear messages.
6. **Push** to your fork: `git push origin short-description-of-change`
7. **Open a pull request** from your branch into `main` on the upstream repository. Describe what you changed and why.

Maintainers will review your PR; we may request changes before merging.

### Optional tooling

Some maintainers use [Claude Code](https://docs.anthropic.com/en/docs/claude-code) with the slash commands in `.claude/commands/` (e.g. `/validate-sites`). That is optional—you can contribute with any editor and the Python scripts documented in `README.md`.

## What you can contribute

- **Site data**: corrections and additions in `data/osm_clean/{slug}.json`, then run `python3 scripts/sync_sites.py <slug>` so markdown and `index.json` stay in sync (see `README.md`).
- **New destinations**: follow the pipeline in `README.md` / `CLAUDE.md` (`destinations.json`, scrapers, cleaning, gap-fill as needed).
- **Descriptions & validation**: improve site text and metadata where you can cite reliable sources.
- **Scripts & docs**: fixes and improvements to tooling or documentation.
- **Issues**: open an issue for bugs, data problems, or discussion before large changes.

## Data quality standards

Contributions must follow the rules in `CLAUDE.md` (also summarized in `README.md`), including:

- Dive **sites** only—no commercial dive shops, schools, or operators framed as “sites.”
- No contact info (websites, phones, social URLs) in data meant for redistribution.
- Accurate **site types** (not defaulting everything to “reef” without justification).
- Valid coordinates within each destination’s bounds, no duplicate site names per destination, and sensible difficulty/depth where stated.

## Data format (quick reference)

- **JSON source of truth for bulk edits**: `data/osm_clean/{slug}.json`
- **Generated pages**: `divesites/{slug}/*.md` and `divesites/{slug}/index.json` — regenerate with `sync_sites.py` after JSON changes unless you’re editing in a coordinated way described in the docs.
- **Destination list**: `destinations.json`

For frontmatter fields and conventions, see existing files under `divesites/` and `_template.md`.

## Code of conduct

Be respectful and constructive. We want a welcoming, inclusive community around the data.

## Review process

- Every PR is reviewed by maintainers.
- We may ask for changes or more detail before merging.
- Once merged, your contribution is part of the repo history and subject to the same licenses (`LICENSE` for code, `LICENSE-DATA.md` / ODbL for OSM-derived data—see `README.md` and `ATTRIBUTION.md`).

## Questions?

- Open an **issue** on this repository for bugs, data problems, or proposals.
- Use **GitHub Discussions** if enabled on the repo for broader questions.

Thank you for helping improve this resource for divers.
