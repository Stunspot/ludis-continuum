# Provenance, validation, and evidence status

This file separates what Ludis Continuum contains from what has actually been exercised. Presence is not behavior; a passing local check is not a fresh-host or live-table result.

## Provenance

This standalone repository preserves the curated Ludis Continuum skill from the public Nova + MIND OpenAI Build Week contest release. The repository is a fresh standalone history. Private development history, private campaign material, and worked campaign worlds are intentionally excluded.

- Product edition: `1.0.0`
- Campaign-ledger format accepted by the current executable validator: `0.1.0`
- License: MIT
- Runtime dependencies for bundled tools: Python standard library
- Creative corpus: 32 compact instrument cores listed in `knowledge/instruments/manifest.json`

The manifest describes the instrument corpus as semantically rewritten derivative material with legacy source retained only for provenance. It does not by itself prove originality or rights clearance; publication review remains human work.

## Evidence ladder

| Claim | Current status | Evidence boundary |
|---|---|---|
| Standalone package constructed | Verified | Required source, doctrine, fallbacks, instruments, schemas, assets, scripts, and host metadata are present at the reviewed commit. |
| Curated package self-check | Verified | `python -B scripts/self_check.py` returned PASS for 32 instrument cores. |
| Campaign initialization | Verified | An isolated probe created the template workspace at a previously absent destination, then the resulting ledger validated. |
| Ledger structural guard | Verified | Valid template passed; a player-safe link to a GM-only object failed with the expected spoiler-link error. |
| Promotion authority guard | Verified | Promotion without `--gm-approved` failed; a valid proposed object with the flag promoted and recorded approval. |
| Player-safe export filtering | Verified | Export included exactly the approved player-safe object and excluded GM-only content in the synthetic fixture. |
| Seeded selection reproducibility | Verified | Identical seed, table, and count produced byte-identical JSON results in consecutive runs. |
| Snapshot behavior | Verified | Consecutive snapshots produced manifests and excluded previous checkpoint ZIPs. |
| Fresh-host installation | Not independently verified | Instructions are published; no fresh machine receipt is inferred from this checkout. |
| Codex discovery and invocation of this standalone checkout | Not independently verified | Installed contest-bundle source exists on the review host, but that does not validate this repository's manual-copy path on a fresh host. |
| Claude Code discovery and invocation | Not independently verified | Package shape and instructions exist; no fresh-host receipt is claimed. |
| Live table fun, safety, balance, accessibility, or usability | Not independently verified | These require representative human play and table-specific review. |
| Rules accuracy or VTT compatibility | Not claimed | No authoritative game rules or VTT integration are bundled. |

## Synthetic functional probe

The review probe used a temporary campaign with one GM-only proposed secret and one approved player-safe rumor. It deliberately introduced a player-safe link to the secret, observed validator rejection, removed the link, validated again, tested guarded canon promotion, exported the player view, reproduced a seeded roll, and created two snapshots.

Synthetic fixtures establish deterministic behavior for the exercised paths. They do not establish real-campaign semantic safety.

## Documentation review custody

The final publication candidate receives three separate reviews:

1. Hesperos customer-documentation authorship and journey review;
2. accessibility review of language, structure, links, contrast, focus, motion, and image alternatives;
3. adversarial TestForge verification of claims, tools, links, assets, package boundaries, and live deployment.

Receipts are stored under [`verification/`](verification/) and bind to the exact reviewed commit or a content fingerprint. Any later content change invalidates the prior receipt and requires re-review.

## Interpreting PASS

A repository PASS means the final commit, live repository, rendered Pages deployment, navigation, public assets, and bound review evidence were rechecked. It does not widen the product's claims beyond the evidence table above.