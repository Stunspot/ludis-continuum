# Support, recovery, update, and removal

Use [GitHub Issues](https://github.com/Stunspot/ludis-continuum/issues) for reproducible public defects. Do not attach private campaign ledgers, player identities, consent notes, licensed source text, or unreleased story secrets. For a vulnerability or sensitive exposure, follow [SECURITY.md](SECURITY.md).

## Before reporting a defect

Run from the installed skill directory:

```powershell
python -B scripts/self_check.py
```

Record:

- host and host version;
- operating system and Python version;
- installation scope and exact skill path;
- whether the skill is present, discoverable, invoked, or healthy;
- exact command and exit code;
- smallest redacted fixture that reproduces the problem;
- expected and observed behavior.

Do not report “installed” when only the directory exists. State the furthest observed stage: copied, package self-check passed, discovered by host, invoked, or behaviorally verified.

## Skill is not discoverable

1. Confirm the directory is named `ludis-continuum`.
2. Confirm `SKILL.md` is directly inside that directory, not nested under an archive folder.
3. Confirm the complete `knowledge/`, `fallbacks/`, `scripts/`, `assets/`, `schemas/`, and `agents/` directories are present.
4. Run `scripts/self_check.py`.
5. Restart the host.
6. Check the host's current skill-discovery documentation and policy.
7. If discovery still fails, use the copy/paste fallback and report host discovery as **not verified**.

## Self-check fails

Treat the first reported failure as primary. Common causes are a partial download, missing instrument file, altered frontmatter, line-ending damage, or package files copied into the wrong level. Compare against the current Git commit; do not “fix” hashes or manifests until you know why the bytes differ.

## Ledger validation fails

- `missing top-level field`: restore the field from the campaign template or a trusted snapshot.
- `duplicate id`: assign a new stable ID and update intended references.
- `broken link`: restore the referenced object or remove the link only after confirming the relationship is obsolete.
- `spoiler link`: a player-safe object points to GM-only state. Redesign the public reference; never expose the secret to satisfy validation.
- `active canon requires gm_approved authority`: return the object to proposed/disputed or obtain and record the GM decision.
- `session collision`: resolve the schedule explicitly; do not discard one session silently.

Make a snapshot or copy before editing damaged state, then rerun validation.

## Promotion fails

`promote_object.py` requires exactly one matching object, status `proposed` or `disputed`, explicit `--gm-approved`, and no unresolved contradiction with active canon. The tool does not grant approval; it records the human decision asserted by the operator.

## Player export fails or exposes too much

If validation fails, export is denied. If export succeeds but prose still reveals a secret, revoke `player_export_approved`, correct the content, validate again, and manually review the complete export. Structural validation cannot understand semantic spoilers.

## Snapshot and restore

Create a snapshot:

```powershell
python -B scripts/snapshot_campaign.py C:\Games\MyCampaign
```

Copy the ZIP and printed SHA-256 to independent storage. To test recovery, extract into a new empty directory, compare the archive hash, inspect `snapshot-manifest.json`, and run `validate_ledger.py` on the restored ledger before replacing any live workspace.

A created archive is not a verified backup until restore has been exercised.

## Update

Git install:

```powershell
git -C "$env:USERPROFILE\.codex\skills\ludis-continuum" status --short
git -C "$env:USERPROFILE\.codex\skills\ludis-continuum" pull --ff-only
python -B "$env:USERPROFILE\.codex\skills\ludis-continuum\scripts\self_check.py"
```

Use the corresponding `.claude\skills` path for Claude Code. If the status command shows local changes, preserve or commit them before updating; do not overwrite them. Restart the host and repeat discovery/invocation verification.

Archive installs must be replaced with a fresh archive. Preserve local modifications separately and never store campaign data inside the skill directory.

## Remove the skill

First locate the exact skill directory and verify that it contains this repository. Prefer moving it to a dated backup location over immediate deletion.

Windows example:

```powershell
Move-Item -LiteralPath "$env:USERPROFILE\.codex\skills\ludis-continuum" -Destination "$env:USERPROFILE\Desktop\ludis-continuum-removed"
```

Restart the host and confirm the skill is no longer discoverable. For Claude Code, use the `.claude\skills` path.

## Campaign data cleanup

Removing the skill does not remove campaign workspaces. Campaign data may include:

- `campaign-ledger.json`;
- player-safe exports;
- session notes and creative artifacts added by the user;
- `checkpoints/*.zip` archives;
- independent backups or synced copies.

Inventory those locations, decide retention with the campaign owner and participants, and remove copies according to their privacy and rights obligations. Ludis has no remote account, cloud database, telemetry store, or deletion API.

## Support boundary

Maintainers can investigate package and documentation defects. They cannot certify third-party host behavior, recover undisclosed campaign data, determine rights to source material, resolve table consent disputes, or guarantee that generated content is safe, balanced, original, or suitable.