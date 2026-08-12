# Ludis Continuum Pages source

This directory is the source for <https://stunspot.github.io/ludis-continuum/>.

## Customer journey

- `index.html` — product identity, modes, campaign loop, ledger, instruments, and trust edge.
- `start.html` — Codex, Claude Code, project-scoped, archive, and fallback installation; package/discovery/invocation verification; first run.
- `guide.html` — inputs, outputs, representative workflows, campaign state, tool behavior, and limitations.
- `trust.html` — privacy, storage, security, evidence, recovery, update, removal, cleanup, accessibility, support, and license routes.
- `404.html` — useful recovery navigation for unknown paths.

## Role-specific visuals

- `assets/ludis-continuum-readme-hero.png` — wide, text-free repository introduction; used only by the root README.
- `assets/ludis-continuum-pages-hero.png` — taller, text-free interactive-campaign composition; used as the Pages home hero.
- `assets/ludis-continuum-social-card.png` — 1200×630 share card with the exact product title and identifying line; used by Open Graph and Twitter metadata.

The assets are different compositions and aspect ratios, not crops. Their actual pixels must be reviewed after any change.

## Deployment

GitHub Actions publishes `docs/` from `main`. A successful workflow run establishes deployment execution only. Publication PASS also requires live route, content, navigation, metadata, asset, and custom-404 verification against the final commit.